"""紧凑层逐字与上下文成本验证,不使用模型裁判。"""
import unittest

from backend import evidence_probe
from tests import test_evidence_probe as probe_tests
from tools import eval_evidence_efficiency as evaluator


class EvidenceMetricTest(unittest.TestCase):
    def test_verifier_rejects_wrong_role_unit_and_changed_reference(self):
        row = probe_tests.BindingTest().row()
        need = {"parameter": "Voltage", "role": "max", "condition": "mode=low"}
        bindings, _ = evidence_probe.bind_rows([row], [need])
        binding = bindings[0]
        self.assertTrue(evaluator.binding_valid(binding, need, [row]))
        self.assertFalse(evaluator.binding_valid({**binding, "unit": "mV"}, need, [row]))
        self.assertFalse(evaluator.binding_valid({**binding, "values": {"max": "2"}}, need, [row]))
        self.assertFalse(evaluator.binding_valid({**binding, "source": {**binding["source"], "index_md5": "changed"}}, need, [row]))
        self.assertFalse(evaluator.binding_valid({**binding, "source": {**binding["source"], "start_offset": -1}}, need, [row]))

    def test_page_context_is_equal_for_full_and_compact_and_not_silently_cut(self):
        row = probe_tests.BindingTest().row()
        binding = evidence_probe.bind_rows([row], [{"parameter": "Voltage", "role": "max", "condition": "mode=low"}])[0][0]
        result = {"results": [], "bindings": [binding]}
        pages = {(row["file"], row["page"]+1): [row]}
        full = evaluator.context_turns(result, pages, max_chars=40)
        compact = evaluator.context_turns(evidence_probe.compact_payload(result), pages, max_chars=40)
        self.assertEqual(full, compact)
        self.assertEqual("".join(turn["text"] for turn in full), row["text"])
        self.assertGreater(len(full), 1)
        self.assertFalse(full[-1]["truncated"])


if __name__ == "__main__":
    unittest.main()
