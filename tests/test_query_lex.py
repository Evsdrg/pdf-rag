"""查询词法在实体、子串、片段与身份提示之间必须一致。"""
import random
import re
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

    def test_factored_signal_regex_preserves_overlap_and_unicode_boundaries(self):
        interface = re.compile(r"(?<![a-z0-9_])(?P<name>i[2²]c|i[2²]s|qspi|spi|usart|uart|gpio|usb|can|sdio|pwm)\d*(?![a-z0-9_])", re.I)
        symbol = re.compile(r"(?<![a-z0-9_])(?:vdif[12]|vdd(?:[ _\t]*(?:apc|core|mem|ioq|io|rf))?|vin|vout|vbat|vled|vcc|vgs|vds|idd(?:[ _\t]*(?:hp|lp|pd|standby))?|ibias|iout|sda|scl|sa0|cs|n?reset|en|cbst|r[ _\t]*(?:in|out)|ftype)(?![a-z0-9_])", re.I)
        rng = random.Random(20261101)
        tokens = ["VDD", "VDD_IOQ", "VDD IO", "IDD HP", "SDA", "SA0", "CS", "r in", "EN", "CBST", "I2C", "I²S", "CAN", "can", "SPI", "UART3", "ſpi", "İ2C", "ı2c"]
        separators = ["", " ", "_", "x", "\t", "\n", "中", "é", "-", "."]
        texts = ["VDD" + " " * 20000 + "X"]
        texts += ["".join(rng.choice(separators) + rng.choice(tokens) for _ in range(8)) for _ in range(300)]
        for text in texts:
            expected_interfaces = [(m.span(), m.group(), m["name"]) for m in interface.finditer(text)]
            expected_symbols = [(m.span(), m.group()) for m in symbol.finditer(text)]
            matches = list(query_lex._SIGNAL_RE.finditer(text))
            self.assertEqual([(m.span(), m.group(), m["name"]) for m in matches if m["interface"] is not None], expected_interfaces)
            self.assertEqual([(m.span(), m.group()) for m in matches if m["symbol"] is not None], expected_symbols)

    def test_possessive_quantity_regex_keeps_values_and_rejects_long_near_misses(self):
        reference = re.compile(query_lex.VALUE_RE.pattern.replace("++", "+").replace("*+", "*"))
        for text in ("1.2.3V -0.3 V +3.3V 3.3Vx 10ms", "1 mA 1 MA 500 mΩ 500 MΩ", "١٢ mA 1\u2003mA",
                     "9" * 20000 + "X", "9" + " " * 20000 + "X", "SSP1117-3.3V 74LVC1G04GW"):
            self.assertEqual([(m.span(), m.group()) for m in query_lex.VALUE_RE.finditer(text)],
                             [(m.span(), m.group()) for m in reference.finditer(text)])

    def test_alias_word_prefilter_preserves_hyphens_parentheses_and_embedded_words(self):
        for text in ("rds(on) rds (on)", "pull-up pull up", "supply\tvoltage output\ndata rate", "pinout pin", "xdropout dropoutx", "静态偏置电流 陀螺仪量程"):
            keys = set(query_lex.extract_entities(text))
            folded = text.casefold()
            expected = {"parameter:" + name for name, _, pattern, chinese in query_lex._PARAMETERS
                        if any(alias in folded for alias in chinese) or pattern.search(folded)}
            self.assertEqual({key for key in keys if key.startswith("parameter:")}, expected)

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
