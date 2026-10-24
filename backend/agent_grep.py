"""Agent 精确检索:按页聚合索引匹配,不把分块计数冒充印刷页计数。"""
import re

from . import library
from .agent_paging import bounded_items, fingerprint


def _normalize(text):
    return re.sub(r"[\s|]+", "", text)


def grep(table, pattern: str, category: str, file: str, max_hits: int, context: int,
         flex_separator: bool, cursor: str):
    _, regex = library.compile_search_regex(pattern, flex_separator)
    data = library.scan_arrow(table, ["uid", "file", "page", "text", "category", "model_no"])
    groups = {}
    for row in data.to_pylist():
        if category and row["category"] != category:
            continue
        if file and file.replace("\\", "/") not in row["file"]:
            continue
        if not regex.search(row["text"]):
            continue
        key = (row["file"], int(row["page"]) + 1)
        group = groups.setdefault(key, {"file": key[0], "page": key[1],
                                  "model_no": row["model_no"], "contexts": [],
                                  "indexed_matches": 0})
        for match in regex.finditer(row["text"]):
            group["indexed_matches"] += 1
            if len(group["contexts"]) >= 5:
                continue
            start, end = max(0, match.start() - context), min(len(row["text"]), match.end() + context)
            window = row["text"][start:end]
            normalized = _normalize(window)
            if any(_normalize(item["context"]) == normalized for item in group["contexts"]):
                continue
            group["contexts"].append({"match": match.group(0), "context": window,
                                      "chunk_id": row["uid"], "start_offset": start,
                                      "end_offset": end})
    items = []
    for key in sorted(groups):
        item = groups[key]
        item["contexts_truncated"] = item["indexed_matches"] > len(item["contexts"])
        items.append(item)
    revision = fingerprint((table.version, [(key, value["indexed_matches"]) for key, value in sorted(groups.items())]))
    scope = ("grep", pattern, category, file, context, flex_separator)
    return bounded_items(items, "results", {"schema_version": 2, "pattern": pattern,
                         "flex_separator": flex_separator, "count_basis": "matched_pages",
                         "matches_basis": "indexed_text_including_duplicates"},
                         scope, revision, max_hits, cursor)
