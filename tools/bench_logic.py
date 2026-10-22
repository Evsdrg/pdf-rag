# -*- coding: utf-8 -*-
"""纯逻辑性能测试:不访问任何模型服务。

做法:把两处**唯一**的外部模型调用换成确定性本地替身,其余代码路径一行不改 ——
检索流程、LanceDB 查询、RRF 融合、去重、片段窗口都走真实实现。

    embed_query   -> 返回分区里已存的某条真实向量(768 维)
    _call_reranker-> 用查询词在文档中的命中数做确定性评分

这样测出的是"本系统地带的计算成本",可复现、零网络、零 API 额度。
想测含模型端的端到端延迟,用 eval_retrieval.py(那个必须联网)。

用法:
    python tools/bench_logic.py              # 全部
    python tools/bench_logic.py --json out.json
"""
import argparse
import json
import pathlib
import statistics
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend import config, library, retrieval, vecstore  # noqa: E402

EVAL = ROOT / "eval_queries.json"
# 与线上一致的检索参数,避免"测的是另一套配置"
SEARCH_KW = dict(top_k=5, mode="mixed", rerank=True)


# ==================== 模型调用替身 ====================

_QUERY_VEC: list[float] | None = None
_RERANK_CALLS = 0


def install_stubs(db) -> None:
    """把两个模型调用替换为确定性本地实现。返回后被替换的函数仍在,便于统计。"""
    global _QUERY_VEC
    metas = vecstore.list_partitions(db)
    if not metas:
        sys.exit("没有向量分区;先跑一次索引(或迁移),否则测不到向量通道")
    part = vecstore.open_partition(db, metas[0]["slug"])
    # 取分区里第一条已有向量当固定查询向量:维度/分布都与真实查询一致
    _QUERY_VEC = part.search().select(["vector"]).limit(1).to_arrow().to_pylist()[0]["vector"]

    def fake_embed(text, input_type_override=None, dim_override=None,
                   model_override=None):
        return _QUERY_VEC

    def fake_rerank(query, docs):
        """按查询词在文档里的出现次数打分 —— 纯 CPU,确定性,量级与真实重排不同但
        代价特征一致(线性于文档数 × 文档长度)。"""
        global _RERANK_CALLS
        _RERANK_CALLS += 1
        terms = [t for t in retrieval._query_terms(query)[0]]
        out = []
        for d in docs:
            low = d.lower()
            hits = sum(low.count(t.lower()) for t in terms)
            out.append(hits / (1.0 + hits) if hits else 0.0)
        return out

    retrieval.embed_query = fake_embed
    retrieval._call_reranker = fake_rerank


# ==================== 计时工具 ====================

def bench(fn, n=20, warmup=3) -> dict:
    for _ in range(warmup):
        fn()
    ts = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        ts.append((time.perf_counter() - t0) * 1000)
    ts.sort()
    return {"median": statistics.median(ts), "min": ts[0],
            "p95": ts[min(len(ts) - 1, int(len(ts) * 0.95))], "n": n}


def show(label: str, r: dict, note: str = ""):
    print(f"  {label:<38} 中位 {r['median']:8.2f} ms  "
          f"min {r['min']:8.2f}  p95 {r['p95']:8.2f}   {note}")


# ==================== 各组测试 ====================

def bench_channels(t, db, results: dict):
    """三个召回通道 + 回表 + 覆盖率的单项成本。"""
    print("\n--- 单通道成本(不含融合/重排) ---")
    meta = vecstore.list_partitions(db)[0]
    part = vecstore.open_partition(db, meta["slug"])
    q = "QMC6309 供电电压 VDD 范围"
    limit = config.get("cand_floor")

    r = bench(lambda: t.search(q, query_type="fts").limit(limit).to_list())
    show(f"FTS 检索 (limit={limit})", r)
    results["channel.fts"] = r

    retrieval._proj_table(t)      # 预热:投影表是进程级缓存,冷建成本单列
    r = bench(lambda: retrieval._substring_recall(t, "QMC6309", limit))
    show("子串召回 (投影已缓存)", r)
    results["channel.substring_warm"] = r

    # 冷建必须绕开 bench 的 warmup —— 否则第一次调用就把缓存填上,
    # 测到的是命中缓存的 0.1ms,完全失真。
    cold = []
    for _ in range(5):
        retrieval._PROJ_CACHE = None
        t0 = time.perf_counter()
        retrieval._proj_table(t)
        cold.append((time.perf_counter() - t0) * 1000)
    cold.sort()
    r = {"median": statistics.median(cold), "min": cold[0],
         "p95": cold[-1], "n": len(cold)}
    show("子串投影表冷建 (每进程一次)", r, "to_arrow 全表 + 选列")
    results["channel.proj_cold"] = r
    retrieval._proj_table(t)

    hits = part.search(_QUERY_VEC, query_type="vector").limit(limit).to_list()
    r = bench(lambda: part.search(_QUERY_VEC, query_type="vector").limit(limit).to_list())
    show(f"向量检索 (limit={limit})", r,
         "无向量索引=暴力扫描" if not part.list_indices() else "")
    results["channel.vector"] = r

    uids = [h["uid"] for h in hits]
    r = bench(lambda: retrieval._hydrate(t, uids))
    show(f"回表 _hydrate ({len(uids)} uid)", r)
    results["channel.hydrate"] = r

    # 覆盖率:每次 search 都会查一次,有 (slug, 表版本, 分区版本) 缓存。
    # 这里测"缓存未命中"的成本 —— 即分区刚重建、版本变化后的第一条查询。
    meta = vecstore.list_partitions(db)[0]
    def cov_cold():
        retrieval._COV_CACHE.clear()
        vecstore.coverage(db, t, meta["slug"])
    r = bench(cov_cold, n=10)
    show("覆盖率计算 (缓存未命中)", r, "扫全分区 uid,每版本一次")
    results["channel.coverage"] = r


def bench_pipeline(t, queries: list[str], results: dict):
    """完整 search():分档位看各阶段增量。

    注意别用"每轮 reset_cache()"来测:那会把进程级缓存(投影表、覆盖率)一起清掉,
    测出来的是每条查询都付一次全表物化 —— 线上冷启动后只有**第一条**付这笔钱。
    这里分两个口径:
      冷 = reset_cache 后第一条查询(含投影表/覆盖率的首次构建)
      热 = 缓存已就绪后的稳态查询
    """
    print("\n--- 完整 search() 分档 ---")

    def cold(**over):
        def f():
            retrieval.reset_cache()
            retrieval.search(t, queries[0], **{**SEARCH_KW, **over})
        return f

    def hot(**over):
        def f():
            retrieval.search(t, queries[0], **{**SEARCH_KW, **over})
        return f

    for label, key, kw in (
        ("mixed + rerank(替身)", "search.mixed_rerank", {}),
        ("mixed,无重排", "search.mixed_norerank", {"rerank": False}),
        ("仅 FTS + 子串", "search.fts_only", {"mode": "fts", "rerank": False}),
        ("仅向量", "search.vector_only", {"mode": "vector", "rerank": False}),
    ):
        r = bench(cold(**kw), n=8, warmup=1)
        show(f"{label} [冷]", r, "含首次缓存构建")

        # 热:复用投影表与覆盖率缓存,但必须**绕过结果缓存** —— 否则测到的是
        # 0.1ms 的缓存命中。直接清结果缓存,不动 _PROJ_CACHE / _COV_CACHE。
        probe = "热态探针查询 XYZ-12345"
        retrieval.search(t, probe, **{**SEARCH_KW, **kw})

        def hot_probe(**over):
            def f():
                retrieval._RESULT_CACHE.clear()
                retrieval.search(t, probe, **{**SEARCH_KW, **over})
            return f
        r2 = bench(hot_probe(**kw), n=8, warmup=2)
        show(f"{label} [热]", r2, "复用投影表/覆盖率,绕开结果缓存")
        results[key] = {"cold": r, "hot": r2}


def bench_queries(t, queries: list[str], results: dict):
    """全量查询集:看分布,不只均值。"""
    print(f"\n--- 全量 {len(queries)} 条查询(mixed + rerank,含缓存命中) ---")
    retrieval.reset_cache()
    lat = []
    for q in queries:
        t0 = time.perf_counter()
        retrieval.search(t, q, **SEARCH_KW)
        lat.append((time.perf_counter() - t0) * 1000)
    lat.sort()
    r = {"median": statistics.median(lat), "min": lat[0],
         "p95": lat[min(len(lat) - 1, int(len(lat) * 0.95))], "n": len(lat)}
    show("全部查询", r, f"max {lat[-1]:.0f} ms")
    results["queries.set"] = r

    # 缓存命中的边际成本
    r2 = bench(lambda: retrieval.search(t, queries[0], **SEARCH_KW), n=50, warmup=0)
    show("结果缓存命中", r2)
    results["search.cached"] = r2


def bench_metadata(t, results: dict):
    """/api/* 端点里那些扫全表的计算(它们各自有 version 缓存)。

    这里每次都清缓存,测的是"缓存未命中"的真实重算成本 —— 缓存命中时这些
    端点几乎不耗时,那不是需要优化的部分。
    """
    print("\n--- 元数据聚合(缓存未命中时的重算) ---")
    for label, key, fn in (
        ("categories (扫 category 列)", "meta.categories",
         lambda: library.categories(t)),
        ("files_index (全表聚合)", "meta.files",
         lambda: library.files_index(t)),
        ("extract_report (含 text 列)", "meta.report",
         lambda: library.extract_report(t, 100)),
    ):
        def once(f=fn):
            library._META_CACHE.clear()
            f()
        try:
            r = bench(once, n=5, warmup=1)
        except Exception as e:
            print(f"  {label:<38} 跳过: {e}")
            continue
        show(label, r)
        results[key] = r


def bench_scaling(t, results: dict):
    """单块文本处理随长度的增长 —— 片段窗口与重排载荷都是这块的开销。"""
    print("\n--- 单块文本处理随长度 ---")
    rows = t.search().select(["text"]).limit(t.count_rows()).to_arrow().to_pylist()
    texts = sorted((r["text"] for r in rows), key=len)
    q = "QMC6309 供电电压 VDD 范围"
    out = {}
    for frac, label in ((0.1, "短(10 分位)"), (0.5, "中位"), (0.9, "长(90 分位)")):
        txt = texts[int(len(texts) * frac)]
        r = bench(lambda: retrieval.make_snippet(txt, q), n=50)
        show(f"make_snippet {label} {len(txt)} 字符", r)
        out[label] = r
    results["snippet.scaling"] = out


def bench_concurrency(t, queries: list[str], results: dict):
    """并发下的吞吐。注意:检索本身是同步阻塞的,这里看 GIL 与 lance 的表现。"""
    import threading
    print("\n--- 并发(8 线程 x 5 次) ---")
    retrieval.reset_cache()
    errs, lat = [], []
    lock = threading.Lock()

    def worker(idx):
        for j in range(5):
            q = queries[(idx + j) % len(queries)]
            try:
                t0 = time.perf_counter()
                retrieval.search(t, q, **SEARCH_KW)
                with lock:
                    lat.append((time.perf_counter() - t0) * 1000)
            except Exception as e:
                with lock:
                    errs.append(f"{type(e).__name__}: {e}")

    ths = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    t0 = time.perf_counter()
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    wall = time.perf_counter() - t0
    lat.sort()
    print(f"  墙钟 {wall:5.1f}s  {len(lat)/wall:5.2f} q/s  "
          f"中位 {statistics.median(lat):6.0f} ms  P95 {lat[int(len(lat)*0.95)-1]:6.0f} ms  "
          f"错误 {len(errs)}")
    results["concurrency.8x5"] = {
        "wall_s": wall, "qps": len(lat) / wall,
        "median": statistics.median(lat), "errors": len(errs)}


# ==================== main ====================

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="把结果写成 JSON")
    args = ap.parse_args()

    db = library.get_db()
    if db is None:
        sys.exit("索引不存在;先跑一次 ingest")
    t = library.get_table()
    queries = [q["query"] for q in json.loads(EVAL.read_text(encoding="utf-8"))]

    install_stubs(db)
    print(f"索引: {t.count_rows()} 块 / {len(queries)} 条查询")
    print(f"分区: {[m['slug'] for m in vecstore.list_partitions(db)]}")
    print("模型调用已替换为本地确定性替身 —— 不计任何网络等待,不消耗 API 额度")

    results: dict = {"meta": {"chunks": t.count_rows(), "queries": len(queries),
                              "partitions": [m["slug"] for m in vecstore.list_partitions(db)]}}
    bench_channels(t, db, results)
    bench_pipeline(t, queries, results)
    bench_queries(t, queries, results)
    bench_metadata(t, results)
    bench_scaling(t, results)
    bench_concurrency(t, queries, results)

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n已写入 {args.json}")


if __name__ == "__main__":
    main()
