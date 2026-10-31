"""表格事实提取的保守边界,全部使用合成小表,不复制手册原文。"""
import unittest

from backend import table_facts


def row(text, *, uid="chunk-1", file="cat/A.pdf", page=3, md5="m1", model_no="QMC6309"):
    return {"uid": uid, "file": file, "page": page, "text": text,
            "md5": md5, "model_no": model_no}


TABLE = """Electrical Characteristics

| Parameter | Symbol | Conditions | Unit | Min | Typ | Max |
|---|---|---|---|---|---|---|
| Supply Voltage | VDD | Ta = 25 C | V | 1.62 | 1.80 | 1.98 |
| Supply Current | IDD | Ta = 85 C | mA | 1.2 | 2.5 | 4.0 |

Notes below the table.
"""


class TableFactsTest(unittest.TestCase):
    def test_complete_table_keeps_original_strings_and_offsets(self):
        facts = table_facts.extract(row(TABLE))
        self.assertEqual(len(facts), 2)
        first = facts[0]
        self.assertEqual(first["parameter"], "Supply Voltage")
        self.assertEqual(first["symbol"], "VDD")
        self.assertEqual(first["subject"], "QMC6309")
        self.assertEqual(first["values"], {"min": "1.62", "typ": "1.80", "max": "1.98"})
        self.assertEqual(first["unit"], "V")
        self.assertEqual(first["conditions"], "Ta = 25 C")
        source = first["source"]
        self.assertEqual(source["chunk_id"], "chunk-1")
        self.assertEqual(source["index_md5"], "m1")
        self.assertEqual(source["offset_basis"], "indexed_chunk")
        text = TABLE
        row_text = text[source["start_offset"]:source["end_offset"]]
        self.assertIn("Supply Voltage", row_text)
        self.assertIn("| 1.62 |", row_text)
        header_text = text[source["header_start_offset"]:source["header_end_offset"]]
        self.assertIn("| Parameter |", header_text)
        self.assertIn("| Max |", header_text)
        self.assertEqual(facts[1]["unit"], "mA")
        self.assertEqual(facts[1]["values"]["typ"], "2.5")

    def test_same_parameter_different_conditions_are_not_merged(self):
        text = """| Parameter | Unit | Conditions | Value |
|---|---|---|---|
| Supply Voltage | V | Ta = 25 C | 1.80 |
| Supply Voltage | V | Ta = 85 C | 1.95 |
"""
        facts = table_facts.extract(row(text))
        self.assertEqual(len(facts), 2)
        self.assertEqual({fact["conditions"] for fact in facts}, {"Ta = 25 C", "Ta = 85 C"})
        self.assertEqual({fact["values"]["value"] for fact in facts}, {"1.80", "1.95"})

    def test_blank_condition_is_not_inherited_from_previous_row(self):
        text = """| Parameter | Unit | Conditions | Value |
|---|---|---|---|
| Supply Voltage | V | Ta = 25 C | 1.80 |
| Supply Voltage | V |  | 1.95 |
"""
        facts = table_facts.extract(row(text))
        self.assertEqual(len(facts), 2)
        self.assertEqual(facts[1]["conditions"], "")
        self.assertEqual(facts[0]["conditions"], "Ta = 25 C")

    def test_missing_header_and_wrong_shape_are_skipped(self):
        no_header = """| Supply Voltage | V | 1.80 |
|---|---|---|
"""
        no_separator = """| Parameter | Unit | Value |
| Supply Voltage | V | 1.80 |
"""
        self.assertEqual(table_facts.extract(row(no_header)), [])
        self.assertEqual(table_facts.extract(row(no_separator)), [])

    def test_ambiguous_header_and_missing_unit_are_skipped(self):
        ambiguous = """| Parameter | Unit | Min | Min |
|---|---|---|---|
| Supply Voltage | V | 1.62 | 1.70 |
"""
        no_unit = """| Parameter | Value |
|---|---|
| Supply Voltage | 1.80 |
"""
        broken_unit = """| Parameter | Unit | Value |
|---|---|---|
| Supply Voltage | volts | 1.80 |
"""
        self.assertEqual(table_facts.extract(row(ambiguous)), [])
        self.assertEqual(table_facts.extract(row(no_unit)), [])
        self.assertEqual(table_facts.extract(row(broken_unit)), [])

    def test_broken_number_and_code_fence_are_skipped(self):
        broken = """| Parameter | Unit | Value |
|---|---|---|
| Supply Voltage | V | 1,80 |
"""
        fenced = "```\n" + TABLE + "```\n"
        self.assertEqual(table_facts.extract(row(broken)), [])
        self.assertEqual(table_facts.extract(row(fenced)), [])

    def test_ragged_columns_and_repeated_separator_are_skipped(self):
        ragged = """| Parameter | Unit | Min | Typ | Max |
|---|---|---|---|---|
| Supply Voltage | V | 1.62 | 1.80 |
"""
        repeated = """| Parameter | Unit | Min | Typ | Max |
|---|---|---|---|---|
| Supply Voltage | V | 1.62 | 1.80 | 1.98 |
|---|---|---|---|---|
| Supply Current | V | 1.0 | 2.0 | 3.0 |
"""
        self.assertEqual(table_facts.extract(row(ragged)), [])
        self.assertEqual(table_facts.extract(row(repeated)), [])

    def test_query_filters_and_budget_limits_results(self):
        text = """| Parameter | Unit | Conditions | Value |
|---|---|---|---|
| Supply Voltage | V | Ta = 25 C | 1.80 |
| Input Current | V | Ta = 25 C | 2.50 |
| Output Voltage | V | Ta = 25 C | 3.30 |
"""
        filtered = table_facts.extract(row(text), query="current")
        self.assertEqual([fact["parameter"] for fact in filtered], ["Input Current"])
        budgeted = table_facts.extract(row(text), max_facts=2)
        self.assertEqual(len(budgeted), 2)
        capped = table_facts.extract(row(text), max_facts=99)
        self.assertLessEqual(len(capped), 4)
        self.assertEqual(table_facts.extract(row(text), query="nothing matches"), [])

    def test_overlong_condition_is_rejected_not_silently_truncated(self):
        text = "| Parameter | Unit | Conditions | Value |\n|---|---|---|---|\n" + (
            "| Supply Voltage | V | " + "condition " * 30 + " | 1.80 |\n")
        self.assertEqual(table_facts.extract(row(text)), [])

    def test_subject_is_kept_exact_and_units_remain_case_sensitive(self):
        text = """| Parameter | Unit | Value |
|---|---|---|
| Quiescent Current | mA | 1.5 |
| Peak Current | MA | 2.5 |
"""
        facts = table_facts.extract(row(text, model_no="LSM6DS3TR-C"))
        self.assertEqual({fact["subject"] for fact in facts}, {"LSM6DS3TR-C"})
        units = {fact["parameter"]: fact["unit"] for fact in facts}
        self.assertEqual(units["Quiescent Current"], "mA")
        self.assertEqual(units["Peak Current"], "MA")


if __name__ == "__main__":
    unittest.main()
