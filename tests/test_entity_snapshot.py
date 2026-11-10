"""实体索引快照的回归测试。

背景(2026-11-10 规模化分析):构建一次实体索引在真实规模上要数秒到数十秒
(8561 块约 2s,25k 块约 7.7s,1000 手册量级约 23s),而反序列化只要十几毫秒。
快照把"每次索引后首次 structured 查询"的等待从数十秒降到毫秒级。

风险不在速度而在**陈旧数据**:表内容变了却复用旧索引,会让检索结果与主表不一致。
所以这里重点测版本绑定、损坏回退和原子写入,而不是只测"能存能读"。
"""
import pickle
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import lancedb
import pyarrow as pa

from backend import entity
from tools.entity_cache_benchmark import measure_entity_cache


def _rows(tag: str, n: int = 3):
    return [{"uid": f"{tag}-{i}", "file": f"{tag}/manual.pdf", "page": i + 1,
             "category": "01_传感器", "model_no": f"QMC6309{tag}",
             "text": f"QMC6309 VDD supply voltage {i} 3.3V"}
            for i in range(n)]


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # 快照路径由 config.SETTINGS_FILE 的父目录决定,这里改到临时目录。
        self.settings = self.root / "data" / "settings.json"
        patcher = patch("backend.config.SETTINGS_FILE", self.settings)
        patcher.start()
        self.addCleanup(patcher.stop)
        entity.reset_cache(clear_snapshot=True)
        self.addCleanup(entity.reset_cache, True)

        self.db = lancedb.connect(str(self.root / "db"))
        self.table = self.db.create_table("chunks", data=pa.Table.from_pylist(_rows("A")))
    def test_snapshot_is_written_and_reused(self):
        first = entity.get_index(self.table)
        self.assertTrue(entity.cache_path().exists(), "构建后应写出快照")

        # 清掉内存缓存但保留快照:应当从磁盘恢复,内容一致
        entity.reset_cache(clear_snapshot=False)
        with patch.object(entity, "_release_heap") as release:
            second = entity.get_index(self.table)
        release.assert_called_once_with()
        self.assertEqual(second.table_version, first.table_version)
        self.assertEqual(set(second.entities_by_uid), set(first.entities_by_uid))
        self.assertEqual(second.by_entity, first.by_entity)
        self.assertEqual(second.metadata_by_uid, first.metadata_by_uid)

    def test_cache_benchmark_separates_rebuilds_and_preserves_real_snapshot(self):
        entity.get_index(self.table)
        original = entity.cache_path().read_bytes()
        with patch.object(entity, "build", wraps=entity.build) as build:
            cold, snapshot_load = measure_entity_cache(self.table, rounds=2)
        self.assertEqual((len(cold), len(snapshot_load)), (2, 2))
        self.assertEqual(build.call_count, 2, "两轮快照恢复不应再次构建索引")
        self.assertEqual(entity.cache_path().read_bytes(), original)

    def test_stale_version_snapshot_is_rejected(self):
        """表内容变了(版本号变化),旧快照必须被拒绝并重建。"""
        entity.get_index(self.table)
        snapshot = pickle.loads(entity.cache_path().read_bytes())
        self.assertEqual(snapshot["table_version"], int(self.table.version))

        # 写入新数据使版本前进
        self.table.add(_rows("B"))
        new_version = int(self.table.version)
        self.assertNotEqual(new_version, snapshot["table_version"])

        entity.reset_cache(clear_snapshot=False)
        index = entity.get_index(self.table)
        self.assertEqual(index.table_version, new_version)
        # 新数据必须出现在索引里,证明没有复用旧快照
        self.assertTrue(any(uid.startswith("B-") for uid in index.entities_by_uid),
                        "重建后的索引应包含新行")

    def test_corrupt_snapshot_falls_back_to_rebuild(self):
        entity.get_index(self.table)
        entity.cache_path().write_bytes(b"not a pickle at all")
        entity.reset_cache(clear_snapshot=False)
        index = entity.get_index(self.table)
        self.assertEqual(len(index.entities_by_uid), 3)

    def test_unknown_cache_version_is_rejected(self):
        entity.get_index(self.table)
        payload = pickle.loads(entity.cache_path().read_bytes())
        payload["cache_version"] = entity._CACHE_VERSION + 99
        entity.cache_path().write_bytes(pickle.dumps(payload))
        entity.reset_cache(clear_snapshot=False)
        index = entity.get_index(self.table)
        self.assertEqual(len(index.entities_by_uid), 3)

    def test_snapshot_write_failure_does_not_break_search(self):
        """磁盘不可写时只损失速度,不能影响正确性。"""
        with patch.object(entity, "_save_snapshot", side_effect=OSError("disk full")):
            index = entity.get_index(self.table)
        self.assertEqual(len(index.entities_by_uid), 3)

    def test_no_temp_file_left_behind(self):
        entity.get_index(self.table)
        leftovers = list(entity.cache_path().parent.glob("*.tmp"))
        self.assertEqual(leftovers, [], f"不应残留临时文件: {leftovers}")

    def test_reset_with_clear_removes_snapshot(self):
        entity.get_index(self.table)
        self.assertTrue(entity.cache_path().exists())
        entity.reset_cache(clear_snapshot=True)
        self.assertFalse(entity.cache_path().exists())


class IndexLimitTest(unittest.TestCase):
    """上限值必须与"1000+ 手册"的规模目标匹配。

    旧值 5 万行在约 660 个同规模手册就会拒绝,使 structured 静默降级。
    """

    def test_row_limit_covers_thousand_manual_target(self):
        # 线上实测 75.3 块/文件;1000 手册约 75,300 块。
        blocks_for_1000_manuals = 75_300
        self.assertGreater(entity.MAX_INDEX_ROWS, blocks_for_1000_manuals,
                           "上限必须能容纳 1000 手册的目标规模")

    def test_limits_are_internally_consistent(self):
        # 链接数上限不应比行数上限更早触发(平均每块多个实体是常态)
        self.assertGreaterEqual(entity.MAX_INDEX_LINKS, entity.MAX_INDEX_ROWS)
        self.assertGreater(entity.MAX_INDEX_BYTES, 0)

    def test_release_heap_is_safe_when_unavailable(self):
        """没有 malloc_trim 的平台不能抛异常。"""
        with patch("ctypes.CDLL", side_effect=OSError("no libc")):
            entity._release_heap()   # 不应抛出


if __name__ == "__main__":
    unittest.main()
