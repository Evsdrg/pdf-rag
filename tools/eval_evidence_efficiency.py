"""证据效率冻结验证:只读本地,拒绝网络/模型,不把字节数称作token。"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend import config, library, retrieval
from tools.eval_relations import block_network

DATASET = ROOT / "eval_evidence_efficiency.json"


def size(value):
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return {"bytes": len(text.encode()), "chars": len(text),
            "lexical_units_proxy": len(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]|[^\w\s]", text))}


def contains(text, values):
    normalized = re.sub(r"[\s_]+", "", text)
    return all(re.sub(r"[\s_]+", "", value) in normalized for value in values)


def validate(data, rows):
    by_uid = {row["uid"]: row for row in rows}
    for q in data["questions"]:
        for target in q["targets"]:
            row = by_uid[target["chunk_id"]]
            assert row["md5"] == target["index_md5"] and row["file"] == target["file"]
            assert row["page"] + 1 == target["page"]
            assert contains(row["text"][target["start_offset"]:target["end_offset"]], target["required"])


def binding_valid(binding, need, rows):
    """评分复核独立回到引用的表头与原行,不以原型给出的状态自证正确。"""
    by_uid = {row["uid"]: row for row in rows}
    ref = binding["source"]
    row = by_uid.get(ref.get("chunk_id"))
    if not row or row["md5"] != ref.get("index_md5") or row["file"] != ref.get("file"):
        return False
    if row["page"] + 1 != ref.get("page"):
        return False
    offsets = [ref.get(key) for key in ("header_start_offset", "header_end_offset", "start_offset", "end_offset")]
    if (any(type(value) is not int for value in offsets)
            or not 0 <= offsets[0] < offsets[1] <= offsets[2] < offsets[3] <= len(row["text"])):
        return False
    raw = row["text"][ref["start_offset"]:ref["end_offset"]]
    header = row["text"][ref["header_start_offset"]:ref["header_end_offset"]].splitlines()[0]
    cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
    labels = [cell.strip().casefold().rstrip(".") for cell in header.strip().strip("|").split("|")]
    if len(cells) != len(labels) or need.get("role") not in labels:
        return False
    value = cells[labels.index(need["role"])]
    unit_key = next((i for i, label in enumerate(labels) if label in ("unit", "units")), None)
    if unit_key is None or binding.get("unit") != cells[unit_key]:
        return False
    condition_key = next((i for i, label in enumerate(labels) if label in ("condition", "conditions", "test conditions")), None)
    condition = cells[condition_key] if condition_key is not None else ""
    normalize = lambda text: re.sub(r"[\s_]+", "", text).replace("µ", "u").replace("μ", "u")
    return (normalize(need["parameter"]).casefold() in {normalize(cell).casefold() for cell in cells}
            and binding["values"].get(need["role"]) == value
            and (not need.get("condition") or normalize(condition) == normalize(need["condition"])))


def context_turns(result: dict, by_page: dict, *, max_chars: int = 8000) -> list[dict]:
    """固定保守策略:每个行绑定所在页全文补读(只读索引),双方等同,不使用gold页。"""
    turns = []
    pages = sorted({(binding["source"]["file"], binding["source"]["page"]) for binding in result.get("bindings", [])})
    for file, page in pages:
        text = "\n".join(row["text"] for row in by_page[(file, page)])
        for start in range(0, len(text), max_chars):
            turns.append({"stage": "indexed_page_context", "file": file, "page": page,
                          "start_offset": start, "text": text[start:start+max_chars],
                          "truncated": start+max_chars < len(text), "basis": "indexed_text_not_live_pdf"})
    return turns


def evaluate(data, table, rows, variant="baseline"):
    records = []
    by_page = {}
    metadata = {row["file"]: row["md5"] for row in rows}
    for row in rows:
        by_page.setdefault((row["file"], row["page"] + 1), []).append(row)
    for q in data["questions"]:
        start = time.perf_counter()
        diagnostics = {}
        if variant == "baseline":
            from backend.evidence_probe import _api_hits
            hits = _api_hits(retrieval.search(table, q["query"], mode="fts", rerank=False,
                                    structured=True, diagnostics=diagnostics))
            result = {"results": hits, "degraded": diagnostics.get("degraded", [])}
            turns = [result]
        else:
            from backend import evidence_probe
            result = evidence_probe.run(table, q["query"], model=q["model"],
                source_terms=q["source_terms"], revision=q["revision"], needs=q["needs"],
                refill=variant in ("refill", "compact"), compact=variant == "compact", bind=variant != "source")
            hits = result["results"]
            turns = result.pop("_turns")
        page_coverage, snippet_coverage, content_pages, content_snippets = [], [], [], []
        for target in q["targets"]:
            matching = [hit for hit in hits if hit["file"] == target["file"] and hit["page"] == target["page"]]
            aliases = [hit for hit in hits if metadata[hit["file"]] == target["index_md5"] and hit["page"] == target["page"]]
            content_pages.append(any(contains("\n".join(row["text"] for row in by_page[(hit["file"], hit["page"])]), target["required"]) for hit in aliases))
            content_snippets.append(any(contains(hit["snippet"], target["required"]) for hit in aliases))
            page_coverage.append(any(contains("\n".join(row["text"] for row in by_page[(hit["file"], hit["page"])]), target["required"]) for hit in matching))
            snippet_coverage.append(any(contains(hit["snippet"], target["required"]) for hit in matching))
        measurements = [size(turn) for turn in turns]
        contexts = context_turns(result, by_page)
        verified_measurements = measurements + [size(turn) for turn in contexts]
        def cumulative(values):
            return sum(sum(m["bytes"] for m in values[:i+1]) for i in range(len(values)))
        # 固定模拟:一次决策前携带全部既有工具响应,累加前缀,不冒充真实Agent调用。
        records.append({"id": q["id"], "page_covered": sum(page_coverage), "snippet_covered": sum(snippet_coverage),
            "content_page_covered": sum(content_pages), "content_snippet_covered": sum(content_snippets),
            "targets": len(q["targets"]), "all_pages": bool(page_coverage) and all(page_coverage),
            "negative": q["negative"], "status": result.get("status", "retrieved"),
            "source": result.get("source", {}),
            "wrong_source_hits": (sum(metadata[hit["file"]] not in {target["index_md5"] for target in q["targets"]}
                                      for hit in hits) if q["id"].startswith("S") and q["targets"] else None),
            "different_file_hits": (sum(hit["file"] not in {target["file"] for target in q["targets"]}
                                      for hit in hits) if q["id"].startswith("S") and q["targets"] else None),
            "bindings": result.get("bindings", []), "missing": result.get("missing", []),
            "binding_count": len(result.get("bindings", [])),
            "invalid_bindings": sum(not binding_valid(item, q["needs"][item["need"]], rows)
                                    for item in result.get("bindings", [])),
            "negative_bindings": len(result.get("bindings", [])) if q["negative"] else 0,
            "calls": len(turns), "response_bytes": sum(m["bytes"] for m in measurements),
            "response_chars": sum(m["chars"] for m in measurements),
            "lexical_units_proxy": sum(m["lexical_units_proxy"] for m in measurements),
            "cumulative_input_bytes_proxy": cumulative(measurements),
            "with_context_calls": len(verified_measurements),
            "with_context_response_bytes": sum(m["bytes"] for m in verified_measurements),
            "with_context_cumulative_bytes_proxy": cumulative(verified_measurements),
            "elapsed_ms": (time.perf_counter() - start) * 1000,
            "degraded": result.get("degraded", []),
            "hits": [{"file": h["file"], "page": h["page"]} for h in hits]})
    total = sum(record["targets"] for record in records)
    summary = {"questions": len(records), "targets": total, "variant": variant,
        "page_coverage": sum(r["page_covered"] for r in records) / total,
        "snippet_coverage": sum(r["snippet_covered"] for r in records) / total,
        "same_bytes_page_coverage": sum(r["content_page_covered"] for r in records) / total,
        "same_bytes_snippet_coverage": sum(r["content_snippet_covered"] for r in records) / total,
        "wrong_source_hits": sum(r["wrong_source_hits"] or 0 for r in records),
        "positive_questions_all_pages": sum(r["all_pages"] for r in records),
        "degraded_queries": sum(bool(r["degraded"]) for r in records),
        "response_bytes": sum(r["response_bytes"] for r in records),
        "cumulative_input_bytes_proxy": sum(r["cumulative_input_bytes_proxy"] for r in records),
        "with_context_calls": sum(r["with_context_calls"] for r in records),
        "with_context_response_bytes": sum(r["with_context_response_bytes"] for r in records),
        "with_context_cumulative_bytes_proxy": sum(r["with_context_cumulative_bytes_proxy"] for r in records),
        "tool_calls": sum(r["calls"] for r in records),
        "binding_count": sum(r["binding_count"] for r in records),
        "invalid_bindings": sum(r["invalid_bindings"] for r in records),
        "negative_bindings": sum(r["negative_bindings"] for r in records),
        "token_metric": "unavailable: no target-model tokenizer; bytes/chars/lexical units only"}
    return {"summary": summary, "records": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("baseline", "source", "binding", "refill", "compact"), default="baseline")
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()
    block_network()
    config.override_local({"query_cache_ttl": 0})
    data = json.loads(DATASET.read_text())
    table = library.get_table()
    rows = library.scan_columns(table, ["uid", "file", "page", "text", "md5", "model_no", "title", "version", "category", "c_id"])
    validate(data, rows)
    result = evaluate(data, table, rows, args.variant)
    result["dataset_sha256"] = hashlib.sha256(DATASET.read_bytes()).hexdigest()
    result["implementation_sha256"] = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in ("backend/evidence_probe.py", "backend/retrieval.py", "backend/table_facts.py",
                     "tools/eval_evidence_efficiency.py")}
    result["index"] = {"version": int(table.version), "rows": len(rows), "files": len({r["file"] for r in rows}),
        "sources_sha256": hashlib.sha256(json.dumps(sorted({(r["file"], r["md5"]) for r in rows}),
                                                    ensure_ascii=False).encode()).hexdigest()}
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
