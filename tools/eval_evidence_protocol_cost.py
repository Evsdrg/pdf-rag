"""补测证据原型的正式序列化/游标与详情成本;不注册新工具、不调用模型。"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend import agent_api, agent_documents, agent_paging, config, evidence_probe, library
from tools.eval_relations import block_network
from tools.eval_evidence_efficiency import DATASET, validate


class IndexedReader:
    """仅替换正文来源;分页/校验/游标使用真实agent_documents.read实现。"""
    def __init__(self, file, rows, version):
        self.file = file
        self.pages = {}
        for row in rows:
            if row["file"] == file:
                self.pages.setdefault(row["page"] + 1, []).append(row["text"])
        self.total = max(self.pages, default=0)
        self.revision = agent_paging.fingerprint((file, version))
        self.kind, self.basis = "pdf", "physical"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def base(self):
        return agent_api.response(file=self.file, kind=self.kind, page_basis=self.basis, total_pages=self.total)

    def page(self, number):
        if number not in self.pages:
            raise agent_documents.page_error(number, self.total)
        return {"text": "\n".join(self.pages[number]), "ocr": False,
                "warnings": [{"code": "INDEX_REPLAY", "message": "仅回放索引文本,非实时PDF提取"}]}


def packet_entries(payload):
    """模拟研究原型的传输适配器,不声称现有MCP已提供此工具。"""
    metadata = {key: value for key, value in payload.items() if key not in ("results", "bindings")}
    return ([{"kind": "metadata", "value": metadata}]
            + [{"kind": "hit", "value": hit} for hit in payload.get("results", [])]
            + [{"kind": "binding", "value": item} for item in payload.get("bindings", [])])


def packet_events(payload, *, scope, revision):
    items = packet_entries(payload)
    events, seen, cursor = [], [], ""
    while True:
        request = {"tool": "offline_evidence_packet", "arguments": {"scope": scope, "cursor": cursor}}
        response = agent_paging.bounded_items(items, "entries", agent_api.response(experimental=True),
                                              scope, revision, 100, cursor)
        assert agent_paging.json_size(response) <= agent_paging.MAX_RESPONSE_BYTES
        events.append({"request": request, "response": response})
        seen.extend(response["entries"])
        cursor = response["next_cursor"]
        if not cursor:
            break
    assert seen == items
    return events


def read_events(file, page):
    events, text, cursor, offset = [], "", "", 0
    while True:
        args = {"file": file, "page": page, "max_chars": 8000, "cursor": cursor}
        response = agent_api.read_page(**args)
        assert agent_paging.json_size(response) <= agent_paging.MAX_RESPONSE_BYTES
        assert response["start_offset"] == offset
        text += response["text"]
        offset = response["end_offset"]
        events.append({"request": {"tool": "pdf_rag_read_page", "arguments": args}, "response": response})
        cursor = response["next_cursor"]
        if not cursor:
            break
    return events, text


def transcript_cost(events, task):
    """固定每次工具调用后由模型决策,计所有请求+响应历史;非真实模型token。"""
    history = agent_paging.json_size(task)
    cumulative, requests, responses = 0, 0, 0
    for event in events:
        request = agent_paging.json_size(event["request"])
        response = agent_paging.json_size(event["response"])
        assert response <= agent_paging.MAX_RESPONSE_BYTES
        requests += request
        responses += response
        history += request + response
        cumulative += history
    return {"calls": len(events), "request_bytes": requests, "response_bytes": responses,
            "cumulative_input_bytes_proxy": cumulative}


def compact_formal(payload):
    # 只用原型已验证的逐命中字段裁减;身份/告警/降级/裁尾字段保持原样。
    return evidence_probe.compact_payload(payload)


def evaluate(data, table, rows):
    records = []
    version = table.version
    pages = {}
    for row in rows:
        pages.setdefault((row["file"], row["page"] + 1), []).append(row["text"])
    reader_factory = lambda file: IndexedReader(file, rows, version)
    with patch.object(agent_documents, "Reader", side_effect=reader_factory):
        for q in data["questions"]:
            result = evidence_probe.run(table, q["query"], model=q["model"],
                source_terms=q["source_terms"], revision=q["revision"], needs=q["needs"], refill=True)
            turns = result.pop("_turns")
            source = result["source"]
            formal = None
            if source["status"] == "resolved":
                args = {"query": q["query"], "file": source["files"][0], "mode": "fts",
                        "rerank": False, "structured": True, "top_k": 5}
                formal = agent_api.search(**args)
                assert not formal["degraded"]
                # 正式协议裁尾不能被原型隐藏;本批次若裁尾,停止而不是拿不可见证据算成功。
                assert not formal["truncated"], q["id"]
                assert [(h["file"], h["page"], h["snippet"]) for h in formal["results"]] == [
                    (h["file"], h["page"], h["snippet"]) for h in turns[0]["results"]], q["id"]
                formal_event = {"request": {"tool": "pdf_rag_search", "arguments": args}, "response": formal}
                compact_event = {**formal_event, "response": compact_formal(formal)}
                full_events, lean_events = [formal_event], [compact_event]
                # 原型绑定/未解决状态单独计入实验包,不冒充现有search字段。
                initial = {key: value for key, value in turns[0].items() if key != "results"}
                full_events += packet_events(initial, scope=(q["id"], "binding"), revision=str(version))
                lean_events += packet_events(initial, scope=(q["id"], "binding"), revision=str(version))
            else:
                full_events = packet_events(turns[0], scope=(q["id"], "source"), revision=str(version))
                lean_events = list(full_events)
            for index, turn in enumerate(turns[1:], 1):
                full_events += packet_events(turn, scope=(q["id"], "refill", index, "full"), revision=str(version))
                lean_events += packet_events(compact_formal(turn), scope=(q["id"], "refill", index, "compact"), revision=str(version))
            read_pages = sorted({(binding["source"]["file"], binding["source"]["page"])
                                 for binding in result["bindings"]})
            context_events = []
            for file, page in read_pages:
                events, text = read_events(file, page)
                assert text == "\n".join(pages[(file, page)])
                context_events += events
            task = {key: q[key] for key in ("query", "model", "source_terms", "revision", "needs")}
            full_with_context, lean_with_context = full_events + context_events, lean_events + context_events
            detail_events = []
            if formal:
                # 按需取完整详情的保守策略:重发完整已输出证据包,重复内容成本也算进去。
                for index, turn in enumerate(turns):
                    detail_events += packet_events(turn, scope=(q["id"], "details", index), revision=str(version))
            stable_formal = None
            if formal:
                stable_formal = {key: value for key, value in formal.items()
                                 if key not in ("timings_ms", "upstream")}
                stable_formal["structured"] = {key: value for key, value in formal["structured"].items()
                                                if key not in ("index_build_ms", "index_load_ms", "index_cached",
                                                               "index_source")}
            record = {"id": q["id"], "source_status": source["status"], "bindings": len(result["bindings"]),
                "formal_index_build_ms": (formal or {}).get("structured", {}).get("index_build_ms"),
                "stable_formal_signature": agent_paging.fingerprint(stable_formal),
                "binding_signature": agent_paging.fingerprint((result["bindings"], result["missing"], result["source"])),
                "missing": result["missing"],
                "context_signature": agent_paging.fingerprint([event["response"]["text"] for event in context_events]),
                "formal_stable_bytes": agent_paging.json_size(stable_formal) if formal else 0,
                "formal_search_bytes": agent_paging.json_size(formal) if formal else 0,
                "max_response_bytes": max(agent_paging.json_size(event["response"])
                                           for event in full_with_context + lean_with_context + detail_events),
                "full": transcript_cost(full_with_context, task),
                "compact": transcript_cost(lean_with_context, task),
                "compact_with_details": transcript_cost(lean_events + detail_events + context_events, task),
                "semantic_signature": agent_paging.fingerprint([(h["file"], h["page"], h["snippet"]) for h in result["results"]])}
            records.append(record)
    summary = {}
    for rate in (0, 25, 50, 100):
        # 确定性前缀子集,只是敏感性情境,不声称是真实用户取详情概率。
        selected = {record["id"] for record in records[:len(records) * rate // 100]}
        total = {key: 0 for key in records[0]["full"]}
        for record in records:
            cost = record["compact_with_details"] if record["id"] in selected else record["compact"]
            for key in total:
                total[key] += cost[key]
        summary[f"compact_details_{rate}pct"] = total
    summary["full"] = {key: sum(record["full"][key] for record in records) for key in records[0]["full"]}
    weighted = {}
    for rate in (0, 25, 50, 100):
        fraction = rate / 100
        weighted[str(rate)] = {key: sum((1-fraction) * record["compact"][key]
                                      + fraction * record["compact_with_details"][key] for record in records)
                              for key in records[0]["full"]}
    summary["uniform_details_expected_cost"] = weighted
    return {"summary": summary, "records": records,
            "limitations": ["existing search/read functions, experimental packet adapter not a deployed API",
                            "indexed Reader replaces PDF extraction only; pagination and cursors use real functions",
                            "details rates are deterministic scenarios, not real agent decisions",
                            "bytes include explicit request/task history, not model framing/reasoning or actual tokens"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()
    block_network()
    config.override_local({"query_cache_ttl": 0})
    data = json.loads(DATASET.read_text())
    table = library.get_table()
    rows = library.scan_columns(table, ["uid", "file", "page", "text", "md5", "model_no", "title", "version", "category", "c_id"])
    validate(data, rows)
    result = evaluate(data, table, rows)
    result["dataset_sha256"] = hashlib.sha256(DATASET.read_bytes()).hexdigest()
    result["index"] = {"version": int(table.version), "rows": len(rows)}
    result["implementation_sha256"] = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in ("tools/eval_evidence_protocol_cost.py", "backend/evidence_probe.py", "backend/agent_api.py",
                     "backend/agent_documents.py", "backend/agent_paging.py")}
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
