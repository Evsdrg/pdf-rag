"""面向 Agent 的共享响应协议;MCP 和 REST v2 使用同一领域入口。"""
import json
import logging
from datetime import datetime
from pathlib import Path

from . import agent_documents, config, doc_utils, library, retrieval
from .agent_paging import bounded_items, fingerprint

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


def read_page(file: str, page: int, max_chars: int = 8000, cursor: str = "") -> dict:
    check_int(page, "page", 1, 1_000_000)
    check_int(max_chars, "max_chars", 256, 12000)
    return agent_documents.read(file, [page], max_chars, cursor, single=True)


def read_pages(file: str, pages: str, max_chars: int = 8000, cursor: str = "") -> dict:
    check_int(max_chars, "max_chars", 256, 12000)
    numbers = library.parse_page_spec(pages, max_pages=50)
    return agent_documents.read(file, numbers, max_chars, cursor)


def read_section(file: str, section_id: str, max_chars: int = 8000, cursor: str = "") -> dict:
    check_int(max_chars, "max_chars", 256, 12000)
    if not section_id:
        raise library.LibraryError("section_id 不可为空", code="INVALID_SECTION")
    return agent_documents.read(file, [], max_chars, cursor, section_id=section_id)


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


def grep(pattern: str, category: str = "", file: str = "", max_hits: int = 20,
         context: int = 60, flex_separator: bool = True) -> dict:
    check_int(max_hits, "max_hits", 1, 200)
    check_int(context, "context", 0, 500)
    if not pattern:
        raise library.LibraryError("pattern 不可为空")
    return response(**library.grep_rows(require_table(), pattern, category, file,
                                       max_hits, context, flex_separator))


def search(query: str, category: str = "", top_k: int = 5, file: str = "",
           max_per_doc: int = 0, mode: str = "mixed", rerank: bool = True) -> dict:
    if not query.strip() or len(query) > 200:
        raise library.LibraryError("query 需包含 1–200 个字符")
    check_int(top_k, "top_k", 1, 20)
    check_int(max_per_doc, "max_per_doc", 0, 20)
    if mode not in ("mixed", "fts", "vector"):
        raise library.LibraryError("mode 需为 mixed、fts 或 vector")
    diagnostics = {}
    hits = retrieval.search(require_table(), query, category=category or None,
                            top_k=top_k, file=file or None, max_per_doc=max_per_doc,
                            mode=mode, rerank=rerank, diagnostics=diagnostics)
    return response(query=query, count=len(hits), results=hits,
                    degraded=diagnostics.get("degraded", []),
                    notice=diagnostics.get("notice", ""),
                    counts=diagnostics.get("counts", {}),
                    cached=diagnostics.get("cached", False))


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
    return response(indexed=table is not None, files=len(files),
                    chunks=sum(f["chunks"] for f in files),
                    categories=len({f["category"] for f in files}),
                    last_ingest=last_ingest, ocr=ocr.status(),
                    checked_at=datetime.now().isoformat(timespec="seconds"))
