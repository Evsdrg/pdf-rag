"""向量分区:uid 唯一性、slug 契约区分、分区读写与覆盖率口径。"""
import shutil
import tempfile
import unittest

import lancedb
import pyarrow as pa

from backend import config, vecstore
from tests.support import override_config


class UidTest(unittest.TestCase):
    def test_stable_and_unique_across_seq(self):
        a = vecstore.make_uid("a.pdf", 0, 0)
        self.assertEqual(a, vecstore.make_uid("a.pdf", 0, 0))
        self.assertNotEqual(a, vecstore.make_uid("a.pdf", 0, 1))
        self.assertNotEqual(a, vecstore.make_uid("a.pdf", 1, 0))
        self.assertNotEqual(a, vecstore.make_uid("b.pdf", 0, 0))

    def test_identical_text_on_same_page_still_unique(self):
        # 历史 bug:用 file+page+text 做哈希,同页逐字相同的块会碰撞(实测 9 处)。
        # uid 必须含页内块序,与文本无关。
        uids = vecstore.chunk_uids("a.pdf", 5, 3)
        self.assertEqual(len(set(uids)), 3)

    def test_length_fixed(self):
        self.assertEqual(len(vecstore.make_uid("x", 0, 0)), vecstore.UID_LEN)


class SlugTest(unittest.TestCase):
    def test_separates_model(self):
        self.assertNotEqual(vecstore.model_slug("m-a", 768), vecstore.model_slug("m-b", 768))

    def test_separates_dim(self):
        self.assertNotEqual(vecstore.model_slug("m", 768), vecstore.model_slug("m", 1024))

    def test_separates_input_type(self):
        # 同一模型不同建库 input_type 产出不同空间的向量,必须分区隔离
        self.assertNotEqual(vecstore.model_slug("m", 768, ""),
                            vecstore.model_slug("m", 768, "search_document"))

    def test_normalizes_unsafe_chars(self):
        s = vecstore.model_slug("Qwen/Qwen3-Embedding-8B", 768)
        self.assertNotIn("/", s)
        self.assertNotIn(".", s)
        self.assertEqual(s, "qwen_qwen3_embedding_8b__768__")


class PartitionStoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.db = lancedb.connect(self.dir)
        # 主表:2 个文件共 4 块
        main = [{"uid": vecstore.make_uid("a.pdf", 0, i), "file": "a.pdf", "text": f"a{i}"}
                for i in range(2)]
        main += [{"uid": vecstore.make_uid("b.pdf", 0, i), "file": "b.pdf", "text": f"b{i}"}
                 for i in range(2)]
        self.main = self.db.create_table("chunks", data=main)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _part(self, slug, rows):
        t = vecstore.ensure_partition(self.db, slug, 4)
        t.add(rows)
        return t

    def test_ensure_partition_rejects_dim_mismatch(self):
        vecstore.ensure_partition(self.db, "s1", 4)
        with self.assertRaises(ValueError):
            vecstore.ensure_partition(self.db, "s1", 8)

    def test_open_missing_returns_none(self):
        self.assertIsNone(vecstore.open_partition(self.db, "nope"))

    def test_coverage_full(self):
        rows = [{"uid": r["uid"], "file": r["file"], "page": 0, "category": "",
                 "md5": "", "vector": [0.1] * 4} for r in self.main.to_arrow().to_pylist()]
        self._part("s", rows)
        cov = vecstore.coverage(self.db, self.main, "s")
        self.assertEqual(cov["blocks_covered"], 4)
        self.assertEqual(cov["ratio"], 1.0)
        self.assertEqual(cov["files_partial"], 0)

    def test_coverage_counts_blocks_not_files(self):
        # 只覆盖 a.pdf 的 1/2 块:b.pdf 全缺。按块统计必须是 1/4,
        # 按文件会误报成"1/2 文件已覆盖",掩盖 within-file 缺口。
        rows = [{"uid": vecstore.make_uid("a.pdf", 0, 0), "file": "a.pdf", "page": 0,
                 "category": "", "md5": "", "vector": [0.1] * 4}]
        self._part("s", rows)
        cov = vecstore.coverage(self.db, self.main, "s")
        self.assertEqual(cov["blocks_covered"], 1)
        self.assertEqual(cov["blocks_total"], 4)
        self.assertEqual(cov["ratio"], 0.25)
        self.assertEqual(cov["files_covered"], 1)
        self.assertEqual(cov["files_partial"], 1)   # a.pdf 部分覆盖

    def test_coverage_ignores_orphans(self):
        rows = [{"uid": r["uid"], "file": r["file"], "page": 0, "category": "",
                 "md5": "", "vector": [0.1] * 4} for r in self.main.to_arrow().to_pylist()]
        rows.append({"uid": "ghost", "file": "gone.pdf", "page": 0,
                     "category": "", "md5": "", "vector": [0.1] * 4})
        self._part("s", rows)
        cov = vecstore.coverage(self.db, self.main, "s")
        self.assertEqual(cov["blocks_covered"], 4)   # 孤儿不计入分子
        self.assertEqual(cov["ratio"], 1.0)

    def test_coverage_missing_partition(self):
        cov = vecstore.coverage(self.db, self.main, "nope")
        self.assertFalse(cov["exists"])
        self.assertEqual(cov["ratio"], 0.0)

    def test_meta_roundtrip(self):
        vecstore.upsert_partition_meta(self.db, "s", blocks=4, files=2)
        meta = vecstore.get_partition_meta(self.db, "s")
        self.assertEqual(meta["blocks"], 4)
        self.assertEqual(meta["files"], 2)
        # 再次写入应更新而非插新行
        vecstore.upsert_partition_meta(self.db, "s", blocks=5)
        self.assertEqual(len(vecstore.list_partitions(self.db)), 1)
        self.assertEqual(vecstore.get_partition_meta(self.db, "s")["blocks"], 5)
        self.assertEqual(vecstore.get_partition_meta(self.db, "s")["files"], 2)

    def test_delete_file_from_partition(self):
        rows = [{"uid": vecstore.make_uid("a.pdf", 0, i), "file": "a.pdf", "page": 0,
                 "category": "", "md5": "", "vector": [0.1] * 4} for i in range(2)]
        t = self._part("s", rows)
        vecstore.delete_file(t, "a.pdf")
        self.assertEqual(t.count_rows(), 0)


if __name__ == "__main__":
    unittest.main()
