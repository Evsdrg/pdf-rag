"""在隔离目录测量实体索引冷建与快照恢复,不碰真实运行快照。"""
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from backend import config, entity


def measure_entity_cache(table, rounds: int = 3) -> tuple[list[float], list[float]]:
    """返回 (真实冷建毫秒, 快照恢复毫秒);每轮冷建都从无快照开始。"""
    if rounds < 1:
        raise ValueError("测量轮数必须为正数")
    cold, snapshot_load = [], []
    try:
        with tempfile.TemporaryDirectory(prefix="pdf-rag-entity-bench-") as tmp, \
                patch.object(config, "SETTINGS_FILE", Path(tmp) / "settings.json"):
            for _ in range(rounds):
                entity.reset_cache(clear_snapshot=True)
                start = time.perf_counter()
                entity.get_index(table)
                cold.append((time.perf_counter() - start) * 1000)
            for _ in range(rounds):
                entity.reset_cache()
                start = time.perf_counter()
                entity.get_index(table)
                snapshot_load.append((time.perf_counter() - start) * 1000)
    finally:
        # 临时目录已卸载,清掉其中的内存缓存;默认不删真实快照。
        entity.reset_cache()
    return cold, snapshot_load
