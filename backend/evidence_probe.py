"""离线证据效率原型,不接入API/默认检索,不调用模型或修改索引。"""
import re
from dataclasses import dataclass

from . import library, retrieval, table_facts

MAX_SOURCE_FILES = 4
MAX_NEEDS = 8
MAX_PAGE_BLOCKS = 64
MAX_REFILL_CALLS = 3
MAX_SOURCE_ROWS = 512
MAX_SOURCE_CHARS = 2_000_000


def _supplement(table, file: str, need: dict, seen_pages: set[int]) -> list[dict]:
    """有界本地参数字面补查;只用任务参数,不能接收目标页/答案/uid。"""
    found = table.search().where("file = '" + file.replace("'", "''") + "'").select(
        ["uid", "file", "page", "text", "md5", "model_no", "category", "c_id", "version"]
    ).limit(MAX_SOURCE_ROWS + 1).to_list()
    if len(found) > MAX_SOURCE_ROWS or sum(len(row["text"]) for row in found) > MAX_SOURCE_CHARS:
        return []
    matched = [row for row in found if row["page"] + 1 not in seen_pages
               and _literal(need["parameter"]) in _literal(row["text"])]
    grouped = {}
    for row in matched:
        grouped.setdefault(row["page"], []).append(row)
    ranked = sorted(grouped, key=lambda page: (not bool(bind_rows(grouped[page], [need])[0]), page))[:2]
    cands = retrieval._Candidates(60, 5)
    for rank, page in enumerate(ranked):
        for row in grouped[page]:
            cands.add(row, rank)
    return retrieval._build_results(cands.top(2), cands, {}, need["parameter"], 2, 0)


def _condition_literal(text: str) -> str:
    # 只宽容空白/下标分隔,保留SI大小写,不换算、不按子串匹配条件。
    return re.sub(r"[\s_]+", "", text).replace("µ", "u").replace("μ", "u")


def bind_rows(rows: list[dict], needs) -> tuple[list[dict], list[int]]:
    """只绑定同一显式行的参数/角色/完整字面条件;缺失项留给回读而非猜测。"""
    bindings, missing = [], []
    for index, need in enumerate(needs[:MAX_NEEDS]):
        candidates = []
        for row in rows:
            # query用于让已存在提取器保留该参数,不改其每块cap4及保守空白格规则。
            for fact in table_facts.extract(row, query=need["parameter"], max_facts=4):
                names = {_literal(fact["parameter"]), _literal(fact["symbol"] or "")}
                if _literal(need["parameter"]) not in names:
                    continue
                if need.get("role") and need["role"] not in fact["values"]:
                    continue
                if need.get("condition") and _condition_literal(need["condition"]) != _condition_literal(fact["conditions"]):
                    continue
                source = dict(fact["source"], file=row["file"], page=row["page"] + 1)
                # 绑定只说明行字面正确,不宣称表外条件或脚注已经解决。
                candidates.append({"need": index, **fact, "source": source,
                    "verification": "literal_row_only", "context_status": "requires_page_context"})
        identities = {(item["parameter"], item["symbol"], item["conditions"], item["unit"],
                       tuple(sorted(item["values"].items()))) for item in candidates}
        if len(identities) == 1:
            bindings.append(candidates[0])
        else:
            missing.append(index)
    return bindings, missing


def _hit_rows(table, hits: list[dict]) -> list[dict]:
    rows = []
    for hit in hits:
        file = hit["file"].replace("'", "''")
        found = table.search().where(f"file = '{file}' AND page = {int(hit['page']) - 1}").select(
            ["uid", "file", "page", "text", "md5", "model_no"]
        ).limit(MAX_PAGE_BLOCKS + 1).to_list()
        if len(found) > MAX_PAGE_BLOCKS:
            continue
        rows.extend(found)
    return list({row["uid"]: row for row in rows}.values())


@dataclass(frozen=True, slots=True)
class SourceSelection:
    status: str
    files: tuple[str, ...]
    candidates: tuple[str, ...]
    reason: str


def _literal(text: str) -> str:
    return re.sub(r"\s+", "", text).casefold()


def select_sources(table, model: str, source_terms=(), revision: str = "") -> SourceSelection:
    """显式约束只作字面核验;未找到/多内容来源不默默放宽,不推断厂商或版本继承。"""
    if not model.strip():
        return SourceSelection("unconfirmed", (), (), "missing_model")
    rows = library.scan_columns(table, ["file", "page", "model_no", "version", "title", "text", "md5"])
    documents = {}
    for row in rows:
        identity = _literal(row.get("model_no") or "")
        if not identity.startswith(_literal(model)):
            continue
        doc = documents.setdefault(row["file"], {"identity": identity, "md5": row.get("md5"),
            "version": row.get("version", ""), "title": row.get("title", ""), "front": []})
        if row["page"] == 0:
            doc["front"].append(row["text"][:8000])
    selected = []
    for file, doc in documents.items():
        evidence = " ".join([file, doc["title"], *doc["front"]])
        if not all(_literal(term) in _literal(evidence) for term in source_terms):
            continue
        if revision and _literal(doc["version"]) != _literal(revision):
            # 只认明确Rev/Revision字段,不能从任意包含字母的标题猜版本。
            versions = re.findall(r"\bRev(?:ision)?[.:\s]+([A-Za-z0-9]+(?:\.[0-9]+)*)\b", evidence, re.I)
            if _literal(revision) not in {_literal(value) for value in versions}:
                continue
        selected.append(file)
    if not selected:
        return SourceSelection("not_found", (), (), "no_literal_source_match")
    digests = {documents[file]["md5"] or ("file", file) for file in selected}
    if len(digests) > 1:
        return SourceSelection("ambiguous", (), tuple(sorted(selected)[:MAX_SOURCE_FILES]), "multiple_distinct_sources")
    selected.sort(key=lambda file: (documents[file]["identity"] != _literal(model), file))
    # 同字节别名只选一个引用,不据此确认订购行。
    return SourceSelection("resolved", (selected[0],), tuple(selected[:MAX_SOURCE_FILES]), "literal_source_only")


def run(table, query: str, *, model: str, source_terms=(), revision: str = "", needs=(),
        refill: bool = False, compact: bool = False, bind: bool = True) -> dict:
    if len(needs) > MAX_NEEDS:
        raise ValueError("证据需求超过原型预算")
    selected = select_sources(table, model, source_terms, revision)
    source = {"status": selected.status, "files": list(selected.files),
              "candidates": list(selected.candidates), "reason": selected.reason}
    if selected.status != "resolved":
        result = {"status": selected.status, "source": source, "results": [], "bindings": [],
                  "missing": list(range(len(needs))), "degraded": []}
        return {**result, "_turns": [dict(result)]}
    diag = {}
    hits = retrieval.search(table, query, file=selected.files[0], top_k=5,
                            mode="fts", rerank=False, structured=True, diagnostics=diag)
    bindings, missing = bind_rows(_hit_rows(table, hits), needs) if bind else ([], list(range(len(needs))))
    turns = [{"stage": "initial", "source": source, "results": list(hits), "bindings": list(bindings),
              "missing": list(missing), "degraded": diag.get("degraded", [])}]
    if refill and bind:
        attempted = set()
        for _ in range(MAX_REFILL_CALLS):
            unresolved = [index for index in missing if index not in attempted]
            if not unresolved:
                break
            index = unresolved[0]
            attempted.add(index)
            extra = _supplement(table, selected.files[0], needs[index], {hit["page"] for hit in hits})
            hits.extend(extra)
            hits = list({(hit["file"], hit["page"]): hit for hit in hits}.values())
            bindings, missing = bind_rows(_hit_rows(table, hits), needs)
            turns.append({"stage": "refill", "need": index, "results": extra,
                          "bindings": list(bindings), "missing": list(missing)})
    result = {"status": "row_evidence" if bindings else "retrieved", "source": source,
              "results": hits, "bindings": bindings, "missing": missing,
              "degraded": diag.get("degraded", [])}
    return {**result, "_turns": turns}
