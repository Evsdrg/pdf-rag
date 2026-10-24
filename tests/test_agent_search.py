"""空召回不等于通道故障;精确查找只合并确定性重复。"""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pyarrow as pa

from backend import agent_api, agent_grep, library, retrieval, vecstore
from tests.support import override_config


def row(text, uid="uid", page=0):
    return {"uid": uid, "file": "cat/QMC6309.pdf", "page": page, "text": text,
            "category": "cat", "model_no": "QMC6309", "c_id": "", "version": ""}


class DiagnosticsTest(unittest.TestCase):
    def tearDown(self):
        retrieval.reset_cache()

    def test_empty_degraded_result_still_has_notice(self):
        def fail(*args):
            args[-1].append("fts")
        diagnostics = {}
        with patch.object(retrieval, "_channel_fts", side_effect=fail), patch.object(retrieval, "_channel_substring"):
            result = retrieval.search(SimpleNamespace(version=1), "voltage", mode="fts", diagnostics=diagnostics)
        self.assertEqual(result, [])
        self.assertIn("全文", diagnostics["notice"])
        self.assertEqual(diagnostics["warnings"][0]["code"], "FTS")

    def test_successful_zero_vector_hits_is_not_degraded(self):
        part = MagicMock()
        part.schema.field.return_value.type.list_size = 3
        part.search.return_value.limit.return_value.to_list.return_value = []
        degraded, diagnostics = [], {}
        with patch.object(library, "get_db", return_value=object()), \
             patch.object(vecstore, "select_partitions", return_value=[{"slug": "sample", "dim": 3}]), \
             patch.object(vecstore, "open_partition", return_value=part), \
             patch.object(vecstore, "has_vector_index", return_value=False), \
             patch.object(retrieval, "embed_query", return_value=[1, 2, 3]), \
             override_config(vector_coverage_min=0):
            retrieval._channel_vector(object(), "query", 20, None, None,
                                      retrieval._Candidates(60, 5), degraded, diagnostics)
        self.assertEqual(degraded, [])
        self.assertEqual(diagnostics["vector_partitions"], ["sample"])

    def test_category_error_happens_before_model_call(self):
        with patch.object(library, "get_table", return_value=object()), \
             patch.object(library, "categories", return_value=["cat"]), \
             patch.object(retrieval, "search", side_effect=AssertionError("should not query")):
            result, _ = agent_api.invoke(agent_api.search, "query", category="missing")
        self.assertEqual(result["error"]["code"], "CATEGORY_NOT_FOUND")

    def test_identity_warning_not_a_probability_or_filter(self):
        identities, warnings = agent_api._identity("ZXQ999999 供电", [row("voltage")])
        self.assertEqual(identities[0]["status"], "unconfirmed")
        self.assertEqual(warnings[0]["code"], "MODEL_IDENTITY_UNCONFIRMED")
        self.assertEqual(agent_api._identity("I2C V1.2 100MHz", [row("text")]), ([], []))
        for query in ("SPI2 时序", "GPIO12 配置", "UART3 初始化", "ADC1 采样"):
            self.assertEqual(agent_api._identity(query, [row("text")]), ([], []))

    def test_cached_diagnostics_preserve_partitions(self):
        def add(table, query, limit, category, file, candidates, degraded, diagnostics):
            candidates.add(row("supply voltage"), 0)
            diagnostics["vector_partitions"] = ["part"]
        with patch.object(retrieval, "_channel_vector", side_effect=add), \
             override_config(query_cache_ttl=600, query_cache_size=10):
            first, second = {}, {}
            table = SimpleNamespace(version=1)
            retrieval.search(table, "voltage", mode="vector", rerank=False, diagnostics=first)
            retrieval.search(table, "voltage", mode="vector", rerank=False, diagnostics=second)
        self.assertTrue(second["cached"])
        self.assertEqual(first["vector_partitions"], second["vector_partitions"])
        self.assertEqual(second["warnings"], [])


class GrepTest(unittest.TestCase):
    def run_grep(self, rows, **kwargs):
        table = SimpleNamespace(version=1)
        with patch.object(library, "scan_arrow", return_value=pa.Table.from_pylist(rows)):
            return agent_grep.grep(table, "VDD", "", "", kwargs.get("max_hits", 20),
                                   kwargs.get("context", 60), True, kwargs.get("cursor", ""))

    def test_exact_table_duplicate_is_collapsed_but_conditions_remain(self):
        rows = [row("VDD 2.5 V", "a"), row("| VDD | 2.5 V |", "b"),
                row("VDD 3.3 V at 25 C", "c")]
        result = self.run_grep(rows)
        self.assertEqual(result["count"], 1)
        self.assertEqual(len(result["results"][0]["contexts"]), 2)
        self.assertEqual(result["results"][0]["indexed_matches"], 3)
        self.assertNotIn("matches_in_page", result["results"][0])

    def test_unmatched_rows_do_not_create_empty_page_hits(self):
        result = self.run_grep([row("unrelated text", "a"), row("VDD 3.3 V", "b", 1)])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["page"], 2)

    def test_case_and_symbol_differences_are_not_duplicates(self):
        result = self.run_grep([row("VDD 1 mA", "a"), row("VDD 1 MA", "b")])
        self.assertEqual(len(result["results"][0]["contexts"]), 2)

    def test_unicode_regex_and_explicit_separator_class(self):
        table = SimpleNamespace(version=1)
        for pattern, text in ((r"\w+", "电压"), (r"VDD[ _]APC", "VDD APC"), (r"VDD[_ ]APC", "VDD_APC")):
            with patch.object(library, "scan_arrow", return_value=pa.Table.from_pylist([row(text)])):
                result = agent_grep.grep(table, pattern, "", "", 20, 60, True, "")
            self.assertEqual(result["count"], 1)

    def test_multiple_matches_and_page_cursor(self):
        rows = [row("VDD one VDD two", "a"), row("VDD three", "b", 1)]
        first = self.run_grep(rows, max_hits=1, context=3)
        self.assertTrue(first["next_cursor"])
        second = self.run_grep(rows, max_hits=1, context=3, cursor=first["next_cursor"])
        self.assertEqual(second["results"][0]["page"], 2)

    def test_overlapping_windows_merge_but_distant_matches_remain(self):
        rows = [row("VDDIO low VIL; VDDIO high VIH" + "x" * 200 + "VDDIO supply")]
        result = self.run_grep(rows, context=20)
        contexts = result["results"][0]["contexts"]
        self.assertEqual(len(contexts), 2)
        self.assertIn("low VIL", contexts[0]["context"])
        self.assertIn("high VIH", contexts[0]["context"])
        self.assertEqual(contexts[1]["match"], "VDD")
        self.assertFalse(result["results"][0]["contexts_truncated"])

    def test_context_cap_reports_only_omitted_windows(self):
        rows = [row(" ".join(f"VDD parameter{i}" for i in range(8)))]
        result = self.run_grep(rows, context=2)
        item = result["results"][0]
        self.assertEqual(len(item["contexts"]), 5)
        self.assertEqual(item["omitted_contexts"], 3)
        self.assertTrue(item["contexts_truncated"])

    def test_duplicate_after_cap_is_not_counted_as_another_omission(self):
        texts = ["VDD alpha", "VDD beta", "VDD gamma", "VDD delta", "VDD epsilon", "VDD zeta"]
        rows = [row(text, f"chunk{i}") for i, text in enumerate(texts)]
        rows.append(row(texts[0], "duplicate-of-first"))
        result = self.run_grep(rows, context=2)
        item = result["results"][0]
        self.assertEqual(len(item["contexts"]), 5)
        self.assertEqual(item["omitted_contexts"], 1)
        self.assertNotIn("seen", item)


if __name__ == "__main__":
    unittest.main()
