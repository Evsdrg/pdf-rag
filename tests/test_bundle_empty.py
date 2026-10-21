"""数据包在空库/空分区上的健壮性。

历史上 `if not db.list_tables():` 被当成"库为空"的判断,但 LanceDB 0.36 的
`list_tables()` 返回 `ListTablesResponse` 对象 —— 空库时 `bool()` 仍为真,
保护形同虚设,紧接着 `open_table("chunks")` 抛 ValueError:导出空库直接 500。
"""
import pathlib
import tempfile
import unittest

import lancedb

from backend import bundle, config, library
import tests  # noqa: F401  —— 触发配置隔离,必须在 config 被使用前导入


class EmptyIndexTest(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self._db_path = config.DB_PATH
        self._pdf_root = config.PDF_ROOT
        config.DB_PATH = str(self.tmp / "empty.lance")
        config.PDF_ROOT = str(self.tmp / "pdf")
        pathlib.Path(config.PDF_ROOT).mkdir()

    def tearDown(self):
        config.DB_PATH = self._db_path
        config.PDF_ROOT = self._pdf_root

    def test_table_names_empty_db(self):
        db = lancedb.connect(config.DB_PATH)
        self.assertEqual(library.db_table_names(db), [])
        self.assertEqual([], [n for n in library.db_table_names(db) if n == "chunks"])

    def test_table_names_lists_real_table(self):
        db = lancedb.connect(config.DB_PATH)
        db.create_table("chunks", data=[{"uid": "x"}])
        self.assertIn("chunks", library.db_table_names(db))

    def test_indexed_files_empty(self):
        self.assertEqual(bundle._indexed_files(), [])

    def test_chunk_count_empty(self):
        self.assertEqual(bundle._chunk_count(), 0)

    def test_partition_block_empty(self):
        self.assertEqual(bundle._partition_block(), [])

    def test_export_empty_bundle(self):
        dest = self.tmp / "empty.tar.zst"
        r = bundle.export_bundle(dest, include_docs=False)
        self.assertEqual(r["documents"], 0)
        self.assertEqual(r["manifest"]["counts"]["chunks"], 0)
        self.assertTrue(dest.is_file())

    def test_get_db_returns_none_for_empty(self):
        library.reset_table()
        self.assertIsNone(library.get_db())
        self.assertIsNone(library.get_table())


if __name__ == "__main__":
    unittest.main()
