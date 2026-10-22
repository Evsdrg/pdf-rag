"""向量分区:uid 唯一性、slug 契约区分、分区读写、覆盖率口径与向量索引。"""
import shutil
import tempfile
import unittest
from unittest import mock

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
        uids = [vecstore.make_uid("a.pdf", 5, i) for i in range(3)]
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


class VectorIndexTest(unittest.TestCase):
    """向量索引是可选加速:没有它必须照样能查,且结果不能变。"""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.db = lancedb.connect(self.dir)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _part(self, slug, rows):
        t = vecstore.ensure_partition(self.db, slug, 4)
        t.add(rows)
        return t

    def _rows(self, n):
        # 方向各异的向量,避免重复导致 KMeans 退化
        return [{"uid": f"u{i}", "file": f"f{i}.pdf", "page": 0, "category": "",
                 "md5": "", "vector": [float(i + 1), float((i * 7) % 11 + 1),
                                       float((i * 3) % 5 + 1), 1.0]}
                for i in range(n)]

    def test_no_index_by_default(self):
        p = self._part("s", self._rows(20))
        self.assertFalse(vecstore.has_vector_index(p))

    def test_small_dataset_skips_index(self):
        # Lance 在 40 行上 KMeans 会产出大量空簇,索引结果与暴力扫描完全不同
        # (实测 top10 无一相同)。小库必须拒绝建索引,退回暴力扫描。
        p = self._part("s", self._rows(40))
        self.assertLess(40, vecstore.MIN_ROWS_FOR_INDEX)
        self.assertFalse(vecstore.ensure_vector_index(p))
        self.assertFalse(vecstore.has_vector_index(p))

    def test_ensure_is_idempotent_on_big_dataset(self):
        p = self._part("s", self._rows(vecstore.MIN_ROWS_FOR_INDEX + 100))
        self.assertTrue(vecstore.ensure_vector_index(p))
        self.assertTrue(vecstore.has_vector_index(p))
        self.assertFalse(vecstore.ensure_vector_index(p))          # 已有则跳过
        self.assertTrue(vecstore.ensure_vector_index(p, replace=True))

    def test_search_works_without_index(self):
        p = self._part("s", self._rows(20))
        got = [r["uid"] for r in p.search([1.0, 1.0, 1.0, 1.0],
                                          query_type="vector").limit(5).to_list()]
        self.assertEqual(len(got), 5)

    def test_refine_factor_at_least_two(self):
        # 小于 2 会静默漏召回(实测 rf=1 时 400 条查询漏 17 条)
        self.assertGreaterEqual(vecstore.REFINE_FACTOR, 2)

    def test_failure_does_not_raise(self):
        # 索引纯属加速:建不了也不能让写入/检索失败
        p = self._part("s", self._rows(vecstore.MIN_ROWS_FOR_INDEX + 10))
        with mock.patch.object(p, "create_index", side_effect=RuntimeError("boom")):
            self.assertFalse(vecstore.ensure_vector_index(p))


if __name__ == "__main__":
    unittest.main()


class SelectPartitionsTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.db = lancedb.connect(self.dir)
        for slug, model, dim in (("m_a__768__", "model-a", 768),
                                 ("m_b__768__", "model-b", 768),
                                 ("m_a__1024__", "model-a", 1024)):
            vecstore.ensure_partition(self.db, slug, 4)
            vecstore.upsert_partition_meta(self.db, slug, blocks=1, files=1,
                                           model=model, dim=dim)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _slugs(self):
        return [m["slug"] for m in vecstore.select_partitions(self.db)]

    def test_default_uses_current_slug_only(self):
        with override_config(vector_models_priority="", vector_models_exclude=""):
            slugs = self._slugs()
        cur = vecstore.current_slug()
        self.assertEqual(slugs, [cur] if cur in ("m_a__768__", "m_b__768__", "m_a__1024__") else [])

    def test_priority_order_respected(self):
        with override_config(vector_models_priority="m_b__768__, m_a__768__"):
            self.assertEqual(self._slugs(), ["m_b__768__", "m_a__768__"])

    def test_model_name_matches_all_its_partitions(self):
        with override_config(vector_models_priority="model-a"):
            self.assertEqual(sorted(self._slugs()), ["m_a__1024__", "m_a__768__"])

    def test_exclude_wins_over_priority(self):
        # 冲突时以排除为准(fail-closed)
        with override_config(vector_models_priority="m_a__768__, m_b__768__",
                             vector_models_exclude="m_a__768__"):
            self.assertEqual(self._slugs(), ["m_b__768__"])

    def test_exclude_by_model_name(self):
        with override_config(vector_models_priority="model-a, m_b__768__",
                             vector_models_exclude="model-a"):
            self.assertEqual(self._slugs(), ["m_b__768__"])

    def test_unknown_slug_ignored(self):
        with override_config(vector_models_priority="nope, m_b__768__"):
            self.assertEqual(self._slugs(), ["m_b__768__"])

    def test_empty_meta_returns_empty(self):
        db2 = lancedb.connect(tempfile.mkdtemp())
        with override_config(vector_models_priority="x"):
            self.assertEqual(vecstore.select_partitions(db2), [])
