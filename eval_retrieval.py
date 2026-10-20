"""检索评测:对 eval_queries.json 计算两级指标。

两级指标的差别是关键 —— 本项目的缺陷恰恰是"文件找对了,片段里没有答案":

    recall@k    文档级:期望文件是否出现在 top-k 结果里
    snippet@k   答案级:返回的 **片段** 是否真的包含答案字面值(must_contain)

用法:
    python eval_retrieval.py                        # mixed + rerank, k=5
    python eval_retrieval.py --mode fts --no-rerank # 仅 FTS,不调 embedding API
    python eval_retrieval.py --json before.json     # 导出机器可读结果,便于改动前后对比
"""
import argparse
import json
import re
from pathlib import Path

import lancedb

from backend import config
from backend.retrieval import search

ROOT = Path(__file__).resolve().parent


def load_queries() -> list[dict]:
    p = ROOT / "eval_queries.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _basename(path: str) -> str:
    """取文件名,同时认 / 和 \\ 两种分隔符。

    历史数据里 expect 存的是 Windows 反斜杠路径(早期索引在 Windows 上构建),
    而 os.path.basename 在 Linux 上不把 \\ 当分隔符 —— 取出来的仍是整串
    "06_天线\\xxx.PDF",永远匹配不上,43/55 条查询被误判为失败(实测 recall
    被低估成 22%,真实值 100%)。
    """
    return re.split(r"[\\/]", path)[-1].lower()


def _hit(files: list[str], expect: str) -> bool:
    """按文件名匹配,而不是完整相对路径。

    类别目录会被重组(实测 TPS55289 手册从 04_电源管理 移到 17_升降压DC-DC),
    用完整路径断言会把"检索其实找对了"误判成失败。文档身份是文件名。
    """
    exp = _basename(expect)
    return any(exp in _basename(f) for f in files)


def _norm_sep(s: str) -> str:
    """归一化分隔符:PDF 提取时下标常丢失,同一写法在库里有歧义
    ("500 Ω" / "500Ω" / "500\\nΩ",以及 "VDD_APC" / "VDD APC")。"""
    return re.sub(r"[\s_]+", "", s)


def _snippet_ok(snippet: str, must: list[str]) -> list[str]:
    """返回片段中**缺失**的答案字面值;空列表表示全部命中。分隔符宽容。"""
    return [m for m in must if m not in snippet and _norm_sep(m) not in _norm_sep(snippet)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--mode", default="mixed", choices=["mixed", "fts", "vector"])
    ap.add_argument("--no-rerank", action="store_true")
    ap.add_argument("--legacy-snippet", action="store_true",
                    help="消融对照:片段退回旧行为(代表块的前 400 字符)")
    ap.add_argument("--json", default="", help="把结果写入该 JSON 文件")
    args = ap.parse_args()

    # 评测必须关掉结果缓存:否则消融对照(如 --legacy-snippet)会命中上一次
    # 正常运行的缓存,返回与当前设置不符的结果。
    # 用 override_local 而非 set_many —— 后者会持久化,跑完评测就把用户的
    # 查询缓存永久关掉了。
    config.override_local({"query_cache_ttl": 0})

    if args.legacy_snippet:
        # 消融实验:复现改动前的片段行为,用来量化"片段窗口化"的贡献
        import backend.retrieval as _r
        _r.page_snippet = lambda chunks, query, width=0: (chunks[0]["text"][:400] if chunks else "")
        print("[消融] 片段已退回 text[:400]\n")

    db = lancedb.connect(config.DB_PATH)
    table = db.open_table("chunks")
    queries = load_queries()

    tot_recall = 0.0
    tot_s1 = 0
    tot_sk = 0
    n_degraded = 0
    degraded_paths: dict[str, int] = {}
    records = []

    for q in queries:
        diag: dict = {}
        hits = search(table, q["query"], top_k=args.k,
                      mode=args.mode, rerank=not args.no_rerank, diagnostics=diag)
        # 降级(嵌入/重排接口不可用)会显著影响排序质量,必须计入并上报 ——
        # 否则一次限流就能让分数无声下滑,把环境问题误读成代码退化。
        deg = diag.get("degraded") or []
        if deg:
            n_degraded += 1
            for d in deg:
                degraded_paths[d] = degraded_paths.get(d, 0) + 1
        got = [h["file"] for h in hits]
        # expect 列的是**等价文档**(同一颗料的多份手册都算对),彼此是"或"关系:
        # 命中任意一份即为满分。按"找到几份"计分会让 2 份手册的查询永远到不了 100%,
        # 从而把"命中了正确答案"误报成 50% 失败。
        recall = 1.0 if any(_hit(got, e) for e in q["expect"]) else 0.0
        tot_recall += recall

        must = q.get("must_contain", [])
        if must and hits:
            miss1 = _snippet_ok(hits[0]["snippet"], must)
            missk = min((_snippet_ok(h["snippet"], must) for h in hits), key=len)
        else:
            miss1, missk = list(must), list(must)
        s1 = bool(must) and not miss1
        sk = bool(must) and not missk
        tot_s1 += s1
        tot_sk += sk

        records.append({
            "query": q["query"], "source": q.get("source", "?"), "recall": recall,
            "snippet_at_1": s1, "snippet_at_k": sk, "degraded": deg,
            "missing_in_top1": miss1, "top1_file": hits[0]["file"] if hits else None,
            "top1_page": hits[0]["page"] if hits else None,
        })

        flag = "✓" if s1 else ("~" if sk else "✗")
        print(f"[recall {recall:.0%}] [{flag} 片段] {q['query']!r}")
        for h in hits[:args.k]:
            snippet_miss = _snippet_ok(h["snippet"], must) if must else []
            mark = "✓" if not snippet_miss else " "
            fname = re.split(r"[\\/]", h["file"])[-1]
            print(f"   {mark} {fname[:52]} (p{h['page']}, {h['model_no'] or '-'})")
        if must and miss1:
            print(f"      ↑ top-1 片段缺失: {miss1}")

    n = len(queries)
    by_src: dict[str, list] = {}
    for r in records:
        by_src.setdefault(r["source"], []).append(r)
    print(f"\n{'='*66}")
    print(f"文档级 recall@{args.k} ({args.mode})      : {tot_recall / n:.0%}")
    print(f"答案级 snippet@{args.k} (任一命中)        : {tot_sk / n:.0%}  ({tot_sk}/{n})")
    print(f"答案级 snippet@1  (top-1 即含答案)        : {tot_s1 / n:.0%}  ({tot_s1}/{n})")
    if len(by_src) > 1:
        print(f"{'-'*66}")
        print(f"{'来源':<8} {'条数':>4} {'recall':>8} {'snippet@k':>10} {'snippet@1':>10}")
        for src, rs in sorted(by_src.items()):
            m = len(rs)
            print(f"{src:<8} {m:>4} {sum(x['recall'] for x in rs)/m:>8.0%} "
                  f"{sum(x['snippet_at_k'] for x in rs)/m:>10.0%} "
                  f"{sum(x['snippet_at_1'] for x in rs)/m:>10.0%}")
    if n_degraded:
        print(f"{'-'*66}")
        print(f"⚠ 降级 {n_degraded}/{n} 条查询({degraded_paths})")
        print("  接口不可用会拉低排序质量,该次结果不代表代码真实水平")
    print(f"{'='*66}")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "k": args.k, "mode": args.mode, "rerank": not args.no_rerank,
            "legacy_snippet": args.legacy_snippet,
            "recall": tot_recall / n, "snippet_at_k": tot_sk / n, "snippet_at_1": tot_s1 / n,
            "degraded_queries": n_degraded, "degraded_paths": degraded_paths,
            "records": records,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"结果已写入 {args.json}")


if __name__ == "__main__":
    main()
