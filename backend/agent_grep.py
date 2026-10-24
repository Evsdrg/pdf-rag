"""Agent 精确检索:按页聚合索引匹配,不把分块计数冒充印刷页计数。"""
from . import library
from .agent_paging import bounded_items, fingerprint


def _normalize(text):
    return " ".join(text.replace("|", " ").split())


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
                                  "model_no": row["model_no"], "all_contexts": [],
                                  "indexed_matches": 0})
        windows = []
        text = row["text"]
        for match in regex.finditer(text):
            group["indexed_matches"] += 1
            start, end = max(0, match.start() - context), min(len(text), match.end() + context)
            if windows and start <= windows[-1]["end_offset"]:
                windows[-1]["end_offset"] = max(end, windows[-1]["end_offset"])
            else:
                windows.append({"start_offset": start, "end_offset": end,
                                "match": match.group(0)})
        for window in windows:
            content = text[window["start_offset"]:window["end_offset"]]
            normalized = _normalize(content)
            if any(_normalize(item["context"]) == normalized for item in group["all_contexts"]):
                continue
            group["all_contexts"].append({**window, "context": content,
                                          "chunk_id": row["uid"]})
    items = []
    for key in sorted(groups):
        item = groups[key]
        contexts = item.pop("all_contexts")
        item["contexts"] = contexts[:5]
        item["contexts_truncated"] = len(contexts) > 5
        item["omitted_contexts"] = max(0, len(contexts) - 5)
        items.append(item)
    revision = fingerprint((table.version, [(key, value["indexed_matches"]) for key, value in sorted(groups.items())]))
    scope = ("grep", pattern, category, file, context, flex_separator)
    return bounded_items(items, "results", {"schema_version": 2, "pattern": pattern,
                         "flex_separator": flex_separator, "count_basis": "matched_pages",
                         "matches_basis": "indexed_text_including_duplicates"},
                         scope, revision, max_hits, cursor)
