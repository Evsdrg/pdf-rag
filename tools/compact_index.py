# -*- coding: utf-8 -*-
"""索引维护:合并碎片 + 清理历史版本。

增量索引每跑一次都会留下若干新版本(LanceDB 的 MVCC)。长期累积后磁盘占用
会远超真实数据 —— 本仓库实测:8561 块真实数据约 26 MB,而目录 248 MB /
517 个版本 / 1457 个文件,即约 9 倍的开销,同时查询要扫更多碎片。

**不改变任何一行数据**,只是合并小文件、丢掉不再被引用的旧版本。

    uv run python tools/compact_index.py              # 清理 1 小时前的旧版本
    uv run python tools/compact_index.py --dry-run    # 只看现状,不动
    uv run python tools/compact_index.py --keep-hours 24

注意:清理会有极短窗口内旧版本不可读,但服务侧按版本号校验句柄
(见 backend/main.py 与 server.py 的 _TABLE_VERSION),会自动重开最新版本;
清理完仍建议重启后端,让它在最新版本上重新持有句柄。

实现用 `Table.optimize()` —— 等价的 `compact_files()` / `cleanup_old_versions()`
会走 `to_lance()`,在没装 `pylance` 的纯 lancedb 环境里直接 ImportError。
"""
import argparse
import pathlib
import sys
import time
from datetime import timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import lancedb                                          # noqa: E402
from backend import config                              # noqa: E402

TABLE = "chunks"


def stats(path: pathlib.Path) -> tuple[int, int, float]:
    """返回 (文件数, 目录 MB, 版本号)。"""
    files = [p for p in path.rglob("*") if p.is_file()]
    mb = sum(p.stat().st_size for p in files) / 1048576
    t = lancedb.connect(str(path)).open_table(TABLE)
    return len(files), mb, t.version


def main() -> None:
    ap = argparse.ArgumentParser(description="合并索引碎片并清理历史版本")
    ap.add_argument("--dry-run", action="store_true", help="只报告现状,不做修改")
    ap.add_argument("--keep-hours", type=float, default=1.0,
                    help="保留最近多少小时内的版本(默认 1)")
    args = ap.parse_args()

    path = pathlib.Path(config.DB_PATH)
    tbl = lancedb.connect(str(path)).open_table(TABLE)
    rows_before = tbl.count_rows()
    f0, mb0, v0 = stats(path)
    n_idx = [i.name for i in tbl.list_indices()]
    print(f"  现状: {rows_before} 块, {v0} 个版本, {f0} 个文件, {mb0:.0f} MB, "
          f"索引 {n_idx}")
    if args.dry_run:
        print("  (--dry-run,未做修改)")
        return

    t0 = time.time()
    print(f"  合并碎片并清理 {args.keep_hours}h 前的旧版本 ...", end=" ", flush=True)
    tbl.optimize(cleanup_older_than=timedelta(hours=args.keep_hours))
    print(f"{time.time() - t0:.0f}s")

    tbl = lancedb.connect(str(path)).open_table(TABLE)
    rows_after = tbl.count_rows()
    f1, mb1, v1 = stats(path)
    n_idx1 = [i.name for i in tbl.list_indices()]
    print(f"\n  结果: {rows_after} 块, {v1} 个版本, {f1} 个文件, {mb1:.0f} MB "
          f"({mb1 - mb0:+.0f} MB), 索引 {n_idx1}")
    if rows_after != rows_before:
        raise SystemExit(f"!! 行数变了({rows_before} -> {rows_after}),"
                         "数据被动过,请从备份恢复")
    if not n_idx1:
        raise SystemExit("!! FTS 索引丢失,需重建:"
                         " table.create_fts_index('text', replace=True)")
    print("  行数与全文索引均完好 ✓(清理完建议重启后端)")


if __name__ == "__main__":
    main()
