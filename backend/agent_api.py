"""面向 Agent 的共享响应协议;MCP 和 REST v2 使用同一领域入口。"""
import json
import logging
from datetime import datetime
from pathlib import Path

import fitz

from . import config, doc_utils, library, retrieval

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


def document_path(file: str) -> str:
    try:
        full = doc_utils.resolve_under(config.PDF_ROOT, file)
    except FileNotFoundError:
        raise library.NotFound("文件不存在或路径越界") from None
    if not Path(full).is_file():
        raise library.NotFound("文件不存在", details={"file": file})
    if not doc_utils.is_markdown(full) and Path(full).suffix.lower() != ".pdf":
        raise library.LibraryError("仅支持 PDF 或 Markdown 文档", code="UNSUPPORTED_FORMAT")
    return full


def page_error(page: int, total: int) -> library.LibraryError:
    return library.LibraryError("请求页码超出文档范围", code="PAGE_OUT_OF_RANGE",
                                details={"page": page, "total_pages": total})


def read_page(file: str, page: int) -> dict:
    full = document_path(file)
    if doc_utils.is_markdown(full):
        pages = doc_utils.md_pages(full)
        total = len(pages)
        if page < 1 or page > total:
            raise page_error(page, total)
        result = {"text": pages[page - 1], "ocr": False, "warnings": []}
        kind, basis = "md", "h1_section"
    else:
        with fitz.open(full) as doc:
            total = len(doc)
            if page < 1 or page > total:
                raise page_error(page, total)
            result = doc_utils.read_page_content(doc, page)
        kind, basis = "pdf", "physical"
    return response(file=file, kind=kind, page=page, page_basis=basis,
                    total_pages=total, **result)


def read_pages(file: str, pages: str) -> dict:
    numbers = library.parse_page_spec(pages)
    out = []
    total = 0
    for page in numbers:
        try:
            item = read_page(file, page)
            total = item["total_pages"]
            out.append({k: v for k, v in item.items() if k not in ("schema_version", "file")})
        except library.LibraryError as error:
            if error.code != "PAGE_OUT_OF_RANGE":
                raise
            total = error.details["total_pages"]
            out.append({"page": page, "error": error_payload(error)["error"]})
    return response(file=file, total_pages=total, pages=out)


def get_outline(file: str) -> dict:
    document_path(file)
    return response(**library.doc_outline(config.PDF_ROOT, file))


def list_files(category: str = "") -> dict:
    files = library.files_index(require_table())
    if category:
        files = [f for f in files if f["category"] == category]
    files = [{**f, "pages_basis": "indexed_max_page"} for f in files]
    return response(files=files, count=len(files))


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
