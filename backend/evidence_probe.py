"""离线证据效率原型,不接入API/默认检索,不调用模型或修改索引。"""
import re
from dataclasses import dataclass

from . import library, retrieval

MAX_SOURCE_FILES = 4


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
    result = {"status": "retrieved", "source": source, "results": hits, "bindings": [],
              "missing": list(range(len(needs))), "degraded": diag.get("degraded", [])}
    return {**result, "_turns": [dict(result)]}
