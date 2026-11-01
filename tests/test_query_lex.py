"""查询词法在实体、子串、片段与身份提示之间必须一致。"""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pyarrow as pa

from backend import agent_api, entity, query_lex, retrieval
from tests.support import override_config


class QueryLexTest(unittest.TestCase):
    def test_full_part_number_suffixes_are_neither_models_nor_values(self):
        for part in ("SSP1117-3.3V", "AMS1117-3.3S", "ICM-42605-HXY", "74LVC1G04GW"):
            with self.subTest(part=part):
                self.assertEqual(query_lex.model_tokens(part), [part])
                self.assertEqual(set(entity.extract_entities(part, query=True)), {"model:" + part.casefold()})
                terms, models = retrieval._query_terms(part)
                self.assertEqual(terms, [])
                self.assertEqual(models, {part.casefold()})
                with override_config(num_unit_bonus=1.5):
                    self.assertEqual(retrieval._score_window(part, [], set()), 0)
        self.assertEqual(query_lex.model_tokens("MSM8216-MSM8616-MSM8916"), ["MSM8216", "MSM8616", "MSM8916"])

    def test_units_symbols_versions_and_interfaces_are_not_models(self):
        text = "I2C UART3 V1.2 0x6A SA0 VDD_APC Vdif1 Vdif2 SOT-89-3L 100MHz 3.3V 1mA 1MA"
        self.assertEqual(query_lex.model_tokens(text), [])
        keys = query_lex.extract_entities(text, query=True)
        self.assertTrue({"symbol:sa0", "symbol:vddapc", "value:1mA", "value:1MA"}.issubset(keys))
        self.assertFalse(any(key.startswith("model:") for key in keys))

    def test_prefix_candidate_is_not_an_identity_confirmation(self):
        hits = [{"file": "cat/LSM6DS3TR-C.pdf", "model_no": "LSM6DS3TR-C"}]
        identities, warnings = agent_api._identity("LSM6DS3TR", hits)
        self.assertEqual(identities[0]["status"], "unconfirmed")
        self.assertEqual(warnings[0]["code"], "MODEL_IDENTITY_UNCONFIRMED")
        self.assertEqual(agent_api._identity("LSM6DS3TR-C", hits)[0][0]["status"], "matched")

    def test_parameter_condition_slots_are_bounded_and_diversify_evidence(self):
        query = "QMC6309 input voltage address"
        slots = query_lex.evidence_slots(query)
        self.assertEqual({slot.signal for slot in slots}, {"parameter:input_voltage", "parameter:address"})
        cands = retrieval._Candidates(60, 5)
        for i in range(5):
            cands.add({"file": "a.pdf", "page": i, "uid": str(i), "model_no": "QMC6309",
                       "text": "input voltage 3.3 V"}, i)
        cands.add({"file": "a.pdf", "page": 8, "uid": "address", "model_no": "QMC6309",
                   "text": "I2C address 0x6a"}, 30)
        picked = retrieval._cover_evidence(cands.top(20), cands, query)
        self.assertIn(("a.pdf", 8), [key for key, _ in picked[:2]])
        self.assertEqual(len(picked), len(cands.scores))
        conditions = query_lex.evidence_slots("QMC6309 VCC=3.0V VCC=4.5V VOH")
        self.assertEqual(len(conditions), 2)
        self.assertEqual({slot.conditions[0] for slot in conditions}, {"vcc=3.0V", "vcc=4.5V"})
        unit_slot = query_lex.EvidenceSlot("", "parameter:current", ("iout=1mA",))
        self.assertEqual(query_lex.slot_score(unit_slot, {"parameter:current"}, "IOUT=1MA"), 1)
        scoped = retrieval._Candidates(60, 5)
        for page, text in enumerate(("VOH VCC=3.0V", "VOH VCC=4.5V")):
            scoped.add({"file": "a.pdf", "page": page, "text": text, "model_no": "QMC6309"}, page)
        covered = retrieval._cover_evidence(scoped.top(5), scoped, "QMC6309 VCC=3.0V VCC=4.5V VOH")
        self.assertEqual(len(covered[:2]), 2)
        self.assertEqual({key[1] for key, _ in covered[:2]}, {0, 1})

    def test_coverage_reuses_text_only_within_one_query(self):
        cands = retrieval._Candidates(60, 5)
        text = "input voltage 3.3 V and I2C address"
        for page in range(2):
            cands.add({"file": "a.pdf", "page": page, "uid": str(page), "model_no": "QMC6309", "text": text}, page)
        query = "QMC6309 input voltage address"
        coverage = retrieval._EvidenceCoverage(query)
        with patch.object(query_lex, "extract_entities", wraps=query_lex.extract_entities) as parse:
            first = retrieval._cover_evidence(cands.top(5), cands, query, coverage)
            second = retrieval._cover_evidence(list(reversed(first)), cands, query, coverage)
        self.assertEqual(sum(call.args == (text,) for call in parse.call_args_list), 1)
        self.assertEqual({key for key, _ in first}, {key for key, _ in second})
        cands.chunks[("a.pdf", 0)][0] = {**cands.rows[("a.pdf", 0)], "text": "input voltage only"}
        fresh = retrieval._EvidenceCoverage(query)
        self.assertNotIn("parameter:address", fresh.page(("a.pdf", 0), cands)[0])

    def test_substring_filters_before_limit_and_uses_parameter_relevance(self):
        rows = [{"uid": str(i), "file": "other/A.pdf", "page": i, "category": "other", "text": "ICM-42605-HXY voltage"}
                for i in range(5)]
        rows += [{"uid": "header", "file": "cat/Z_100%.pdf", "page": 0, "category": "cat", "text": "ICM-42605-HXY header"},
                 {"uid": "answer", "file": "cat/Z_100%.pdf", "page": 6, "category": "cat", "text": "supply voltage 3.3 V"}]
        rows = [{**row, "model_no": "ICM-42605-HXY"} for row in rows]
        with patch.object(retrieval, "_proj_table", return_value=pa.Table.from_pylist(rows)):
            found = retrieval._substring_recall(SimpleNamespace(), "icm-42605-hxy", 1,
                                                query="ICM-42605-HXY supply voltage", category="cat", file="Z_100%")
        self.assertEqual([row["uid"] for row in found], ["answer"])


if __name__ == "__main__":
    unittest.main()
