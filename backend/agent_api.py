"""MCP 与统一 REST 查询/读取接口共享的领域入口。"""
import json
import logging
import re
from datetime import datetime
from pathlib import Path

from . import agent_documents, agent_grep, config, library, retrieval
from .agent_paging import MAX_RESPONSE_BYTES, bounded_items, fingerprint, json_size

log = logging.getLogger("pdfrag.agent_api")
SCHEMA_VERSION = 2


def response(**values) -> dict:
    return {"schema_version": SCHEMA_VERSION, **values}


def error_payload(error: library.LibraryError) -> dict:
    return response(error={"code": error.code, "message": str(error), "details": error.details})


def invoke(function, *args, **kwargs) -> tuple[dict, int]:
    try:
        return function(*args, **kwargs), 200
    except library.LibraryError as error:
        return error_payload(error), error.status
    except Exception:
        log.exception("Agent 请求失败")
        error = library.LibraryError("请求执行失败,请检查服务端日志", code="INTERNAL_ERROR")
        return error_payload(error), 500


def require_table():
    table = library.get_table()
    if table is None:
        raise library.LibraryError("索引不存在,请先通过管理界面构建索引", code="INDEX_NOT_FOUND")
    return table


def check_int(value: int, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise library.LibraryError(f"{name} 需在 {low}–{high} 之间", details={"parameter": name})
    return value


def _read_budget(max_chars: int) -> int:
    value = max_chars or min(int(config.get("page_max_chars")), 12000)
    return check_int(value, "max_chars", 256, 12000)


def read_page(file: str, page: int, max_chars: int = 0, cursor: str = "") -> dict:
    check_int(page, "page", 1, 1_000_000)
    return agent_documents.read(file, [page], _read_budget(max_chars), cursor, single=True)


def read_pages(file: str, pages: str, max_chars: int = 0, cursor: str = "") -> dict:
    numbers = library.parse_page_spec(pages, max_pages=50)
    return agent_documents.read(file, numbers, _read_budget(max_chars), cursor)


def read_section(file: str, section_id: str, max_chars: int = 0, cursor: str = "") -> dict:
    if not section_id:
        raise library.LibraryError("section_id 不可为空", code="INVALID_SECTION")
    return agent_documents.read(file, [], _read_budget(max_chars), cursor, section_id=section_id)


def get_outline(file: str, max_level: int = 2, limit: int = 60, cursor: str = "") -> dict:
    check_int(max_level, "max_level", 1, 6)
    check_int(limit, "limit", 1, 100)
    return agent_documents.outline(file, max_level, limit, cursor)


def list_files(category: str = "", file: str = "", model_no: str = "", kind: str = "",
               limit: int = 30, cursor: str = "") -> dict:
    check_int(limit, "limit", 1, 100)
    if kind not in ("", "pdf", "md"):
        raise library.LibraryError("kind 需为 pdf 或 md")
    table = require_table()
    files = library.files_index(table)
    check_category(table, category)
    files = [{**f, "pages_basis": "indexed_max_page"} for f in files
             if (not category or f["category"] == category)
             and (not file or file.replace("\\", "/").casefold() in f["file"].casefold())
             and (not model_no or model_no.casefold() in f["model_no"].casefold())
             and (not kind or f["kind"] == kind)]
    scope = ("files", category, file, model_no, kind)
    revision = fingerprint((config.DB_PATH, table.version, files))
    return bounded_items(files, "files", response(), scope, revision, limit, cursor)


def list_categories() -> dict:
    values = library.categories(require_table())
    return response(categories=values, count=len(values))


def check_category(table, category: str):
    if category and category not in library.categories(table):
        raise library.LibraryError("该分类未在索引中找到,请先读取类别列表", code="CATEGORY_NOT_FOUND",
                                   details={"category": category})


def grep(pattern: str, category: str = "", file: str = "", max_hits: int = 20,
         context: int = 60, flex_separator: bool = True, cursor: str = "") -> dict:
    check_int(max_hits, "max_hits", 1, 100)
    check_int(context, "context", 0, 500)
    if not pattern or len(pattern) > 300:
        raise library.LibraryError("pattern 需包含1–300个字符")
    table = require_table()
    check_category(table, category)
    return agent_grep.grep(table, pattern, category, file, max_hits, context, flex_separator, cursor)


def _identity(query: str, hits: list[dict]) -> tuple[list, list]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*", query)
    tokens = [token for token in tokens if re.search(r"\d", token) and len(token) >= 4
              and not re.fullmatch(r"(?:i[23]c|spi|qspi|uart|usart|gpio|adc|dac|pwm|timer|tim|usb|can|sdio|i2s)\d*", token, re.I)
              and not re.fullmatch(r"v\d+(?:[._-]\d+)*", token, re.I)]
    if not tokens:
        return [], []
    identities = []
    for token in dict.fromkeys(tokens):
        matched = [hit["file"] for hit in hits if token.casefold() in
                   (Path(hit["file"]).name + " " + hit.get("model_no", "")).casefold()]
        identities.append({"token": token, "status": "matched" if matched else "unconfirmed",
                           "files": list(dict.fromkeys(matched))})
    warnings = []
    if any(item["status"] == "unconfirmed" for item in identities):
        warnings.append({"code": "MODEL_IDENTITY_UNCONFIRMED",
                         "message": "返回文档未确认查询中的型号身份;相近结果不代表该型号存在"})
    return identities, warnings


def search(query: str, category: str = "", top_k: int = 5, file: str = "",
           max_per_doc: int = 0, mode: str = "mixed", rerank: bool = True) -> dict:
    if not query.strip() or len(query) > 200:
        raise library.LibraryError("query 需包含 1–200 个字符")
    check_int(top_k, "top_k", 1, 20)
    check_int(max_per_doc, "max_per_doc", 0, 20)
    if mode not in ("mixed", "fts", "vector"):
        raise library.LibraryError("mode 需为 mixed、fts 或 vector")
    diagnostics = {}
    table = require_table()
    check_category(table, category)
    hits = retrieval.search(table, query, category=category or None,
                            top_k=top_k, file=file or None, max_per_doc=max_per_doc,
                            mode=mode, rerank=rerank, diagnostics=diagnostics)
    hits = [dict(hit) for hit in hits]
    for hit in hits:
        reference = hit.get("snippet_ref")
        if reference:
            reference = dict(reference)
            hit["snippet"] = reference.pop("text", hit["snippet"])
            hit["snippet_ref"] = reference
    omitted = 0
    while len(hits) > 1 and json_size(hits) > MAX_RESPONSE_BYTES - 5000:
        hits.pop()
        omitted += 1
    identities, warnings = _identity(query, hits)
    payload = response(query=query, count=len(hits), results=hits,
                    truncated=bool(omitted), omitted_results=omitted,
                    continuation_hint="缩小 file/category 或 top_k 后重查" if omitted else "",
                    identity=identities, warnings=diagnostics.get("warnings", []) + warnings,
                    vector_partitions=diagnostics.get("vector_partitions", []),
                    degraded=diagnostics.get("degraded", []),
                    notice=diagnostics.get("notice", ""),
                    counts={**diagnostics.get("counts", {}), "returned": len(hits)},
                    cached=diagnostics.get("cached", False))
    if json_size(payload) > MAX_RESPONSE_BYTES:
        raise library.LibraryError("返回内容超过上限,请缩小查询范围", code="RESPONSE_TOO_LARGE")
    return payload


def status() -> dict:
    from . import ocr
    table = library.get_table()
    files = library.files_index(table) if table is not None else []
    history = Path(config.DB_PATH).parent / "ingest_history.json"
    try:
        records = json.loads(history.read_text(encoding="utf-8"))
        last_ingest = records[-1].get("time") if records else None
    except (OSError, ValueError, KeyError, TypeError):
        last_ingest = None
    try:
        inventory = library.source_inventory(files)
        source_status, warnings = "ok", []
    except library.LibraryError as error:
        inventory = {key: None for key in ("source_files", "source_by_kind", "indexed_by_kind",
                                            "unindexed_files", "unindexed_by_kind", "missing_source_files")}
        inventory.update(indexed_files=len(files), unindexed_examples=[], missing_source_examples=[])
        source_status = "unavailable"
        warnings = [{"code": error.code, "message": str(error)}]
    return response(indexed=table is not None, files=len(files),
                    chunks=sum(f["chunks"] for f in files),
                    categories=len({f["category"] for f in files}),
                    last_ingest=last_ingest,
                    last_ingest_status="recorded" if last_ingest else "unknown",
                    source_status=source_status, warnings=warnings,
                    **inventory,
                    ocr=ocr.status(),
                    checked_at=datetime.now().isoformat(timespec="seconds"))
