"""正式序列化预算、补充研究包及详情情境的离线验收。"""
import unittest
from unittest.mock import patch

from backend import agent_api, agent_documents, agent_paging, evidence_probe, library
from tools import eval_evidence_protocol_cost as evaluator


class ProtocolCostTest(unittest.TestCase):
    def test_packet_cursors_preserve_every_record_and_bind_scope_and_version(self):
        hits = [{"file": f"{i}.pdf", "page": 1, "model_no": "ABC123", "snippet": "证据条件\"\\" * 300}
                for i in range(25)]
        payload = {"status": "row_evidence", "results": hits, "bindings": [], "missing": [2]}
        events = evaluator.packet_events(payload, scope=("q1", "full"), revision="v1")
        self.assertGreater(len(events), 1)
        recovered = [entry for event in events for entry in event["response"]["entries"]]
        self.assertEqual(recovered, evaluator.packet_entries(payload))
        self.assertTrue(all(agent_paging.json_size(event["response"]) <= 32000 for event in events))
        cursor = events[0]["response"]["next_cursor"]
        for scope, revision, code in ((("q2", "full"), "v1", "INVALID_CURSOR"),
                                      (("q1", "full"), "v2", "STALE_CURSOR")):
            with self.assertRaises(library.LibraryError) as caught:
                agent_paging.bounded_items([], "entries", {}, scope, revision, 100, cursor)
            self.assertEqual(caught.exception.code, code)

    def test_real_read_api_continuation_reconstructs_same_indexed_text(self):
        text = ("条件/值/单位\"\\\n" * 2500) + "最后的共同条件"
        rows = [{"file": "a.pdf", "page": 0, "text": text}]
        with patch.object(agent_documents, "Reader", side_effect=lambda file: evaluator.IndexedReader(file, rows, 1)):
            events, recovered = evaluator.read_events("a.pdf", 1)
        self.assertEqual(recovered, text)
        self.assertGreater(len(events), 1)
        self.assertTrue(all(event["response"]["schema_version"] == 2 for event in events))
        self.assertTrue(all(agent_paging.json_size(event["response"]) <= 32000 for event in events))

    def test_compact_formal_keeps_warnings_identity_and_truncation(self):
        hit = {"file": "a.pdf", "page": 1, "model_no": "ABC123", "snippet": "value 3 V under mode=low",
               "snippet_ref": {"chunk_id": "u", "start_offset": 0, "end_offset": 25},
               "retrieval_trace": {"kind": "entity_direct"}}
        payload = agent_api.response(results=[hit], warnings=[{"code": "MODEL_IDENTITY_UNCONFIRMED"}],
            identity=[{"status": "unconfirmed"}], degraded=["fts"], truncated=True, omitted_results=2)
        compact = evaluator.compact_formal(payload)
        for key in ("schema_version", "warnings", "identity", "degraded", "truncated", "omitted_results"):
            self.assertEqual(compact[key], payload[key])
        self.assertEqual(compact["results"][0]["snippet"], hit["snippet"])
        self.assertEqual(compact["results"][0]["snippet_ref"], hit["snippet_ref"])

    def test_request_and_extra_details_count_in_cumulative_cost(self):
        event = {"request": {"tool": "lookup", "arguments": {"query": "ABC123"}},
                 "response": {"text": "evidence"}}
        task = {"query": "ABC123 voltage"}
        one = evaluator.transcript_cost([event], task)
        two = evaluator.transcript_cost([event, event], task)
        unit = agent_paging.json_size(event["request"]) + agent_paging.json_size(event["response"])
        self.assertEqual(one["cumulative_input_bytes_proxy"], agent_paging.json_size(task) + unit)
        self.assertEqual(two["cumulative_input_bytes_proxy"], 2 * agent_paging.json_size(task) + 3 * unit)
        self.assertEqual(two["response_bytes"], 2 * one["response_bytes"])

    def test_formal_search_truncation_remains_visible(self):
        hits = [{"file": f"{i}.pdf", "page": 1, "model_no": "ABC123", "snippet": "证据" * 2500}
                for i in range(20)]
        with patch.object(agent_api, "require_table", return_value=object()), \
             patch.object(agent_api, "check_category"), \
             patch.object(agent_api.retrieval, "search", return_value=hits):
            payload = agent_api.search("ABC123", top_k=20, mode="fts", rerank=False)
        compact = evidence_probe.compact_payload(payload)
        self.assertTrue(payload["truncated"])
        self.assertGreater(payload["omitted_results"], 0)
        self.assertEqual(compact["omitted_results"], payload["omitted_results"])
        self.assertLessEqual(agent_paging.json_size(payload), 32000)


if __name__ == "__main__":
    unittest.main()
