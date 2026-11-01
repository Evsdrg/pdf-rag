"""关系检索评测:对多证据 / 跨页 / 条件区分 / 变体反例题集做离线评测。

只读本地索引 chunks,不联网、不调用模型、不改索引或持久配置。

    python tools/eval_relations.py --validate-only
    python tools/eval_relations.py --mode fts --no-rerank
    python tools/eval_relations.py --mode fts --no-rerank --structured --json /tmp/rel.json

指标口径(全部写死在下面,避免"看起来像准确率"的解读):

- all_target_evidence_coverage
    所有 target 都被命中的题目占比。v2 按 source_policy 限定来源和物理页,
    整页必须含参数词、literals 与 cond;content 仅允许同 MD5 内容别名。
    这是"证据可达"口径,不证明参数行列语义或料号身份。
- mean_target_recall
    逐 target 的命中率均值(同一题内各 target 等权,再对题目取平均)。
- identity_constrained_snippet_coverage
    每题 target 中,允许来源同目标页的片段含全部参数词、literals 与 cond 的比例,
    再按题平均。该历史字段名不表示订购料号已确认;identity_covered 另计字面覆盖。
- condition_misassociation
    **明确定义为纯字面共现**:对带 cond/wrong 标注的 target,若命中片段同时
    含该 target 的全部 literals 与其 wrong 标注字面值(而 cond 条件词缺失),
    则记一次"条件错配共现"。这只是字符串层面的共现检查,**不声称**系统理解了
    表格行列或条件语义;它衡量的是"片段是否把不该共现的值摆在一起"。
- wrong_variant_hit_rate
    命中里出现任一 forbidden_variants 文件的题目占比;另记原始错误变体命中条数。
- additional_page_reads
    **仅是代理**:命中结果的片段未含全部 literals、但整页索引文本含全部
    literals 的命中数量,表示"若只用片段仍需再读这一页"。不是真实翻页次数。
- 候选数 p50/p95
    来自检索诊断里的 candidates 计数分布。

--validate-only 会逐条校验标注:文件唯一存在、物理页存在、literals 在该页共存、
cond 在该页存在、wrong 在该页存在、forbidden 变体文件与字面值真实存在、
target.model_no 与索引一致、multi_model 类别各 target 型号互不相同。
v2 还要求参数词、值、条件在绑定 MD5/uid 的块内偏移共存,并明确来源策略与审校状态。
quarantined 题保留待复查但不进入评分。校验不证明语义,坏标注直接报错退出。
"""
import argparse
import json
import re
import socket
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend import config  # noqa: E402
from backend import library  # noqa: E402
from backend.retrieval import search  # noqa: E402

DATASET = ROOT / "eval_relations.json"

CATEGORIES = ("multi_model_compare", "cross_page", "condition", "variant")


# ---------- 网络出口保护 ----------

class NetworkBlocked(RuntimeError):
    """评测期间任何外连尝试都直接失败。"""


def block_network():
    """把 socket 出网封死:评测只允许读本地索引。"""
    def _deny(*args, **kwargs):
        raise NetworkBlocked("评测禁止任何外部网络连接")

    socket.socket.connect = _deny
    socket.socket.connect_ex = _deny
    socket.create_connection = _deny
    if hasattr(socket, "create_server"):
        socket.create_server = _deny


# ---------- 文本工具 ----------

def norm(s: str) -> str:
    """归一化空白与下划线,让 "500 Ω"/"500Ω"、"VDD APC"/"VDD_APC" 视为同形。"""
    return re.sub(r"[\s_]+", "", s)


def has_all(text: str, literals) -> bool:
    """全部字面值是否都出现在 text 中(分隔符宽容)。"""
    low = norm(text)
    return all(norm(x) in low for x in literals)


# ---------- 数据集 ----------

def load_dataset(path: Path = DATASET) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") not in (1, 2):
        raise ValueError(f"不支持的标注版本: {data.get('version')}")
    return data


def index_file_list(table) -> list:
    """索引里全部文件路径(去重排序)。"""
    rows = table.search().select(["file"]).limit(table.count_rows()).to_list()
    return sorted({r["file"] for r in rows})


def resolve_file(index_files, fragment: str):
    """把文件子串解析成唯一索引文件;0 个或多个都算坏标注。"""
    hits = [f for f in index_files if fragment.replace("\\", "/") in f.replace("\\", "/")]
    if len(hits) != 1:
        return None, hits
    return hits[0], hits


def page_texts(table, file: str) -> dict:
    """该文件每个物理页(1 基)的整页索引文本。"""
    rows = table.search().where("file = '" + file.replace("'", "''") + "'") \
        .select(["page", "text"]).limit(table.count_rows()).to_list()
    out: dict[int, list] = {}
    for r in rows:
        out.setdefault(int(r["page"]) + 1, []).append(r["text"])
    return {p: "\n".join(v) for p, v in out.items()}


def model_of(table, file: str):
    rows = table.search().where("file = '" + file.replace("'", "''") + "'") \
        .select(["model_no"]).limit(1).to_list()
    return rows[0]["model_no"] if rows else None


def file_metadata(table) -> dict:
    rows = table.search().select(["file", "md5", "model_no"]).limit(table.count_rows()).to_list()
    return {row["file"]: row for row in rows}


def quarantined_questions(dataset: dict) -> list[str]:
    return [q["id"] for q in dataset["questions"]
            if any(t.get("review_status") == "quarantined" for t in q["targets"])]


def target_locations(target: dict, file: str, metadata: dict) -> set[tuple[str, int]]:
    files = {file}
    digest = metadata.get(file, {}).get("md5")
    if target.get("source_policy") == "content" and digest:
        files.update(name for name, row in metadata.items() if row.get("md5") == digest)
    return {(name, target["page"]) for name in files}


def _evidence_valid(target: dict, table, file: str) -> bool:
    reference = target.get("evidence", {})
    if not isinstance(reference, dict) or reference.get("offset_basis") != "indexed_chunk":
        return False
    if reference.get("review_basis") != "indexed_parameter_context":
        return False
    rows = table.search().where("file = '" + file.replace("'", "''") + "'").select(
        ["uid", "page", "text", "md5"]
    ).limit(table.count_rows()).to_list()
    for row in rows:
        if row.get("uid") != reference.get("chunk_id") or row.get("md5") != reference.get("index_md5"):
            continue
        start, end = reference.get("start_offset"), reference.get("end_offset")
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(row["text"]):
            return False
        segment = row["text"][start:end]
        required = target.get("literals", []) + target.get("cond", []) + target.get("parameter_terms", [])
        return row["page"] + 1 == target["page"] and has_all(segment, required)
    return False


# ---------- 校验 ----------

def validate(dataset: dict, table) -> list:
    """返回问题列表;每个元素是 (error_message, question_id)。"""
    errors = []
    index_files = index_file_list(table)
    metadata = file_metadata(table) if dataset.get("version") == 2 else {}
    seen_ids = set()
    for q in dataset["questions"]:
        qid = q.get("id", "?")
        if not isinstance(q.get("query"), str) or not 1 <= len(q["query"]) <= 200:
            errors.append((f"{qid}: query 必须是 1-200 字符", qid))
        if qid in seen_ids:
            errors.append((f"{qid}: 重复的题目 id", qid))
        seen_ids.add(qid)
        if q.get("category") not in CATEGORIES:
            errors.append((f"{qid}: 未知类别 {q.get('category')!r}", qid))
        targets = q.get("targets") or []
        if not 2 <= len(targets) <= 3:
            errors.append((f"{qid}: 需要 2-3 个 evidence target,实际 {len(targets)}", qid))
        models, target_pages = [], set()
        for i, t in enumerate(targets):
            tag = f"{qid}#t{i}"
            page = t.get("page")
            if isinstance(page, bool) or not isinstance(page, int) or page < 1:
                errors.append((f"{tag}: 物理页必须是正整数", qid))
                continue
            if not isinstance(t.get("file"), str) or not t["file"].strip():
                errors.append((f"{tag}: 文件子串不可为空", qid))
                continue
            if any(not isinstance(t.get(key, []), list) or any(not isinstance(x, str) or not x.strip()
                   for x in t.get(key, [])) for key in ("literals", "cond", "wrong")):
                errors.append((f"{tag}: literals/cond/wrong 必须为非空字符串列表", qid))
                continue
            file, cand = resolve_file(index_files, t.get("file", ""))
            if file is None:
                errors.append((f"{tag}: 文件子串 {t.get('file')!r} 匹配 {len(cand)} 个索引文件(应为 1)", qid))
                continue
            pages = page_texts(table, file)
            target_pages.add((file, page))
            if page not in pages:
                errors.append((f"{tag}: {file} 没有物理页 {page}(现有 {min(pages)}-{max(pages)})", qid))
                continue
            text = pages[page]
            literals = t.get("literals") or []
            if not literals:
                errors.append((f"{tag}: 缺少 literals", qid))
            missing = [x for x in literals if norm(x) not in norm(text)]
            if missing:
                errors.append((f"{tag}: 字面值不在 {file} 第 {page} 页共现: {missing}", qid))
            for c in t.get("cond", []):
                if norm(c) not in norm(text):
                    errors.append((f"{tag}: 条件词 {c!r} 不在 {file} 第 {page} 页", qid))
            for w in t.get("wrong", []):
                if norm(w) not in norm(text):
                    errors.append((f"{tag}: 错值标注 {w!r} 不在 {file} 第 {page} 页(须真实存在才能判错配)", qid))
            if dataset.get("version") == 2:
                if t.get("source_policy") not in ("exact", "content"):
                    errors.append((f"{tag}: source_policy 必须明确为 exact/content", qid))
                terms = t.get("parameter_terms")
                if (not isinstance(terms, list) or not terms
                        or any(not isinstance(x, str) or not x.strip() for x in terms)):
                    errors.append((f"{tag}: parameter_terms 必须为非空字符串列表", qid))
                elif not _evidence_valid(t, table, file):
                    errors.append((f"{tag}: 参数/值/条件未被绑定到有效索引证据范围", qid))
                note = t.get("review_note")
                if (t.get("review_status") not in ("reviewed", "quarantined")
                        or not isinstance(note, str) or not note.strip()):
                    errors.append((f"{tag}: 缺少语义审校状态或说明", qid))
                if "accepted_pages" in t:
                    errors.append((f"{tag}: 额外证据页须另立带锚点的 target,不支持 accepted_pages", qid))
                if "identity_terms" in t:
                    identity = t["identity_terms"]
                    if (not isinstance(identity, list) or not identity
                            or any(not isinstance(x, str) or not x.strip() for x in identity)
                            or not has_all(text, identity)):
                        errors.append((f"{tag}: identity_terms 必须在目标页完整存在", qid))
            m = model_of(table, file)
            if t.get("model_no") != m:
                errors.append((f"{tag}: model_no 标注 {t.get('model_no')!r} 与索引 {m!r} 不一致", qid))
            models.append(t.get("model_no"))
        if q.get("category") == "multi_model_compare" and len(set(models)) != len(models):
            errors.append((f"{qid}: multi_model_compare 的各 target 型号必须互不相同,实际 {models}", qid))
        if q.get("category") == "cross_page" and (len({f for f, _ in target_pages}) != 1
                                                     or len(target_pages) < 2):
            errors.append((f"{qid}: cross_page 需要同一文件至少两页证据", qid))
        if q.get("category") == "variant" and not q.get("forbidden_variants") and q.get("identity_policy") != "ordering_row":
            errors.append((f"{qid}: variant 缺少 forbidden_variants", qid))
        if q.get("category") == "condition" and not any(t.get("cond") and t.get("wrong") for t in targets):
            errors.append((f"{qid}: condition 缺少条件与错值配对", qid))
        for fv in q.get("forbidden_variants", []):
            file, cand = resolve_file(index_files, fv.get("file", ""))
            if file is None:
                errors.append((f"{qid}: forbidden 变体文件 {fv.get('file')!r} 匹配 {len(cand)} 个文件(应为 1)", qid))
                continue
            pages = page_texts(table, file)
            page = fv.get("page")
            if page not in pages:
                errors.append((f"{qid}: forbidden 变体 {file} 没有物理页 {page}", qid))
                continue
            for lit in fv.get("literals", []):
                if norm(lit) not in norm(pages[page]):
                    errors.append((f"{qid}: forbidden 变体 {file} 第 {page} 页缺字面值 {lit!r}", qid))
            if dataset.get("version") == 2 and any(
                metadata.get(file, {}).get("md5") and metadata[file]["md5"] == metadata.get(name, {}).get("md5")
                for target in targets for name, _ in [resolve_file(index_files, target["file"])]
            ):
                errors.append((f"{qid}: forbidden 不能是目标的同字节内容别名", qid))
            if files_overlap(file, [t.get("file", "") for t in targets]):
                errors.append((f"{qid}: forbidden 变体文件与某个 target 指向同一文件", qid))
    return errors


def files_overlap(a: str, fragments) -> bool:
    return any(frag and frag in a for frag in fragments)


# ---------- 评测 ----------

def evaluate(dataset: dict, table, *, mode="fts", no_rerank=True, structured=False, k=5) -> dict:
    index_files = index_file_list(table)
    metadata = file_metadata(table) if dataset.get("version") == 2 else {}
    records = []
    quarantined = quarantined_questions(dataset)
    cand_counts = []
    for q in dataset["questions"]:
        if q["id"] in quarantined:
            continue
        qid = q["id"]
        resolved = []
        for t in q["targets"]:
            file, _ = resolve_file(index_files, t["file"])
            resolved.append((t, file))
        forbidden_files = []
        for fv in q.get("forbidden_variants", []):
            file, _ = resolve_file(index_files, fv["file"])
            if file:
                forbidden_files.append(file)
        diag: dict = {}
        started = time.perf_counter()
        hits = search(table, q["query"], top_k=k, mode=mode, rerank=not no_rerank,
                      structured=structured, diagnostics=diag)
        elapsed_ms = (time.perf_counter() - started) * 1000
        cand_counts.append(int((diag.get("counts") or {}).get("candidates", 0)))
        targets_detail = []
        page_covered = 0
        snippet_covered = 0
        misassoc = 0
        additional_reads = set()
        identity_targets, identity_covered = 0, 0
        for t, file in resolved:
            literals = t.get("literals") or []
            cond = t.get("cond") or []
            wrong = t.get("wrong") or []
            hit_page = False
            hit_snip = False
            locations = target_locations(t, file, metadata)
            for h in hits:
                if (h["file"], h["page"]) not in locations:
                    continue
                required = literals + cond + t.get("parameter_terms", [])
                if has_all(page_texts(table, h["file"]).get(h["page"], ""), required):
                    hit_page = True
                if has_all(h["snippet"], required):
                    hit_snip = True
                if has_all(h["snippet"], literals) and cond and wrong:
                    if has_all(h["snippet"], wrong) and not has_all(h["snippet"], cond):
                        misassoc += 1
            if t.get("identity_terms"):
                identity_targets += 1
                identity_covered += any((h["file"], h["page"]) in locations
                                        and has_all(h["snippet"], t["identity_terms"]) for h in hits)
            if not hit_snip and hit_page:
                # 片段没覆盖、但整页覆盖 => 只用片段还需再读这一页(代理量)。
                additional_reads.add((file, t["page"]))
            page_covered += int(hit_page)
            snippet_covered += int(hit_snip)
            targets_detail.append({
                "file": file, "page": t["page"], "model_no": t.get("model_no"),
                "literals": literals, "cond": cond, "wrong": wrong,
                "page_covered": hit_page, "snippet_covered": hit_snip,
            })
        # 变体命中按题计:命中列表里出现了任何一份被标注为"错误变体"的文件即计 1 次。
        wrong_variant_hits = sum(1 for h in hits if h["file"] in forbidden_files)
        n = len(resolved)
        records.append({
            "id": qid,
            "category": q["category"],
            "query": q["query"],
            "targets": targets_detail,
            "all_targets_page_covered": page_covered == n,
            "all_targets_snippet_covered": snippet_covered == n,
            "target_recall": page_covered / n if n else 0.0,
            "snippet_coverage": snippet_covered / n if n else 0.0,
            "condition_misassociation": misassoc,
            "wrong_variant_hit": int(wrong_variant_hits > 0),
            "wrong_variant_hits": wrong_variant_hits,
            "additional_page_reads": len(additional_reads),
            "identity_targets": identity_targets, "identity_covered": identity_covered,
            "elapsed_ms": elapsed_ms,
            "candidates": cand_counts[-1],
            "degraded": diag.get("degraded", []),
            "structured": diag.get("structured", {"enabled": structured, "status": "disabled"}),
            "hits": [{"file": h["file"], "page": h["page"]} for h in hits],
        })
    result = summarize(records, cand_counts, mode=mode, structured=structured, k=k)
    result["summary"].update(
        dataset_version=dataset.get("version"), quarantined_questions=quarantined,
        evidence_targets=sum(len(r["targets"]) for r in records),
        identity_targets=sum(r.get("identity_targets", 0) for r in records),
        identity_covered=sum(r.get("identity_covered", 0) for r in records),
    )
    return result


def summarize(records, cand_counts, *, mode="fts", structured=False, k=5) -> dict:
    n = len(records) or 1
    by_cat: dict[str, list] = {}
    for r in records:
        by_cat.setdefault(r["category"], []).append(r)

    def pct(x):
        return round(100.0 * x / n, 1)

    out = {
        "questions": len(records),
        "k": k,
        "mode": mode,
        "structured": structured,
        "all_target_evidence_coverage": pct(sum(1 for r in records if r["all_targets_page_covered"])),
        "mean_target_recall": round(100.0 * sum(r["target_recall"] for r in records) / n, 1),
        "identity_constrained_snippet_coverage": round(100.0 * sum(r["snippet_coverage"] for r in records) / n, 1),
        "condition_misassociation_events": sum(r["condition_misassociation"] for r in records),
        "wrong_variant_hit_rate": pct(sum(r["wrong_variant_hit"] for r in records)),
        "wrong_variant_hits_total": sum(r.get("wrong_variant_hits", 0) for r in records),
        "additional_page_reads": sum(r["additional_page_reads"] for r in records),
        "candidates_p50": statistics.median(cand_counts) if cand_counts else 0,
        "candidates_p95": (sorted(cand_counts)[min(len(cand_counts) - 1, int(0.95 * len(cand_counts)))]
                           if cand_counts else 0),
        "by_category": {},
        "latency_ms_p50": statistics.median([r.get("elapsed_ms", 0) for r in records]) if records else 0,
        "latency_ms_p95": sorted(r.get("elapsed_ms", 0) for r in records)[min(len(records)-1, int(.95*len(records)))] if records else 0,
        "degraded_queries": sum(bool(r.get("degraded")) for r in records),
    }
    for cat, rs in sorted(by_cat.items()):
        m = len(rs) or 1
        out["by_category"][cat] = {
            "questions": len(rs),
            "all_target_evidence_coverage": round(100.0 * sum(r["all_targets_page_covered"] for r in rs) / m, 1),
            "mean_target_recall": round(100.0 * sum(r["target_recall"] for r in rs) / m, 1),
            "identity_constrained_snippet_coverage": round(100.0 * sum(r["snippet_coverage"] for r in rs) / m, 1),
            "condition_misassociation_events": sum(r["condition_misassociation"] for r in rs),
            "wrong_variant_hits": sum(r.get("wrong_variant_hits", 0) for r in rs),
            "additional_page_reads": sum(r["additional_page_reads"] for r in rs),
        }
    return {"summary": out, "records": records}


def print_report(result: dict):
    s = result["summary"]
    print("=" * 68)
    print(f"关系检索评测 v{s.get('dataset_version', 1)}  mode={s['mode']}  structured={s['structured']}  k={s['k']}  题数={s['questions']}")
    print(f"隔离题: {', '.join(s.get('quarantined_questions', [])) or '无'}；证据目标: {s.get('evidence_targets', 0)}")
    print("=" * 68)
    print(f"all-target evidence coverage (整页口径) : {s['all_target_evidence_coverage']}%")
    print(f"mean target recall                       : {s['mean_target_recall']}%")
    print(f"identity-constrained snippet coverage    : {s['identity_constrained_snippet_coverage']}%")
    print(f"condition-misassociation (字面共现事件)  : {s['condition_misassociation_events']}")
    print(f"wrong variant hit rate                   : {s['wrong_variant_hit_rate']}%")
    print(f"additional page reads (代理量)            : {s['additional_page_reads']}")
    print(f"候选数 p50 / p95                         : {s['candidates_p50']} / {s['candidates_p95']}")
    print(f"延迟 ms p50 / p95                       : {s['latency_ms_p50']:.2f} / {s['latency_ms_p95']:.2f}")
    print(f"降级查询                                : {s['degraded_queries']}")
    print(f"订购身份字面覆盖(独立,非兼容确认)        : {s.get('identity_covered', 0)} / {s.get('identity_targets', 0)}")
    if s["by_category"]:
        print("-" * 68)
        print(f"{'类别':<22}{'题数':>5}{'all-target%':>14}{'recall%':>10}{'snippet%':>11}{'错配':>7}{'变体':>7}")
        for cat, v in s["by_category"].items():
            print(f"{cat:<22}{v['questions']:>5}{v['all_target_evidence_coverage']:>14}"
                  f"{v['mean_target_recall']:>10}{v['identity_constrained_snippet_coverage']:>11}"
                  f"{v['condition_misassociation_events']:>7}{v['wrong_variant_hits']:>7}")
    print("=" * 68)
    print("口径说明: 覆盖=来源策略允许的文件与目标物理页含全部值、条件及参数词;")
    print("          snippet=该来源/目标页的片段同时含上述全部约束;content 仅放宽到同 MD5 内容别名;")
    print("          condition-misassociation=片段同时含本 target 值与其标注错值且缺条件词(纯字面共现,不声称理解表格语义);")
    print("          additional page reads=片段未覆盖但整页覆盖的页数代理,非真实翻页统计。")


def main():
    ap = argparse.ArgumentParser(description="关系检索评测(只读本地索引,不联网)")
    ap.add_argument("--mode", default="fts", choices=["fts", "mixed", "vector"],
                    help="检索模式;默认 fts(纯本地全文,不需要模型)")
    ap.add_argument("--no-rerank", action="store_true", default=True,
                    help="保持关闭重排(默认;本工具不调用任何模型)")
    ap.add_argument("--rerank", dest="no_rerank", action="store_false",
                    help="显式开启重排 —— 需要外部重排服务,评测环境不支持")
    ap.add_argument("--structured", action="store_true", help="启用默认关闭的实体桥(不调用模型)")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--json", default="", help="把结果写入该 JSON 文件")
    ap.add_argument("--validate-only", action="store_true", help="只校验标注,不检索")
    ap.add_argument("--dataset", type=Path, default=DATASET, help="标注 JSON;旧版可用 eval_relations.v1.json 重放")
    args = ap.parse_args()

    block_network()
    config.override_local({"query_cache_ttl": 0})

    dataset = load_dataset(args.dataset)
    table = library.get_table()
    if table is None:
        print("索引不可用:未找到 chunks 表", file=sys.stderr)
        return 2

    errors = validate(dataset, table)
    if errors:
        print(f"标注校验失败({len(errors)} 项),不做评测:", file=sys.stderr)
        for msg, qid in errors:
            print(f"  [{qid}] {msg}", file=sys.stderr)
        return 2
    quarantined = quarantined_questions(dataset)
    print(f"字面/锚点校验通过:v{dataset['version']}，{len(dataset['questions'])} 题；"
          f"可评分 {len(dataset['questions']) - len(quarantined)} 题，隔离 {len(quarantined)} 题。此校验不证明参数语义。")

    if args.validate_only:
        return 0

    if not args.no_rerank:
        print("评测环境不支持真实模型调用(重排需要外部服务),请使用默认 --no-rerank。", file=sys.stderr)
        return 2
    if args.mode != "fts":
        print(f"评测环境只支持 --mode fts(离线);{args.mode} 需要嵌入/模型服务,已拒绝。", file=sys.stderr)
        return 2

    result = evaluate(dataset, table, mode=args.mode, no_rerank=True,
                      structured=args.structured, k=args.k)
    print_report(result)
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"结果已写入 {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
