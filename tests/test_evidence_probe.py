"""证据原型的关键负例,不复制手册全文、不联网。"""
import unittest
from unittest.mock import patch

from backend import evidence_probe


class SourceTest(unittest.TestCase):
    def rows(self):
        return [dict(file="A.pdf", page=0, model_no="ABC123", title="manual", version="A", md5="a", text="VendorOne Revision A"),
                dict(file="B.pdf", page=0, model_no="ABC123", title="manual", version="D", md5="b", text="VendorTwo Revision D")]

    def test_literal_source_and_revision_resolve_without_latest_guessing(self):
        with patch.object(evidence_probe.library, "scan_columns", return_value=self.rows()):
            chosen = evidence_probe.select_sources(object(), "ABC123", ["VendorOne"], "A")
            wrong = evidence_probe.select_sources(object(), "ABC123", ["VendorOne"], "D")
            unknown = evidence_probe.select_sources(object(), "ABC123", ["Unknown"])
            ambiguous = evidence_probe.select_sources(object(), "ABC123")
        self.assertEqual(chosen.files, ("A.pdf",))
        self.assertEqual(wrong.status, "not_found")
        self.assertEqual(unknown.status, "not_found")
        self.assertEqual(ambiguous.status, "ambiguous")

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


if __name__ == "__main__":
    unittest.main()
