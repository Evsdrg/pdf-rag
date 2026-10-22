# -*- coding: utf-8 -*-
"""给已有分区补建向量索引(或重建)。

索引纯属加速:没有它检索照样正确,只是退化为全表暴力扫描。本地部署小模型时
嵌入只要几十毫秒,暴力扫描的 20ms 就从"零头"变成"主项",这时值得建。

    python tools/build_vec_index.py            # 缺索引的分区建,已有的跳过
    python tools/build_vec_index.py --rebuild  # 全部重建(数据大改后用)

参数见 backend/vecstore.py 的 IVF_PARTITIONS / REFINE_FACTOR。
"""
import argparse
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import lancedb                                          # noqa: E402

from backend import config, vecstore                    # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true",
                    help="已有索引也重建(默认跳过)")
    args = ap.parse_args()

    db = lancedb.connect(config.DB_PATH)
    metas = vecstore.list_partitions(db)
    if not metas:
        print("没有向量分区,先跑一次索引")
        return 1

    for m in metas:
        slug = m["slug"]
        part = vecstore.open_partition(db, slug)
        if part is None:
            print(f"[跳过] {slug}: 分区表不存在")
            continue
        had = vecstore.has_vector_index(part)
        if had and not args.rebuild:
            print(f"[跳过] {slug}: 已有索引(如需重建加 --rebuild)")
            continue
        t0 = time.time()
        ok = vecstore.ensure_vector_index(part, replace=True)
        dt = time.time() - t0
        if ok:
            print(f"[完成] {slug}: {part.count_rows()} 行, 耗时 {dt:.1f}s"
                  f"(nlist={vecstore.IVF_PARTITIONS})")
        else:
            print(f"[失败] {slug}: 见上方日志;检索仍可用,会走暴力扫描")
    return 0


if __name__ == "__main__":
    sys.exit(main())
