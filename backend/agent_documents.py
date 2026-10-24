"""按需文档读取、章节导航与有界续读;不改变索引中的页号或块标识。"""
import copy
import re
import threading
import time
from collections import OrderedDict
from pathlib import Path

import fitz

from . import config, doc_utils, library
from .agent_paging import (MAX_RESPONSE_BYTES, bounded_items, decode_cursor,
                           encode_cursor, fingerprint, json_size)

_CACHE = OrderedDict()
_LOCK = threading.RLock()
_KEY_LOCKS = [threading.Lock() for _ in range(32)]
_CACHE_TTL = 300
_CACHE_BYTES = 16_000_000
_CACHE_ENTRIES = 64
_EXTRACT_PARAMS = ("ocr_smart_filter", "ocr_min_chars", "ocr_backend", "ocr_model",
                   "ocr_prompt", "ocr_api_base", "ocr_url", "ocr_dpi", "ocr_timeout",
                   "table_min_ratio")


def resolve(file: str) -> str:
    try:
        full = doc_utils.resolve_under(config.PDF_ROOT, file)
    except FileNotFoundError:
        raise library.NotFound("文件不存在或路径越界") from None
    if not Path(full).is_file():
        raise library.NotFound("文件不存在", details={"file": file})
    if not doc_utils.is_markdown(full) and Path(full).suffix.lower() != ".pdf":
        raise library.LibraryError("仅支持 PDF 或 Markdown 文档", code="UNSUPPORTED_FORMAT")
    return full


def revision(full: str) -> str:
    stat = Path(full).stat()
    return fingerprint((full, stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns,
                        stat.st_ctime_ns, tuple(config.get(k) for k in _EXTRACT_PARAMS)))


def clear_cache():
    with _LOCK:
        _CACHE.clear()


def _cached(key, build):
    # 同页续读不能重复触发 OCR;同键并发首读复用结果,不同文档不相互阻塞。
    with _LOCK:
        now = time.monotonic()
        for old in [k for k, (at, _, _) in _CACHE.items() if now - at > _CACHE_TTL]:
            _CACHE.pop(old, None)
        if key in _CACHE:
            entry = _CACHE.pop(key)
            _CACHE[key] = entry
            return copy.deepcopy(entry[1])
    lock = _KEY_LOCKS[hash(key) % len(_KEY_LOCKS)]
    with lock:
        with _LOCK:
            entry = _CACHE.get(key)
            if entry is not None:
                return copy.deepcopy(entry[1])
        value = build()
        size = json_size(value)
        if size > _CACHE_BYTES:
            raise library.LibraryError("页面提取结果过大,请改用页图裁剪", code="PAGE_TOO_LARGE")
        with _LOCK:
            while _CACHE and (len(_CACHE) >= _CACHE_ENTRIES or
                              sum(e[2] for e in _CACHE.values()) + size > _CACHE_BYTES):
                _CACHE.popitem(last=False)
            _CACHE[key] = (time.monotonic(), value, size)
        return copy.deepcopy(value)


def page_error(page: int, total: int):
    return library.LibraryError("请求页码超出文档范围", code="PAGE_OUT_OF_RANGE",
                                details={"page": page, "total_pages": total})


class Reader:
    def __init__(self, file: str):
        self.file = file
        self.full = resolve(file)
        self.revision = revision(self.full)
        self.kind = "md" if doc_utils.is_markdown(self.full) else "pdf"
        self.basis = "h1_section" if self.kind == "md" else "physical"
        self.doc = None
        self.md = None
        self.policy = None

    def __enter__(self):
        try:
            if self.kind == "md":
                self.md = _cached((self.revision, "md"), lambda: doc_utils.md_pages(self.full))
                self.total = len(self.md)
            else:
                self.doc = fitz.open(self.full)
                self.total = len(self.doc)
            return self
        except (fitz.FileDataError, RuntimeError):
            raise library.LibraryError("文档无法打开", code="DOCUMENT_UNREADABLE") from None

    def __exit__(self, *args):
        if self.doc is not None:
            self.doc.close()

    def base(self):
        return {"schema_version": 2, "file": self.file, "kind": self.kind,
                "page_basis": self.basis, "total_pages": self.total}

    def page(self, number: int):
        if number < 1 or number > self.total:
            raise page_error(number, self.total)
        def extract():
            if self.md is not None:
                return {"text": self.md[number - 1], "ocr": False, "warnings": []}
            if self.policy is None and config.get("ocr_smart_filter"):
                try:
                    thin = len(self.doc[number - 1].get_text("text").strip()) < config.get("ocr_min_chars")
                except Exception:
                    thin = True
                if thin:
                    from .ocr_policy import DocumentPolicy
                    self.policy = DocumentPolicy(self.doc)
            return doc_utils.read_page_content(self.doc, number, self.policy)
        result = _cached((self.revision, number), extract)
        if revision(self.full) != self.revision:
            raise library.LibraryError("读取期间文档发生变化,请重新读取", code="STALE_CURSOR")
        return result

    def sections(self):
        out = []
        if self.md is not None:
            fenced = False
            marker = ""
            for page, text in enumerate(self.md, 1):
                offset = 0
                for line in text.splitlines(keepends=True):
                    fence = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
                    if fence:
                        if not fenced:
                            fenced, marker = True, fence.group(1)[0]
                        elif fence.group(1)[0] == marker:
                            fenced = False
                    match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line) if not fenced else None
                    if match:
                        out.append({"level": len(match.group(1)), "title": match.group(2),
                                    "page": page, "offset": offset})
                    offset += len(line)
        else:
            out = [{"level": level, "title": title, "page": page, "offset": 0}
                   for level, title, page in self.doc.get_toc() if 1 <= page <= self.total]
        for index, item in enumerate(out):
            item["section_id"] = encode_cursor(("section", self.file), self.revision, index)
        return out


def _slice(text: str, offset: int, chars: int, byte_limit: int) -> str:
    segment = text[offset:offset + chars]
    if json_size(segment) > byte_limit:
        low, high = 0, len(segment)
        while low < high:
            middle = (low + high + 1) // 2
            if json_size(segment[:middle]) <= byte_limit:
                low = middle
            else:
                high = middle - 1
        segment = segment[:low]
    if offset + len(segment) < len(text):
        cut = segment.rfind("\n")
        if cut >= len(segment) // 2:
            segment = segment[:cut + 1]
    return segment


def read(file: str, numbers: list[int], max_chars: int, cursor: str = "",
         single: bool = False, section_id: str = "") -> dict:
    with Reader(file) as reader:
        sections = reader.sections() if section_id else []
        title = None
        start_offset = 0
        end_page, end_offset = reader.total + 1, 0
        if section_id:
            index = decode_cursor(section_id, ("section", file), reader.revision, None)
            if not isinstance(index, int) or not 0 <= index < len(sections):
                raise library.LibraryError("章节标识无效", code="INVALID_SECTION")
            section = sections[index]
            title = section["title"]
            start_page, start_offset = section["page"], section["offset"]
            for following in sections[index + 1:]:
                if following["level"] <= section["level"]:
                    end_page, end_offset = following["page"], following["offset"]
                    break
            if reader.kind == "md":
                numbers = list(range(start_page, min(end_page, reader.total) + 1))
                if end_offset == 0 and numbers and numbers[-1] == end_page:
                    numbers.pop()
            else:
                # PDF 书签没有页内坐标,相邻章节共享的物理页需要保留。
                numbers = list(range(start_page, min(end_page, reader.total) + 1))
        scope = ("read", file, numbers, single, section_id)
        position = decode_cursor(cursor, scope, reader.revision, [0, start_offset])
        if (not isinstance(position, list) or len(position) != 2 or
                any(not isinstance(v, int) or v < 0 for v in position)):
            raise library.LibraryError("游标位置无效", code="INVALID_CURSOR")
        index, offset = position
        if index >= len(numbers):
            raise library.LibraryError("游标位置无效", code="INVALID_CURSOR")
        out = []
        remaining = max_chars
        while index < len(numbers) and remaining > 0 and len(out) < 50:
            number = numbers[index]
            try:
                result = reader.page(number)
            except library.LibraryError as error:
                if single or error.code != "PAGE_OUT_OF_RANGE":
                    raise
                out.append({"page": number, "error": {"code": error.code,
                            "message": str(error), "details": error.details}})
                index, offset = index + 1, 0
                continue
            text = result["text"]
            if section_id and reader.kind == "md" and number == end_page:
                text = text[:end_offset]
            used_bytes = json_size(out)
            segment = _slice(text, offset, remaining, max(0, MAX_RESPONSE_BYTES - used_bytes - 5000))
            if not segment and offset < len(text):
                break
            stop = offset + len(segment)
            more_page = stop < len(text)
            out.append({"page": number, "text": segment, "start_offset": offset,
                        "end_offset": stop, "truncated": more_page,
                        "ocr": result["ocr"], "warnings": result["warnings"]})
            remaining -= len(segment)
            if more_page:
                offset = stop
                break
            index, offset = index + 1, 0
        more = index < len(numbers)
        payload = {**reader.base(), "truncated": more,
                   "next_cursor": encode_cursor(scope, reader.revision, [index, offset]) if more else None}
        if single:
            payload.update(out[0])
        else:
            payload["pages"] = out
        if section_id:
            payload.update(section_id=section_id, title=title,
                           section_basis="heading" if reader.kind == "md" else "bookmark_pages")
        if json_size(payload) > MAX_RESPONSE_BYTES:
            raise library.LibraryError("返回元数据超过上限,请缩小页码范围", code="RESPONSE_TOO_LARGE")
        return payload


def outline(file: str, max_level: int, limit: int, cursor: str):
    with Reader(file) as reader:
        entries = [{k: v for k, v in entry.items() if k != "offset"}
                   for entry in reader.sections() if entry["level"] <= max_level]
        return bounded_items(entries, "outline", {**reader.base(),
                             "note": "" if entries else "没有可用目录,请用 pdf_rag_grep 定位"},
                             ("outline", file, max_level), reader.revision, limit, cursor)
