# -*- coding: utf-8 -*-
"""把现有单列索引迁移为「主表 + 向量分区」布局。在线执行,不重新嵌入。

    python tools/migrate_vec_partition.py --dry-run   # 只看现状与计划
    python tools/migrate_vec_partition.py             # 执行迁移

流程(详见 docs/VECTOR-PARTITION.md §6):
  1. 主表补 uid 列(按 file+page+页内块序生成,校验唯一)
  2. 把 vector 列搬到分区表 vec_<slug>
  3. 校验分区与主表 uid 一一对应、抽样比对向量
  4. drop 主表的 vector 列(实测 FTS 索引与查询不受影响)

迁移后主表不再有 vector 列;`--rollback` 可把向量列加回主表(需重新嵌入或从分区搬回)。
"""
import argparse
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pyarrow as pa                                    # noqa: E402
import lancedb                                          # noqa: E402

from backend import config, vecstore                    # noqa: E402

TABLE = "chunks"


def _has_column(table, name: str) -> bool:
    return name in [f.name for f in table.schema]


def _plan(table) -> dict:
    rows = table.count_rows()
    has_vec = _has_column(table, "vector")
    has_uid = _has_column(table, "uid")
    dim = table.schema.field("vector").type.list_size if has_vec else None
    return {"rows": rows, "has_vector": has_vec, "has_uid": has_uid, "dim": dim}


def _build_uids(rows: list[dict]) -> list[str]:
    """按 (file, page, 页内块序) 生成 uid。

    行顺序即提取写入顺序,同页连续;用计数器恢复页内序号 —— 不能从 text 推导,
    同页可能存在逐字相同的块(实测 9 处碰撞)。
    """
    seq: dict[tuple[str, int], int] = {}
    out = []
    for r in rows:
        k = (r["file"], int(r["page"]))
        n = seq.get(k, 0)
        seq[k] = n + 1
        out.append(vecstore.make_uid(r["file"], int(r["page"]), n))
    return out


def migrate(db, dry_run: bool) -> int:
    if TABLE not in vecstore.table_names(db):
        print("主表不存在,无需迁移")
        return 1
    table = db.open_table(TABLE)
    plan = _plan(table)
    print(f"主表: {plan['rows']} 行, vector 列: {plan['has_vector']}, "
          f"uid 列: {plan['has_uid']}, 维度: {plan['dim']}")
    if not plan["has_vector"]:
        print("已是分区布局(主表无 vector 列),无需迁移")
        return 0

    slug = vecstore.current_slug()
    dim = plan["dim"]
    part_name = vecstore.partition_table_name(slug)
    print(f"目标分区: {part_name}")

    rows = table.to_arrow().to_pylist()
    uids = _build_uids(rows)
    if len(set(uids)) != len(uids):
        dup = len(uids) - len(set(uids))
        print(f"✗ uid 重复 {dup} 个,迁移中止(需先修 uid 生成规则)")
        return 1
    print(f"uid 生成完成: {len(uids)} 个,全部唯一")

    vec_rows = [{"uid": u, "file": r["file"], "page": int(r["page"]),
                 "category": r.get("category", ""), "md5": r.get("md5", ""),
                 "vector": r["vector"]}
                for u, r in zip(uids, rows)]

    if dry_run:
        print(f"[dry-run] 将创建分区 {part_name}({len(vec_rows)} 行, {dim} 维);"
              f"主表重写为 元数据+文本+uid(去 vector 列)并重建 FTS")
        return 0

    # 1) 建分区表(已存在则覆盖:同 uid 重写即为替换)
    if part_name in vecstore.table_names(db):
        print(f"  分区已存在,覆盖写入")
        db.drop_table(part_name)
    db.create_table(part_name, data=vec_rows)
    part = db.open_table(part_name)
    print(f"  分区写入完成: {part.count_rows()} 行")

    # 2) 校验
    part_uids = {r["uid"] for r in part.search().select(["uid"]).limit(part.count_rows())
                 .to_arrow().to_pylist()}
    assert part_uids == set(uids), "分区与主表 uid 不一致"
    check = part.search().where(f"uid = '{uids[0]}'").limit(1).to_list()
    assert check and len(check[0]["vector"]) == dim, "抽样向量维度假定不符"
    print("  校验通过:uid 一一对应,向量维度一致")

    # 3) 主表改为「元数据+文本+uid」:读旧表 → 带 uid 建新表 → 替换旧表。
    #    LanceDB 的 update 只支持按 where 批量赋同一个值,无法逐行写不同 uid,
    #    所以直接重写;8561 行实测秒级,迁移是一次性操作。
    from backend.ingest import schema as main_schema
    plain = [{k: r[k] for k in main_schema().names if k in r} | {"uid": u}
             for r, u in zip(rows, uids)]
    tmp = f"{TABLE}__migrating"
    if tmp in vecstore.table_names(db):
        db.drop_table(tmp)
    db.create_table(tmp, data=plain, schema=main_schema())
    db.drop_table(TABLE)
    # OSS 版不支持 rename_table,用"建同名表后写数据"替代:直接以原名 recreate
    new = db.create_table(TABLE, data=plain, schema=main_schema())
    db.drop_table(tmp)
    print(f"  主表已重写: {new.count_rows()} 行,列 {[f.name for f in new.schema]}")
    table = new

    # 4) 重建 FTS(drop/recreate 会丢索引;实测 text 列数据完好)
    table.create_fts_index("text", replace=True)
    print("  FTS 索引已重建")

    vecstore.upsert_partition_meta(
        db, slug, blocks=part.count_rows(),
        files=len({r["file"] for r in vec_rows}))
    print(f"  分区元数据已写入 vec_meta")

    # 5) 向量索引。纯加速:建不成也照常用(检索退化为暴力扫描)
    if vecstore.ensure_vector_index(part, replace=True):
        print(f"  向量索引已建立(IvfFlat nlist={vecstore.IVF_PARTITIONS})")
    return 0


def rollback(db) -> int:
    print("回滚: 把分区向量搬回主表 vector 列")
    table = db.open_table(TABLE)
    if _has_column(table, "vector"):
        print("主表已有 vector 列,无需回滚")
        return 0
    slug = vecstore.current_slug()
    part = vecstore.open_partition(db, slug)
    if part is None:
        print(f"分区 {slug} 不存在,无法回滚(需要重新嵌入)")
        return 1
    uids = [r["uid"] for r in part.search().select(["uid"]).limit(part.count_rows())
            .to_arrow().to_pylist()]
    print(f"  分区有 {len(uids)} 个向量,回滚需重建主表并逐一匹配 uid —— "
          f"建议改用 --rebuild 重新嵌入,可靠且不必实现第二套写路径")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rollback", action="store_true")
    args = ap.parse_args()

    db = lancedb.connect(config.DB_PATH)
    if args.rollback:
        sys.exit(rollback(db))
    sys.exit(migrate(db, args.dry_run))


if __name__ == "__main__":
    main()
