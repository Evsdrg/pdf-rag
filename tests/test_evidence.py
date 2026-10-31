"""结构化证据包与重排输入使用相同原文窗口。"""
import unittest
from unittest.mock import patch

from backend import evidence, retrieval
from tests.support import override_config


def row(uid, text):
    return {"uid": uid, "text": text, "md5": "hash", "file": "part.pdf", "page": 1,
            "model_no": "ABC123", "category": "cat", "c_id": ""}


class EvidenceTest(unittest.TestCase):
    def test_cross_chunk_bundle_is_identical_to_rerank_content(self):
        chunks = [row("header", "ABC123 overview"), row("voltage", "Supply voltage 3.3 V"),
                  row("current", "Supply current 0.45 mA")]
        key = ("part.pdf", 1)
        cands = retrieval._Candidates(60, 5)
        for rank, chunk in enumerate(chunks):
            cands.add(chunk, rank)
        with override_config(rerank_on_window=True, rerank_meta=False):
            bundle = evidence.select(chunks, "supply voltage current")
            docs = retrieval._rerank_docs(cands.top(5), cands.rows, "supply voltage current", {key: bundle})
            hits = retrieval._build_results(cands.top(5), cands, {}, "supply voltage current", 5, 0, {key: bundle})
        self.assertEqual(docs, [hits[0]["snippet"]])
        self.assertEqual(len(hits[0]["evidence_refs"]), 2)
        self.assertIn("3.3 V", hits[0]["snippet"])
        self.assertIn("0.45 mA", hits[0]["snippet"])
        by_uid = {chunk["uid"]: chunk for chunk in chunks}
        for ref in hits[0]["evidence_refs"]:
            text = by_uid[ref["chunk_id"]]["text"]
            self.assertEqual(bundle["text"][ref["snippet_start"]:ref["snippet_end"]],
                             text[ref["start_offset"]:ref["end_offset"]])

    def test_duplicate_chunks_do_not_consume_second_window(self):
        chunks = [row("a", "Supply voltage 3.3 V"), row("a", "Supply voltage 3.3 V"),
                  row("b", "Supply voltage 3.3 V"), row("c", "Supply current 2 mA")]
        bundle = evidence.select(chunks, "supply voltage current")
        self.assertEqual(len(bundle["references"]), 2)
        self.assertIn("Supply current", bundle["text"])

    def test_header_from_unrelated_previous_table_is_not_inherited(self):
        old = "| Parameter | Value |\n| --- | --- |\n| Old | 1 V |\n\nUnrelated section\n"
        self.assertIsNone(evidence._table_header(old, len(old)))
        active = "| Parameter | Value |\n| --- | --- |\n| VDD | 3.3 V |\n"
        self.assertIn("Parameter", evidence._table_header(active, active.index("| VDD")))
        separate = active + "\n| detached row | 1 mA |\n"
        self.assertIsNone(evidence._table_header(separate, separate.index("| detached")))

    def test_two_windows_share_existing_text_budget(self):
        chunks = [row("a", "voltage 3.3 V\n" * 100), row("b", "current 2 mA\n" * 100)]
        with override_config(snippet_width=200):
            bundle = evidence.select(chunks, "voltage current")
        self.assertLessEqual(len(bundle["text"]), 200)
        self.assertEqual(len(bundle["references"]), 2)

    def test_structured_facts_keep_row_conditions_and_index_references(self):
        text = ("| Parameter | Symbol | Conditions | Unit | Value |\n|---|---|---|---|---|\n"
                "| Supply Current | IDD | mode=low | mA | 0.45 |\n"
                "| Supply Current | IDD | mode=high | mA | 1.20 |\n")
        chunk = row("table", text)
        key = ("part.pdf", 1)
        cands = retrieval._Candidates(60, 5)
        cands.add(chunk, 0)
        bundle = evidence.select([chunk], "ABC123 电流")
        result = retrieval._build_results(cands.top(5), cands, {}, "ABC123 电流", 5, 0, {key: bundle})
        facts = result[0]["structured_facts"]
        self.assertEqual(len(facts), 2)
        self.assertEqual({fact["conditions"] for fact in facts}, {"mode=low", "mode=high"})
        for fact in facts:
            ref = fact["source"]
            self.assertEqual(ref["file"], "part.pdf")
            self.assertEqual(ref["page"], 2)
            self.assertIn(fact["conditions"], text[ref["start_offset"]:ref["end_offset"]])

    def test_nonwindow_rerank_setting_remains_explicit(self):
        chunk = row("a", "full text")
        with override_config(rerank_on_window=False, rerank_meta=False):
            docs = retrieval._rerank_docs([(("part.pdf", 1), 1)], {("part.pdf", 1): chunk},
                                          "voltage", {("part.pdf", 1): {"text": "selected"}})
        self.assertEqual(docs, ["full text"])


if __name__ == "__main__":
    unittest.main()
