"""结构化检索共用的有界证据窗口;优先保全主证据,副窗须有查询信息增益。"""
import re

from . import config, query_lex

MAX_WINDOWS = 2
MAX_HEADER_CHARS = 500
_CONTROLS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _table_header(text: str, start: int) -> str | None:
    """只使用与窗口连续处于同一 Markdown 表中的表头。"""
    lines = text[:start].splitlines(keepends=True)
    for i in range(len(lines) - 1, 0, -1):
        line = lines[i].strip()
        if not line.startswith("|"):
            return None
        if re.fullmatch(r"\|\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?", line):
            header = lines[i - 1] + lines[i]
            if not lines[i - 1].lstrip().startswith("|") or _CONTROLS.search(header):
                return None
            return header.rstrip() if len(header) <= MAX_HEADER_CHARS else None
    return None


def _coverage(text: str, query: str, terms=None, query_keys=None) -> set[str]:
    if terms is None:
        terms, _ = query_lex.query_terms(query)
    low = text.casefold()
    literal = {"term:" + term.casefold() for term in terms if term.casefold() in low}
    if query_keys is None:
        query_keys = {key for key in query_lex.extract_entities(query, query=True) if not key.startswith("model:")}
    return literal | query_keys.intersection(query_lex.extract_entities(text))


def _window(row: dict, query: str, width: int, terms=None, models=None) -> tuple[int, int]:
    """在预算内选完整行;超长单行才保留显式截断,不为第二窗重定位主证据。"""
    from . import retrieval
    text = row["text"]
    if len(text) <= width:
        return 0, len(text)
    if terms is None or models is None:
        terms, models = retrieval._query_terms(query)
    best, score = (0, min(width, len(text))), -1.0
    starts = retrieval._window_starts(len(text), width)
    for offset in starts:
        before = text.rfind("\n", max(0, offset - 120), offset)
        start = before + 1 if before >= 0 else offset
        end = min(len(text), start + width)
        if end < len(text) and text[end - 1:end] != "\n":
            boundary = text.rfind("\n", start, end)
            if boundary > start:
                end = boundary + 1
        candidate_score = retrieval._score_window(text[start:end], terms, models)
        if candidate_score > score:
            best, score = (start, end), candidate_score
    return best


def _compact(row: dict, start: int, end: int, query: str) -> tuple[int, int]:
    """只去首尾空白;条件可能另起段,不能按关键词裁掉“无关”段落。"""
    text = row["text"][start:end]
    return start + len(text) - len(text.lstrip()), end - len(text) + len(text.rstrip())


def _piece(row: dict, start: int, end: int, width: int) -> tuple[str, dict]:
    raw = row["text"]
    text = _CONTROLS.sub("", raw[start:end])
    header = _table_header(raw, start)
    prefix = header + "\n" if header and len(header) + 1 + len(text) <= width else ""
    reference = {"chunk_id": row.get("uid"), "index_md5": row.get("md5"),
                 "start_offset": start, "end_offset": end, "offset_basis": "indexed_chunk",
                 "truncated_before": start > 0, "truncated_after": end < len(raw),
                 "table_header": header if prefix else None,
                 "warnings": ([{"code": "TEXT_CONTROLS_REMOVED", "message": "展示已移除控制字符,未修复原文"}]
                              if text != raw[start:end] else [])}
    return prefix + text, reference


def _prepare(query: str):
    terms, models = query_lex.query_terms(query)
    keys = {key for key in query_lex.extract_entities(query, query=True) if not key.startswith("model:")}
    return terms, models, keys


class Bundles(dict):
    """每请求按需生成并复用证据包;窗口重排会取全池,无重排只取实际展示页。"""
    def __init__(self, chunks_by_key: dict, query: str):
        super().__init__()
        self.chunks_by_key = chunks_by_key
        self.query = query
        self.prepared = _prepare(query)

    def __missing__(self, key):
        bundle = select(self.chunks_by_key[key], self.query, prepared=self.prepared)
        self[key] = bundle
        return bundle


def select(chunks: list[dict], query: str, *, prepared=None) -> dict:
    from . import retrieval

    width = int(config.get("snippet_width"))
    terms, models, query_keys = _prepare(query) if prepared is None else prepared
    candidates, seen = [], set()
    for row in chunks:
        identity = row.get("uid") or (row.get("file"), row.get("page"), row["text"])
        if identity in seen or not row["text"].strip():
            continue
        seen.add(identity)
        start, end = _window(row, query, width, terms, models)
        text = row["text"][start:end]
        candidates.append((retrieval._score_window(text, terms, models), row, start, end))
    candidates.sort(key=lambda item: -item[0])
    if not candidates:
        return {"text": "", "references": []}

    _, main, start, end = candidates[0]
    # 主窗可用全部预算;只去首尾空白,有余量才考虑互补证据。
    compact_start, compact_end = _compact(main, start, end, query)
    main_text, main_ref = _piece(main, compact_start, compact_end, width)
    selected = [(main_text, main_ref)]
    covered = _coverage(main_text, query, terms, query_keys)
    remaining = width - len(main_text) - 2
    best_secondary, best_gain = None, (0, 0.0)
    if remaining > 0:
        for score, row, candidate_start, candidate_end in candidates[1:]:
            lo, hi = _compact(row, candidate_start, candidate_end, query)
            # 不能为塞入副窗硬切连续条件/参数行;放不下就保留单个完整主窗。
            if hi - lo > remaining:
                continue
            text, reference = _piece(row, lo, hi, remaining)
            gain = _coverage(text, query, terms, query_keys) - covered
            priority = (len(gain), score)
            if gain and priority > best_gain:
                best_secondary, best_gain = (text, reference), priority
    if best_secondary and MAX_WINDOWS > 1:
        selected.append(best_secondary)
    pieces, references, length = [], [], 0
    for text, reference in selected:
        if pieces:
            length += 2
        reference.update(snippet_start=length, snippet_end=length + len(text))
        pieces.append(text)
        references.append(reference)
        length += len(text)
    return {"text": "\n\n".join(pieces), "references": references}
