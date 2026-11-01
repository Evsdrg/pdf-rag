"""实体桥的身份、证据、预算与降级边界,全部使用本地夹具。"""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pyarrow as pa

from backend import entity, retrieval
from tests.support import override_config


def row(uid, text, *, file="cat/QMC6309.pdf", page=0, model_no="QMC6309", category="cat"):
    return {"uid": uid, "file": file, "page": page, "text": text,
            "category": category, "model_no": model_no, "c_id": "", "version": "", "md5": ""}


def table_for(rows, version=1):
    return SimpleNamespace(version=version, count_rows=lambda: len(rows))


class EntityExtractionTest(unittest.TestCase):
    def test_identity_preserves_suffixes_and_excludes_units_interfaces_versions(self):
        keys = entity.extract_entities("QMI8658A I2C VDD 1.71 V 100MHz UART3 V1.2", query=True)
        self.assertIn("model:qmi8658a", keys)
        self.assertIn("interface:i2c", keys)
        self.assertIn("symbol:vdd", keys)
        self.assertIn("value:1.71V", keys)
        self.assertFalse({"model:v1", "model:uart3", "model:100mhz"}.intersection(keys))
        for model in ("LSM6DS3TR-C", "MPU-9250", "ESP32-C3", "BY25FQ32ELTIG(T)", "AMS1117-3.3V-JSM"):
            keys = entity.extract_entities(model, query=True)
            self.assertIn("model:" + model.casefold(), keys)
        self.assertNotIn("model:lsm6ds3tr", entity.extract_entities("LSM6DS3TR-C", query=True))
        self.assertNotIn("model:v1.2", keys)
        decimal = entity.extract_entities("AMS1117-3.3 供电电压", query=True)
        self.assertIn("model:ams1117-3.3", decimal)
        self.assertNotIn("model:ams1117-3", decimal)

    def test_units_preserve_prefix_case_and_symbols_normalise_separators(self):
        keys = entity.extract_entities("1 mA 1 MA 500 mΩ 500 MΩ VDD_APC")
        self.assertTrue({"value:1mA", "value:1MA", "value:500mΩ", "value:500MΩ"}.issubset(keys))
        spaced = entity.extract_entities("VDD APC 1 µA")
        self.assertIn("symbol:vddapc", spaced)
        self.assertIn("symbol:vddapc", keys)
        self.assertIn("value:1uA", spaced)

    def test_document_text_is_not_a_model_identity_source(self):
        keys = entity.extract_entities("QMI8658A Series HTTP V1.2 UART3 USB2")
        self.assertFalse(any(key.startswith("model:") for key in keys))
        self.assertIn("interface:uart", keys)
        self.assertIn("interface:usb", keys)


class EntityIndexTest(unittest.TestCase):
    def tearDown(self):
        entity.reset_cache()

    def test_exact_model_scope_prevents_cross_variant_expansion(self):
        rows = [row("a", "VDD supply voltage 1.65 V", page=1),
                row("b", "I2C address 0x6a", page=2),
                row("c", "VDD supply voltage 1.65 V", file="cat/QMC6308.pdf", page=3, model_no="QMC6308")]
        table = table_for(rows)
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()):
            result = entity.search(table, "QMC6309 VDD voltage")
        self.assertEqual(result.direct_uids, ("a",))
        self.assertEqual(result.expanded_uids, ())
        self.assertNotIn("c", result.ordered_uids)
        self.assertEqual(rows[0]["model_no"], "QMC6309")

    def test_prefix_fallback_does_not_merge_exact_variants(self):
        rows = [row("a", "I2C address", model_no="QMI8658A"),
                row("b", "I2C address", file="cat/B.pdf", model_no="QMI8658B")]
        table = table_for(rows)
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()):
            exact = entity.search(table, "QMI8658A I2C")
            prefix = entity.search(table, "QMI8658 I2C")
        self.assertEqual(exact.ordered_uids, ("a",))
        self.assertEqual(set(prefix.direct_uids), {"a", "b"})

    def test_filters_apply_before_posting_limit(self):
        rows = [row(str(i), "I2C address", file="other/early.pdf", page=i) for i in range(5)]
        rows.append(row("target", "I2C address", file="cat/Z_100%.pdf", category="target"))
        table = table_for(rows)
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()), \
             patch.object(entity, "MAX_POSTING", 2):
            result = entity.search(table, "I2C address", category="target", file="Z_100%")
            empty = entity.search(table, "I2C address", file="Z-100%")
        self.assertEqual(result.direct_uids, ("target",))
        self.assertEqual(empty.status, "empty")

    def test_original_seeds_require_query_signals_and_ignore_model_headers(self):
        rows = [row("header", "QMC6309 repeated heading", page=1),
                row("seed", "I2C address", page=2),
                row("neighbor", "I2C electrical", page=3),
                row("noise", "marketing material", page=4)]
        table = table_for(rows)
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()):
            result = entity.search(table, "QMC6309 I2C address", limit=2, seed_rows=rows[:2])
            empty_seeds = entity.search(table, "QMC6309 I2C address", limit=2, seed_rows=[])
        self.assertEqual(result.seeds, 1)
        self.assertIn("neighbor", result.expanded_uids)
        self.assertNotIn("noise", result.ordered_uids)
        self.assertNotIn("header", result.ordered_uids)
        self.assertGreater(result.pruned, 0)
        self.assertFalse(empty_seeds.expanded_uids)

    def test_multi_model_quota_survives_large_first_model(self):
        rows = [row(f"a{i}", "I2C address", model_no="QMI8658A", page=i) for i in range(8)]
        rows.append(row("b", "I2C address", model_no="QMI8658B", file="cat/Z.pdf"))
        table = table_for(rows)
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()):
            result = entity.search(table, "QMI8658A QMI8658B I2C address", limit=4, seed_rows=rows)
        self.assertEqual(len(result.direct_uids), 2)
        self.assertIn("b", result.direct_uids)
        self.assertEqual(result.by_model["qmi8658b"], 1)
        picked = [((r["file"], r["page"]), 1) for r in rows]
        balanced = retrieval._balance_models(picked, {(r["file"], r["page"]): r for r in rows},
                                              "QMI8658A QMI8658B I2C")
        self.assertEqual(balanced[1][0][0], "cat/Z.pdf")

    def test_model_only_query_falls_back_without_building_index(self):
        with patch.object(entity, "_cached_index", side_effect=AssertionError("no semantic signal")):
            result = entity.search(table_for([]), "SSP1117-3.3V")
        self.assertEqual(result.status, "skipped")
        self.assertEqual(result.ordered_uids, ())

    def test_total_query_candidate_budget_is_a_hard_limit(self):
        rows = [row(str(i), "I2C address", page=i) for i in range(10)]
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()), \
             patch.object(entity, "MAX_QUERY_CANDIDATES", 1):
            result = entity.search(table_for(rows), "QMC6309 I2C address", seed_rows=[])
        self.assertEqual(len(result.direct_uids), 1)
        self.assertEqual(result.expanded_uids, ())

    def test_subquestion_slots_preserve_rare_parameter_candidate(self):
        rows = [row(f"v{i}", "input voltage 3.3 V", page=i) for i in range(8)]
        rows.append(row("address", "I2C address 0x6a", page=10))
        table = table_for(rows)
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()):
            result = entity.search(table, "QMC6309 input voltage address", limit=4)
        self.assertIn("address", result.direct_uids)
        self.assertEqual(len(result.direct_uids), 2)

    def test_index_identity_version_and_reset_are_independent(self):
        rows = [row("a", "VDD 3.3 V")]
        first, second = table_for(rows), table_for(rows)
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()) as scan:
            entity.get_index(first)
            entity.get_index(first)
            entity.get_index(second)
            second.version = 2
            entity.get_index(second)
            entity.reset_cache()
            entity.get_index(second)
        self.assertEqual(scan.call_count, 4)

    def test_memory_budget_rejects_instead_of_publishing_partial_index(self):
        rows = [row("a", "VDD 3.3 V")]
        table = table_for(rows)
        with patch.object(entity, "MAX_INDEX_ROWS", 0), patch.object(entity, "_batches") as scan:
            with self.assertRaises(entity.IndexLimitError):
                entity.get_index(table)
        scan.assert_not_called()
        self.assertIsNone(entity.index_for(table))

    def test_over_budget_version_is_not_repeatedly_scanned(self):
        rows = [row("a", "VDD 3.3 V")]
        table = table_for(rows)
        with patch.object(entity, "MAX_INDEX_BYTES", 1), \
             patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()) as scan:
            for _ in range(2):
                with self.assertRaises(entity.IndexLimitError):
                    entity.get_index(table)
            self.assertEqual(scan.call_count, 1)
            table.version = 2
            with self.assertRaises(entity.IndexLimitError):
                entity.get_index(table)
            self.assertEqual(scan.call_count, 2)

    def test_generic_query_does_not_build_an_index_or_report_previous_telemetry(self):
        rows = [row("a", "VDD 3.3 V")]
        table = table_for(rows)
        with patch.object(entity, "_batches", side_effect=lambda _: pa.Table.from_pylist(rows).to_batches()):
            entity.get_index(table)
        result = entity.search(table, "unrelated words")
        self.assertEqual(result.status, "skipped")
        self.assertNotIn("index_rows", entity.diagnostics(result))


class StructuredChannelTest(unittest.TestCase):
    def tearDown(self):
        retrieval.reset_cache()

    def test_empty_entity_query_is_not_degraded(self):
        cands, diag, degraded = retrieval._Candidates(60, 5), {}, []
        with patch.object(entity, "search", return_value=entity.EntitySearch((), (), (), "skipped")):
            retrieval._channel_structured(SimpleNamespace(version=1), "unrelated", 10,
                                          None, None, cands, degraded, diag)
        self.assertEqual(degraded, [])
        self.assertEqual(diag["structured"]["added_pages"], 0)
        self.assertFalse(cands)

    def test_failed_hydration_is_degraded_and_not_cached(self):
        table = SimpleNamespace(version=1)
        result = entity.EntitySearch(("model:qmc6309",), ("a",), (), "used")
        with patch.object(retrieval, "_channel_fts"), patch.object(retrieval, "_channel_substring"), \
             patch.object(entity, "search", return_value=result), \
             patch.object(retrieval, "_hydrate", side_effect=RuntimeError("bad index")), \
             override_config(query_cache_ttl=600):
            with self.assertLogs("pdfrag.retrieval", level="WARNING"):
                diag = {}
                retrieval.search(table, "QMC6309", mode="fts", rerank=False, structured=True, diagnostics=diag)
        self.assertEqual(diag["degraded"], ["structured"])
        self.assertEqual(diag["structured"]["status"], "failed")
        self.assertFalse(retrieval._RESULT_CACHE)

    def test_hydration_filters_orphans_and_adds_only_one_block_per_page(self):
        rows = [row("a", "VDD 3.3 V", file="cat/A_1.pdf"),
                row("b", "VDD 3.3 V", file="cat/A-1.pdf", page=1),
                row("c", "supply voltage", file="cat/A_1.pdf")]
        result = entity.EntitySearch(("model:qmc6309",), ("a", "b", "c"), ("orphan",), "used")
        cands = retrieval._Candidates(60, 5)
        with patch.object(entity, "search", return_value=result), \
             patch.object(retrieval, "_hydrate", return_value={r["uid"]: r for r in rows}):
            retrieval._channel_structured(SimpleNamespace(version=1), "QMC6309", 10,
                                          None, "A_1.pdf", cands, [], {})
        self.assertEqual(set(cands.rows), {("cat/A_1.pdf", 0)})
        self.assertAlmostEqual(cands.scores[("cat/A_1.pdf", 0)], 1 / 70)

    def test_existing_page_only_gains_missing_evidence_not_score(self):
        header = row("header", "model header")
        answer = row("answer", "VDD 3.3 V")
        result = entity.EntitySearch(("symbol:vdd",), ("answer",), (), "used")
        cands = retrieval._Candidates(60, 5)
        cands.add(header, 1)
        before = dict(cands.scores)
        with patch.object(entity, "search", return_value=result), \
             patch.object(retrieval, "_hydrate", return_value={"answer": answer}):
            for _ in range(2):
                retrieval._channel_structured(SimpleNamespace(version=1), "QMC6309 VDD", 10,
                                              None, None, cands, [], {})
        self.assertEqual(cands.scores, before)
        self.assertIs(cands.rows[(header["file"], 0)], header)
        self.assertEqual([chunk["uid"] for chunk in cands.chunks[(header["file"], 0)]], ["header", "answer"])

    def test_expansion_path_is_hydrated_and_bounded(self):
        seed = row("seed", "I2C address", page=1)
        answer = row("answer", "supply voltage", page=2)
        result = entity.EntitySearch(("model:qmc6309",), (), ("answer",), "used",
                                     paths={"answer": {"seed_chunk_id": "seed",
                                                         "shared_entities": ["model:qmc6309", "interface:i2c"]}})
        cands = retrieval._Candidates(60, 5)
        with patch.object(entity, "search", return_value=result), \
             patch.object(retrieval, "_hydrate", return_value={"seed": seed, "answer": answer}) as hydrate:
            retrieval._channel_structured(SimpleNamespace(version=1), "QMC6309", 10,
                                          None, None, cands, [], {})
        self.assertEqual(set(hydrate.call_args.args[1]), {"seed", "answer"})
        hit = retrieval._build_results(cands.top(5), cands, {}, "supply voltage", 5, 0)[0]
        trace = hit["retrieval_trace"]
        self.assertEqual(trace["kind"], "entity_expansion")
        self.assertEqual(trace["seed_page"], 2)
        self.assertEqual(trace["chunk_id"], "answer")
        self.assertEqual(trace["scope"], "retrieval_only")
        self.assertEqual(trace["shared_entities"], ["model:qmc6309", "interface:i2c"])

    def test_default_does_not_call_entity_bridge(self):
        with patch.object(retrieval, "_channel_fts"), patch.object(retrieval, "_channel_substring"), \
             patch.object(entity, "search", side_effect=AssertionError("default must not build entities")):
            self.assertEqual(retrieval.search(SimpleNamespace(version=1), "QMC6309", mode="fts", rerank=False), [])


if __name__ == "__main__":
    unittest.main()
