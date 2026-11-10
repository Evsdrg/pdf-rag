"""索引历史必须写入持久数据目录,而不是容器临时层。

线上现象:资料库的“索引历史”一直为空。原因是 ingest/main/library 各自从代码根目录
(/app/ingest_history.json)读写;容器重建后文件消失,运行数据没有进入 data/ 挂载。
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import lancedb
import pyarrow as pa
from fastapi.testclient import TestClient

from backend import config, ingest, library, main


class IngestHistoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db_path = self.root / "index.lance"
        self.settings = self.root / "data" / "settings.json"
        self.patchers = [
            patch.object(config, "DB_PATH", str(self.db_path)),
            patch.object(config, "SETTINGS_FILE", self.settings),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)
        library.reset_table()
        self.addCleanup(library.reset_table)

    def test_history_is_written_under_mounted_data_directory(self):
        ingest._append_history(2, 0, 42, 1.5, [])
        path = library.ingest_history_file()
        self.assertEqual(path, self.settings.parent / "ingest_history.json")
        self.assertTrue(path.exists())
        records = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(records), 1)
        self.assertEqual((records[0]["added"], records[0]["chunks"]), (2, 42))

    def test_legacy_container_history_is_preserved_on_next_write(self):
        legacy = self.root / "ingest_history.json"
        legacy.write_text(json.dumps([{"time": "old", "added": 1, "chunks": 10}]), encoding="utf-8")
        self.assertEqual(library.read_ingest_history()[0]["time"], "old")

        ingest._append_history(3, 0, 60, 2.0, [])
        records = library.read_ingest_history()
        self.assertEqual([r["time"] for r in records][:1], ["old"])
        self.assertEqual(records[-1]["added"], 3)
        self.assertTrue(library.ingest_history_file().exists())
        self.assertEqual(len(records), 2)

    def test_history_is_bounded_and_atomic(self):
        for i in range(105):
            library.append_ingest_history({"time": str(i), "added": 1})
        records = library.read_ingest_history()
        self.assertEqual(len(records), 100)
        self.assertEqual(records[0]["time"], "5")
        self.assertEqual(records[-1]["time"], "104")
        self.assertFalse(list(self.settings.parent.glob("*.tmp")))

    def test_valid_legacy_json_is_also_limited_to_latest_hundred_records(self):
        path = library.ingest_history_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([{"time": str(i)} for i in range(105)]), encoding="utf-8")
        records = library.read_ingest_history()
        self.assertEqual(len(records), library.MAX_INGEST_HISTORY_RECORDS)
        self.assertEqual(records[0]["time"], "5")
        self.assertEqual(records[-1]["time"], "104")

    def test_history_size_is_bounded_by_dropping_oldest_summaries(self):
        for i in range(100):
            library.append_ingest_history({
                "time": f"2026-11-10T10:{i:02}:00", "added": 1,
                "skipped": [f"category-{i}/manual-{j}.pdf" for j in range(100)],
            })
        path = library.ingest_history_file()
        self.assertLessEqual(path.stat().st_size, library.MAX_INGEST_HISTORY_BYTES)
        records = library.read_ingest_history()
        self.assertLessEqual(len(records), library.MAX_INGEST_HISTORY_RECORDS)
        self.assertEqual(records[-1]["time"], "2026-11-10T10:99:00")

    def test_single_large_record_keeps_counts_and_bounds_path_list(self):
        ingest._append_history(1, 0, 1, 0.5, ["x" * 512] * 2000)
        path = library.ingest_history_file()
        self.assertLessEqual(path.stat().st_size, library.MAX_INGEST_HISTORY_BYTES)
        record = library.read_ingest_history()[-1]
        self.assertEqual(record["added"], 1)
        self.assertEqual(len(record["skipped"]), library.MAX_INGEST_SKIPPED)
        self.assertEqual(record["skipped_omitted"], 2000 - library.MAX_INGEST_SKIPPED)
        # 再入库一次后,已省略的数量不能被重复归一化弄丢。
        ingest._append_history(2, 0, 2, 0.3, [])
        self.assertEqual(library.read_ingest_history()[0]["skipped_omitted"],
                         2000 - library.MAX_INGEST_SKIPPED)

    def test_oversized_or_corrupt_json_is_not_partially_parsed(self):
        path = library.ingest_history_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'[' + b'x' * (library.MAX_INGEST_HISTORY_BYTES + 1))
        self.assertEqual(library.read_ingest_history(), [])
        path.write_text('{"not": "a list"}', encoding="utf-8")
        self.assertEqual(library.read_ingest_history(), [])
        path.write_text('[{"time": "ok"},', encoding="utf-8")
        self.assertEqual(library.read_ingest_history(), [])

    def test_non_finite_numbers_do_not_produce_nonstandard_json(self):
        library.write_ingest_history([{"time": "x", "elapsed": float("nan"), "added": 1}])
        raw = library.ingest_history_file().read_text(encoding="utf-8")
        self.assertNotIn("NaN", raw)
        self.assertNotIn("elapsed", json.loads(raw)[0])

    def test_stats_endpoint_reads_persistent_history(self):
        db = lancedb.connect(str(self.db_path))
        db.create_table("chunks", data=pa.Table.from_pylist([
            {"file": "cat/a.pdf", "category": "cat", "model_no": "M1", "c_id": "",
             "version": "", "md5": "x", "page": 1, "text": "text"},
        ]))
        ingest._append_history(1, 0, 1, 0.2, [])
        with TestClient(main.app) as client:
            response = client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["history"]), 1)
        self.assertEqual(payload["history"][0]["added"], 1)
        self.assertEqual(payload["files"], 1)


if __name__ == "__main__":
    unittest.main()
