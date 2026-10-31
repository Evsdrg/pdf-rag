"""结构化检索共用的有界证据窗口;不改变默认片段算法。"""
import re

from . import config

MAX_WINDOWS = 2
MAX_HEADER_CHARS = 500


def _table_header(text: str, start: int) -> str | None:
    """只使用与窗口连续处于同一 Markdown 表中的表头。"""
    lines = text[:start].splitlines(keepends=True)
    for i in range(len(lines) - 1, 0, -1):
        line = lines[i].strip()
        if not line.startswith("|"):
            return None
        if re.fullmatch(r"\|\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?", line):
            header = lines[i - 1] + lines[i]
            if not lines[i - 1].lstrip().startswith("|") or re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", header):
                return None
            return header.rstrip() if len(header) <= MAX_HEADER_CHARS else None
    return None


def select(chunks: list[dict], query: str) -> dict:
    from . import retrieval

    width = int(config.get("snippet_width"))
    candidates, seen = [], set()
    terms, models = retrieval._query_terms(query)
    for row in chunks:
        uid = row.get("uid")
        if uid in seen:
            continue
        seen.add(uid)
        reference = retrieval.snippet_reference([row], query, width)
        if not reference:
            continue
        text = reference.pop("text")
        score = retrieval._score_window(text, terms, models)
        reference["table_header"] = _table_header(row["text"], reference["start_offset"])
        candidates.append((score, row, text, reference))
    candidates.sort(key=lambda item: -item[0])
    selected, normalized = [], set()
    for score, row, text, reference in candidates:
        signature = re.sub(r"\s+", " ", text).strip()
        if signature in normalized or (selected and score <= 0):
            continue
        normalized.add(signature)
        selected.append((row, text, reference))
        if len(selected) >= MAX_WINDOWS:
            break
    pieces, references, length = [], [], 0
    # 两个窗口共享原有 snippet_width,不把重排正文预算翻倍。
    budget = max(1, (width - 2 * max(0, len(selected) - 1)) // max(1, len(selected)))
    for row, _, _ in selected:
        reference = retrieval.snippet_reference([row], query, budget)
        reference.pop("text", None)
        start = reference["start_offset"]
        header = _table_header(row["text"], start)
        if header and len(header) > budget // 3:
            header = None
        reference["table_header"] = header
        prefix = header + "\n" if header else ""
        end = min(reference["end_offset"], start + budget - len(prefix))
        reference["end_offset"] = end
        reference["truncated_after"] = end < len(row["text"])
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", row["text"][start:end])
        piece = prefix + text
        if pieces:
            length += 2
        reference["snippet_start"] = length
        reference["snippet_end"] = length + len(piece)
        pieces.append(piece)
        references.append(reference)
        length += len(piece)
    return {"text": "\n\n".join(pieces), "references": references}
