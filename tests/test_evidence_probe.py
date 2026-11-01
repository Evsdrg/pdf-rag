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


if __name__ == "__main__":
    unittest.main()
