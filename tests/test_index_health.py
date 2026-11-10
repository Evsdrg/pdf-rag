"""索引健康度视图的回归测试。

这个视图存在的理由:库变大后,"有多少文件"已经不足以判断索引是否可信。
需要能回答——全文/向量索引是否就位、磁盘是否被历史版本撑大、上次索引是否
有文件没进来、结构化快照在不在。

测试重点是**口径正确**:碎片比必须以真实数据量(含向量列)为分母。早先按
"每块 400 字节"估算,把 768 维向量漏掉,2.2 倍的正常索引被误报成 28 倍。
"""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import lancedb
import pyarrow as pa

from backend import library


def _chunks(n: int = 20):
    return [{"uid": f"u{i}", "file": "cat/manual.pdf", "page": i, "category": "cat",
             "model_no": "QMC6309", "text": f"QMC6309 VDD 3.3V block {i}", "md5": "0" * 32}
            for i in range(n)]


class IndexHealthTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db_path = self.root / "index.lance"
        self.db = lancedb.connect(str(self.db_path))
        self.table = self.db.create_table("chunks", data=pa.Table.from_pylist(_chunks()))
        patcher = patch.object(library.config, "DB_PATH", str(self.db_path))
        patcher.start()
        self.addCleanup(patcher.stop)
        settings = self.root / "data" / "settings.json"
        patcher2 = patch.object(library.config, "SETTINGS_FILE", settings)
        patcher2.start()
        self.addCleanup(patcher2.stop)
        self.addCleanup(library.reset_table)

    def test_healthy_index_reports_ok(self):
        self.table.create_fts_index("text", replace=True)
        # 健康判定要求全文与向量索引都在,这里补齐向量分区与索引以模拟真实部署。
        part = self.db.create_table("vec_probe__768__", data=pa.Table.from_pylist(
            [{"uid": f"u{i}", "file": "cat/manual.pdf", "page": i, "category": "cat",
              "model_no": "QMC6309", "vector": [0.01] * 768} for i in range(20)]))
        # 用 IVF_FLAT:默认 IVF_PQ 需要 256 行才能训练,小夹具建不出来。
        part.create_index(metric="cosine", vector_column_name="vector",
                          index_type="IVF_FLAT", num_partitions=1)
        health = library.index_health(self.table)
        self.assertEqual(health["status"], "ok", health["warnings"])
        self.assertEqual(health["rows"], 20)
        self.assertEqual(health["fts_index"], ["text_idx"])
        self.assertEqual(health["warnings"], [])

    def test_missing_fts_index_is_flagged(self):
        health = library.index_health(self.table)
        codes = [w["code"] for w in health["warnings"]]
        self.assertIn("FTS_INDEX_MISSING", codes)
        self.assertEqual(health["status"], "degraded")

    def test_missing_vector_partition_is_flagged(self):
        self.table.create_fts_index("text", replace=True)
        health = library.index_health(self.table)
        codes = [w["code"] for w in health["warnings"]]
        self.assertIn("VECTOR_MISSING", codes)

    def test_fragmentation_uses_real_data_size(self):
        """碎片比的分母必须包含向量列,否则正常索引会被误报。"""
        self.table.create_fts_index("text", replace=True)
        # 建一个带 768 维向量的分区,模拟真实部署
        vec_rows = [{"uid": f"u{i}", "file": "cat/manual.pdf", "page": i,
                     "category": "cat", "model_no": "QMC6309",
                     "vector": [0.01] * 768} for i in range(20)]
        self.db.create_table("vec_probe__768__", data=pa.Table.from_pylist(vec_rows))

        with patch("lancedb.table.Table.to_arrow",
                   side_effect=AssertionError("状态检查不得物化整表")):
            health = library.index_health(self.table)
        self.assertIn("data_bytes", health)
        # 向量数据必须被计入分母:768*4*20 ≈ 61KB,远超文本
        self.assertGreater(health["data_bytes"], 60_000)
        # 正常规模的小索引不应该被判为碎片化
        self.assertNotIn("INDEX_FRAGMENTED", [w["code"] for w in health["warnings"]])

    def test_arrow_size_cache_avoids_repeat_scans(self):
        self.db.create_table("vec_probe__768__", data=pa.Table.from_pylist([
            {"uid": "u0", "file": "cat/manual.pdf", "page": 0, "category": "cat",
             "model_no": "QMC6309", "vector": [0.01] * 768},
        ]))
        with patch.object(library, "_streamed_arrow_bytes",
                          wraps=library._streamed_arrow_bytes) as scan:
            first = library._arrow_bytes(self.table)
            second = library._arrow_bytes(self.table)
        self.assertEqual(first, second)
        self.assertEqual(scan.call_count, 2, "主表和一个分区只应在首次读取时各扫描一次")

    def test_fts_metadata_failure_is_explicitly_degraded(self):
        main = SimpleNamespace(count_rows=lambda: 1, version=1,
                               list_indices=Mock(side_effect=RuntimeError("broken")))
        part = SimpleNamespace(count_rows=lambda: 1,
                               list_indices=lambda: [SimpleNamespace(name="vector_idx")])
        db = SimpleNamespace(list_tables=lambda: SimpleNamespace(tables=["vec_test"]),
                             open_table=lambda name: part)
        with patch("lancedb.connect", return_value=db), patch.object(library, "_arrow_bytes", return_value=None):
            health = library.index_health(main)
        self.assertEqual(health["status"], "degraded")
        self.assertIsNone(health["fts_index"])
        self.assertIsNone(health["data_bytes"])
        self.assertIn("FTS_INDEX_UNAVAILABLE", [w["code"] for w in health["warnings"]])
        self.assertIn("DATA_SIZE_UNAVAILABLE", [w["code"] for w in health["warnings"]])

    def test_unreadable_partition_never_returns_partial_data_size(self):
        main = SimpleNamespace(version=1)
        parts = {name: SimpleNamespace(version=1, uri=name) for name in ("vec_good", "vec_bad")}
        db = SimpleNamespace(list_tables=lambda: SimpleNamespace(tables=list(parts)),
                             open_table=parts.__getitem__)
        with patch("lancedb.connect", return_value=db), patch.object(
                library, "_streamed_arrow_bytes", side_effect=[100, 50, RuntimeError("broken")]):
            self.assertIsNone(library._arrow_bytes(main))

    def test_missing_table_reports_missing(self):
        health = library.index_health(None)
        self.assertEqual(health["status"], "missing")
        self.assertEqual(health["warnings"][0]["code"], "INDEX_MISSING")

    def test_skipped_files_from_history_are_surfaced(self):
        self.table.create_fts_index("text", replace=True)
        history = self.root / "ingest_history.json"
        history.write_text(json.dumps([{
            "time": "2026-11-10T10:00:00", "added": 3, "removed": 0, "chunks": 60,
            "elapsed": 1.5, "skipped": ["a/empty.pdf", "b/scan-only.pdf"], "skipped_omitted": 8}]), encoding="utf-8")
        health = library.index_health(self.table)
        self.assertEqual(health["last_ingest"]["skipped"], 10)
        self.assertEqual(health["last_ingest"]["skipped_omitted"], 8)
        self.assertEqual(health["last_ingest"]["skipped_examples"], ["a/empty.pdf", "b/scan-only.pdf"])
        codes = [w["code"] for w in health["warnings"]]
        self.assertIn("FILES_SKIPPED", codes)
        warning = next(w for w in health["warnings"] if w["code"] == "FILES_SKIPPED")
        self.assertIn("10 个文件", warning["message"])

    def test_no_history_is_not_an_ingest_record(self):
        health = library.index_health(self.table)
        self.assertIsNone(health["last_ingest"])

    def test_health_never_raises_on_broken_paths(self):
        """健康度采集失败不能拖垮 status 接口。"""
        with patch.object(library.config, "DB_PATH", "/nonexistent/path"):
            health = library.index_health(self.table)
        self.assertIn("status", health)
        self.assertIn("warnings", health)


class StatusIntegrationTest(unittest.TestCase):
    def test_status_payload_contains_health(self):
        """status 必须带上 health 字段,否则前端/客户端看不到诊断。"""
        from backend import agent_api

        payload = agent_api.status()
        self.assertIn("health", payload)
        self.assertIn("status", payload["health"])
        self.assertIsInstance(payload["health"]["warnings"], list)


if __name__ == "__main__":
    unittest.main()
