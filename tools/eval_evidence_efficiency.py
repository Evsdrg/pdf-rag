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


def evaluate(data, table, rows, variant="baseline"):
    records = []
    by_page = {}
    for row in rows:
        by_page.setdefault((row["file"], row["page"] + 1), []).append(row)
    for q in data["questions"]:
        start = time.perf_counter()
        diagnostics = {}
        if variant == "baseline":
            hits = retrieval.search(table, q["query"], mode="fts", rerank=False,
                                    structured=True, diagnostics=diagnostics)
            result = {"results": hits, "degraded": diagnostics.get("degraded", [])}
            turns = [result]
        else:
            from backend import evidence_probe
            result = evidence_probe.run(table, q["query"], model=q["model"],
                source_terms=q["source_terms"], revision=q["revision"], needs=q["needs"],
                refill=variant in ("refill", "compact"), compact=variant == "compact", bind=variant != "source")
            hits = result["results"]
            turns = result.pop("_turns")
        page_coverage, snippet_coverage = [], []
        for target in q["targets"]:
            matching = [hit for hit in hits if hit["file"] == target["file"] and hit["page"] == target["page"]]
            page_coverage.append(any(contains("\n".join(row["text"] for row in by_page[(hit["file"], hit["page"])]), target["required"]) for hit in matching))
            snippet_coverage.append(any(contains(hit["snippet"], target["required"]) for hit in matching))
        measurements = [size(turn) for turn in turns]
        # 固定模拟:一次决策前携带全部既有工具响应,累加前缀,不冒充真实Agent调用。
        records.append({"id": q["id"], "page_covered": sum(page_coverage), "snippet_covered": sum(snippet_coverage),
            "targets": len(q["targets"]), "all_pages": bool(page_coverage) and all(page_coverage),
            "negative": q["negative"], "status": result.get("status", "retrieved"),
            "bindings": result.get("bindings", []), "missing": result.get("missing", []),
            "calls": len(turns), "response_bytes": sum(m["bytes"] for m in measurements),
            "response_chars": sum(m["chars"] for m in measurements),
            "lexical_units_proxy": sum(m["lexical_units_proxy"] for m in measurements),
            "cumulative_input_bytes_proxy": sum(sum(m["bytes"] for m in measurements[:i+1]) for i in range(len(measurements))),
            "elapsed_ms": (time.perf_counter() - start) * 1000,
            "degraded": result.get("degraded", []),
            "hits": [{"file": h["file"], "page": h["page"]} for h in hits]})
    total = sum(record["targets"] for record in records)
    summary = {"questions": len(records), "targets": total, "variant": variant,
        "page_coverage": sum(r["page_covered"] for r in records) / total,
        "snippet_coverage": sum(r["snippet_covered"] for r in records) / total,
        "positive_questions_all_pages": sum(r["all_pages"] for r in records),
        "degraded_queries": sum(bool(r["degraded"]) for r in records),
        "response_bytes": sum(r["response_bytes"] for r in records),
        "cumulative_input_bytes_proxy": sum(r["cumulative_input_bytes_proxy"] for r in records),
        "tool_calls": sum(r["calls"] for r in records),
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
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
