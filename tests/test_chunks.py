"""分块逻辑:索引的第一道工序,切错会静默劣化检索。"""
import unittest

from backend import ingest
from tests.support import override_config


class SplitIntoChunksTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(ingest.split_into_chunks(""), [])
        self.assertEqual(ingest.split_into_chunks("   \n\n  "), [])

    def test_short_paragraphs_aggregate(self):
        # 多个短段落应聚合进一个块(段落间以单换行连接)
        chunks = ingest.split_into_chunks("aaa\n\nbbb\n\nccc", max_chars=100, overlap=0)
        self.assertEqual(chunks, ["aaa\nbbb\nccc"])

    def test_respects_max_chars_at_paragraph_boundary(self):
        # 段落放不下时在段落边界收尾,不拆段内文本
        chunks = ingest.split_into_chunks("A" * 60 + "\n\n" + "B" * 60, max_chars=80, overlap=0)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], "A" * 60)
        self.assertEqual(chunks[1], "B" * 60)

    def test_long_paragraph_hard_split_prefers_newline(self):
        # 超长单段按换行硬切,且切点尽量落在 max_chars/2 之后的换行处
        body = "\n".join("x" * 10 for _ in range(20))  # 20 行 x10,换行处众多
        chunks = ingest.split_into_chunks(body, max_chars=50, overlap=0)
        self.assertGreater(len(chunks), 1)
        for c in chunks[:-1]:  # 中间块都不超过 max_chars(切点在换行处)
            self.assertLessEqual(len(c), 50)

    def test_overlap_keeps_tail(self):
        # 相邻块保留 overlap 字重叠,缓解边界信息断裂
        chunks = ingest.split_into_chunks("A" * 60 + "\n\n" + "B" * 60, max_chars=80, overlap=20)
        self.assertEqual(len(chunks), 2)
        self.assertTrue(chunks[1].startswith("A" * 20))
        self.assertTrue(chunks[1].endswith("B" * 60))

    def test_config_defaults_used_when_omitted(self):
        with override_config(chunk_max_chars=400, chunk_overlap_chars=0):
            chunks = ingest.split_into_chunks("A" * 500)
            self.assertEqual(len(chunks[0]), 400)


if __name__ == "__main__":
    unittest.main()
