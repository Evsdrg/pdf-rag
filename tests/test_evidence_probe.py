"""证据原型的关键负例,不复制手册全文、不联网。"""
import unittest
from unittest.mock import patch

from backend import evidence_probe


class SourceTest(unittest.TestCase):
    def rows(self):
        return [dict(file="A.pdf", page=0, model_no="ABC123", title="manual", version="A", md5="a", text="VendorOne Revision A"),
                dict(file="B.pdf", page=0, model_no="ABC123", title="manual", version="D", md5="b", text="VendorTwo Revision D")]

    def scan(self, table, columns):
        return [{key: row[key] for key in columns} for row in self.rows()]

    def table(self):
        from unittest.mock import MagicMock
        table = MagicMock()
        table.count_rows.return_value = 2
        query = table.search.return_value
        query.where.side_effect = lambda clause: self._front(clause)
        return table

    def _front(self, clause):
        from unittest.mock import MagicMock
        result = MagicMock()
        file = clause.split("file = '", 1)[1].split("'", 1)[0]
        result.select.return_value.limit.return_value.to_list.return_value = [
            {"text": row["text"]} for row in self.rows() if row["file"] == file]
        return result

    def test_literal_source_and_revision_resolve_without_latest_guessing(self):
        with patch.object(evidence_probe.library, "scan_columns", side_effect=self.scan):
            chosen = evidence_probe.select_sources(self.table(), "ABC123", ["VendorOne"], "A")
            wrong = evidence_probe.select_sources(self.table(), "ABC123", ["VendorOne"], "D")
            unknown = evidence_probe.select_sources(self.table(), "ABC123", ["Unknown"])
            ambiguous = evidence_probe.select_sources(self.table(), "ABC123")
        self.assertEqual(chosen.files, ("A.pdf",))
        self.assertEqual(wrong.status, "not_found")
        self.assertEqual(unknown.status, "not_found")
        self.assertEqual(ambiguous.status, "ambiguous")

    def test_revision_history_cannot_override_explicit_current_revision(self):
        rows = [dict(file="A.pdf", page=0, model_no="ABC123", title="manual", version="D", md5="a",
                     text="Revision D. Changes from Revision A")]
        with patch.object(evidence_probe.library, "scan_columns", return_value=rows), \
             patch.object(self, "rows", return_value=rows):
            chosen = evidence_probe.select_sources(self.table(), "ABC123", revision="A")
        self.assertEqual(chosen.status, "not_found")

    def test_source_budget_is_explicit_not_empty_result(self):
        table = self.table()
        table.count_rows.return_value = 50_001
        with self.assertRaises(evidence_probe.ProbeLimitError):
            evidence_probe.select_sources(table, "ABC123")

    def test_ambiguous_source_never_triggers_retrieval(self):
        with patch.object(evidence_probe.library, "scan_columns", return_value=self.rows()), \
             patch.object(evidence_probe.retrieval, "search", side_effect=AssertionError("not resolved")):
            result = evidence_probe.run(object(), "ABC123 voltage", model="ABC123")
        self.assertEqual(result["results"], [])
        self.assertEqual(result["status"], "ambiguous")


class BindingTest(unittest.TestCase):
    def row(self):
        text = ("Common conditions: TA=25°C\n\n| Parameter | Unit | Conditions | Min | Typ | Max |\n"
                "|---|---|---|---|---|---|\n| Voltage | V | mode=low | 1 | 2 | 3 |\n"
                "| Voltage | V | mode=high | 4 | 5 | 6 |\n"
                "| Current | mA | I=1mA | - | 2 | - |\n")
        return {"uid": "a", "file": "A.pdf", "page": 0, "md5": "m", "model_no": "ABC123", "text": text}

    def test_role_and_condition_are_bound_to_same_row(self):
        row = self.row()
        bindings, missing = evidence_probe.bind_rows([row], [{"parameter": "Voltage", "role": "max", "condition": "mode=low"}])
        self.assertEqual(missing, [])
        self.assertEqual(bindings[0]["values"]["max"], "3")
        self.assertEqual(bindings[0]["context_status"], "requires_page_context")
        reference = bindings[0]["source"]
        self.assertIn("mode=low", row["text"][reference["start_offset"]:reference["end_offset"]])

    def test_wrong_condition_role_units_and_ambiguous_rows_remain_missing(self):
        for need in ({"parameter": "Voltage", "role": "typ"},
                     {"parameter": "Voltage", "role": "max", "condition": "mode=unknown"},
                     {"parameter": "Current", "role": "max", "condition": "I=1mA"},
                     {"parameter": "Current", "role": "typ", "condition": "I=1MA"}):
            with self.subTest(need=need):
                bindings, missing = evidence_probe.bind_rows([self.row()], [need])
                self.assertEqual(bindings, [])
                self.assertEqual(missing, [0])


class RefillTest(unittest.TestCase):
    def test_only_missing_needs_are_queried_with_a_hard_call_budget(self):
        selected = evidence_probe.SourceSelection("resolved", ("A.pdf",), ("A.pdf",), "literal")
        needs = [{"parameter": f"p{i}", "role": "max"} for i in range(6)]
        with patch.object(evidence_probe, "select_sources", return_value=selected), \
             patch.object(evidence_probe.retrieval, "search", return_value=[]), \
             patch.object(evidence_probe, "_hit_rows", return_value=[]), \
             patch.object(evidence_probe, "_supplement", return_value=[]) as supplement:
            result = evidence_probe.run(object(), "ABC123", model="ABC123", needs=needs, refill=True)
        self.assertEqual(supplement.call_count, 3)
        self.assertEqual(result["missing"], list(range(6)))
        self.assertEqual(len(result["_turns"]), 4)
        self.assertEqual([call.args[2]["parameter"] for call in supplement.call_args_list], ["p0", "p1", "p2"])


class CompactTest(unittest.TestCase):
    def test_compaction_keeps_full_text_references_conditions_and_missing(self):
        hit = {"file": "A.pdf", "page": 1, "model_no": "ABC123", "snippet": "Value 3 V at mode=low",
               "snippet_ref": {"chunk_id": "u", "start_offset": 0, "end_offset": 24, "text": "Value 3 V at mode=low"},
               "retrieval_trace": {"kind": "entity_direct"}, "structured_facts": [{"conditions": "mode=low"}], "score": 1}
        binding = {"conditions": "mode=low", "values": {"max": "3"}, "context_status": "requires_page_context"}
        payload = {"results": [hit], "bindings": [binding], "missing": [2], "degraded": ["fts"]}
        out = evidence_probe.compact_payload(payload)
        self.assertEqual(out["results"][0]["snippet"], hit["snippet"])
        self.assertEqual(out["bindings"], [binding])
        self.assertEqual(out["missing"], [2])
        self.assertEqual(out["degraded"], ["fts"])
        self.assertEqual(out["results"][0]["snippet_ref"]["chunk_id"], "u")
        self.assertIn("text", payload["results"][0]["snippet_ref"])
        self.assertNotIn("text", out["results"][0]["snippet_ref"])
        hit["snippet_ref"]["text"] += " Extra condition"
        out = evidence_probe.compact_payload(payload)
        self.assertIn("Extra condition", out["results"][0]["snippet_ref"]["text"])


if __name__ == "__main__":
    unittest.main()
