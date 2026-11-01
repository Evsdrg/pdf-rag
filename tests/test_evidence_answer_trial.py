"""回答对照包只离线准备;任务字段不混入gold,同证据不等同模型效果已验证。"""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import prepare_evidence_answer_trial as trial


class AnswerTrialPreparationTest(unittest.TestCase):
    def question(self):
        return {"id": "X", "query": "ABC123 voltage max under mode=low", "model": "ABC123",
                "source_terms": [], "revision": "", "needs": [{"parameter": "Voltage", "role": "max", "condition": "mode=low"}],
                "targets": [{"file": "secret-gold-file", "page": 999, "required": ["GOLD-MARKER"]}], "negative": False}

    def test_task_input_whitelist_does_not_include_gold_or_negativity(self):
        task = trial.task_input(self.question())
        self.assertEqual(set(task), set(trial.TASK_FIELDS))
        self.assertNotIn("GOLD-MARKER", str(task))
        self.assertNotIn("secret-gold-file", str(task))
        self.assertNotIn("negative", task)

    def test_two_packets_preserve_evidence_and_context_but_are_not_sent(self):
        hit = {"file": "A.pdf", "page": 1, "model_no": "ABC123", "snippet": "Voltage 3 V at mode=low",
               "retrieval_trace": {"kind": "entity_direct"}}
        binding = {"need": 0, "conditions": "mode=low", "values": {"max": "3"},
                   "source": {"file": "A.pdf", "page": 1}}
        turn = {"results": [hit], "bindings": [binding], "missing": []}
        result = {**turn, "source": {"status": "resolved"}, "_turns": [turn]}
        rows = [{"file": "A.pdf", "page": 0, "text": "Common condition TA=25°C. Voltage 3 V at mode=low"}]
        with patch.object(trial.evidence_probe, "run", return_value=result):
            packets = trial.prepare_case(self.question(), SimpleNamespace(version=1), rows)
        self.assertEqual([packet["variant"] for packet in packets], ["full", "compact"])
        self.assertEqual(packets[0]["page_context_sha256"], packets[1]["page_context_sha256"])
        self.assertEqual(packets[0]["task_sha256"], packets[1]["task_sha256"])
        self.assertNotEqual(packets[0]["messages_sha256"], packets[1]["messages_sha256"])
        for packet in packets:
            self.assertEqual(packet["status"], "prepared_not_sent")
            self.assertEqual(packet["messages_sha256"], trial.digest(packet["messages"]))
            self.assertIn("TA=25°C", packet["messages"][1]["content"])
            self.assertNotIn("GOLD-MARKER", packet["messages"][1]["content"])
            self.assertNotIn("secret-gold-file", packet["messages"][1]["content"])

    def test_prepared_files_are_never_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            trial.write_once(path, {"status": "prepared_not_sent"})
            with self.assertRaises(FileExistsError):
                trial.write_once(path, {"status": "sent"})
            self.assertIn("prepared_not_sent", path.read_text())


if __name__ == "__main__":
    unittest.main()
