"""向量分区:按「模型 + 维度 + 建库 input_type」把向量分表存放。

背景与完整设计见 `docs/VECTOR-PARTITION.md`。这里只强调三条实现约定:

* **主表不再有 vector 列**。元数据与文本在 `chunks`,`text` 上建 FTS;向量在
  `vec_<slug>` 分区表里。这样换模型不必动主表,也不会让不同模型的向量混在一列。
* **分区可以只覆盖部分块**。覆盖率不足时向量通道要响亮降级,不能静默缩小候选池。
* **查询向量必须与分区契约成对**:分区记录了建库时的 `model/dim/input_type`,
  查询侧用该分区的 `input_type_query` 生成向量,而不是用当前全局配置。

分区表结构: `(uid, file, page, category, md5, vector[d])`。
冗余存 file/page/category/md5 是为了把过滤下推到分区(实测带 category 过滤 37.9ms),
避免"先检索再回表再过滤"。
"""
import hashlib
import json
import os
import re
import time

import pyarrow as pa

from . import config

META_TABLE = "vec_meta"
UID_LEN = 20


# ---------- uid ----------

def make_uid(file: str, page: int, seq: int) -> str:
    """块级稳定标识:文件名 + 页号(0-based) + 页内块序号。

    不能把 text 也算进哈希:实测现有 8561 块里有 9 个碰撞(同页存在逐字相同的块),
    会让不同块互相覆盖。块序是提取阶段的确定性输出,加上它即唯一。
    """
    raw = f"{file}\x00{page}\x00{seq}".encode()
    return hashlib.sha256(raw).hexdigest()[:UID_LEN]


def chunk_uids(file: str, page: int, count: int) -> list[str]:
    """某页 count 个块的 uid 序列(按页内顺序)。"""
    return [make_uid(file, page, i) for i in range(count)]


# ---------- slug ----------

def model_slug(model: str, dim: int | None, input_type_doc: str = "") -> str:
    """分区标识: `<model>__<dim>__<input_type_doc>`。

    input_type 必须参与:Cohere 系同一模型用 `search_document` 与留空产出不同空间的
    向量,只按模型名区分会让两个契约的向量混进同一分区。留空时末段为空,保持可读。
    """
    safe = re.sub(r"[^0-9A-Za-z]+", "_", str(model)).strip("_").lower() or "model"
    it = re.sub(r"[^0-9A-Za-z]+", "_", str(input_type_doc)).strip("_").lower()
    return f"{safe}__{dim or 0}__{it}"


def partition_table_name(slug: str) -> str:
    return f"vec_{slug}"


def current_slug() -> str:
    """当前配置对应的分区 slug。"""
    return model_slug(str(config.get("embed_model")),
                      config.get("embed_dimensions"),
                      str(config.get("embed_input_type_doc") or ""))


def _split_csv(raw) -> list[str]:
    return [s.strip() for s in str(raw or "").split(",") if s.strip()]


def select_partitions(db) -> list[dict]:
    """按优先级/排除配置挑出本次检索可用的分区,按优先级排序。

    语义(见 docs/VECTOR-PARTITION.md §3.3):
    * 一项可写分区 slug,也可写模型名(匹配该模型的任意分区,含不同 input_type)。
    * 排除优先于优先级:同时出现在两边时以排除为准(fail-closed)。
    * 优先级留空 = 只用当前配置对应的那个分区。
    * 每次检索中,一个块只用一个模型的向量 —— 调用方按返回顺序依次检索,
      同一块在靠前分区命中后就不再消费靠后分区的结果。

    返回 vec_meta 行(含 slug/model/dim/input_type_query),不存在的分区被跳过。
    """
    metas = {m["slug"]: m for m in list_partitions(db)}
    if not metas:
        return []

    def match(term: str) -> list[dict]:
        return [m for s, m in metas.items() if term == s or term == m.get("model")]

    excluded = {m["slug"] for term in _split_csv(config.get("vector_models_exclude"))
                for m in match(term)}

    order = _split_csv(config.get("vector_models_priority"))
    picked: list[dict] = []
    seen: set[str] = set()
    if order:
        for term in order:
            for m in match(term):
                if m["slug"] in excluded or m["slug"] in seen:
                    continue
                picked.append(m)
                seen.add(m["slug"])
    else:
        cur = current_slug()
        m = metas.get(cur)
        if m is not None and cur not in excluded:
            picked.append(m)
    return picked


# ---------- 分区元数据 ----------

_META_SCHEMA = pa.schema([
    ("slug", pa.string()),
    ("model", pa.string()),
    ("dim", pa.int32()),
    ("input_type_doc", pa.string()),
    ("input_type_query", pa.string()),
    ("base_url", pa.string()),
    ("created_at", pa.string()),
    ("updated_at", pa.string()),
    ("blocks", pa.int64()),
    ("files", pa.int64()),
])


def table_names(db) -> list[str]:
    """库里已有的表名列表。

    LanceDB 0.36 的 `list_tables()` 返回 ListTablesResponse(带 .tables 属性),
    不是 list —— 直接 `in` 判断会永远为假(踩过:迁移脚本误判"主表不存在")。
    """
    res = db.list_tables()
    return list(getattr(res, "tables", res))


def _meta_table(db, create: bool = False):
    names = table_names(db)
    if META_TABLE in names:
        return db.open_table(META_TABLE)
    if not create:
        return None
    return db.create_table(META_TABLE, schema=_META_SCHEMA)


def list_partitions(db) -> list[dict]:
    """全部分区元数据(按创建时间倒序)。vec_meta 不存在时返回空。"""
    t = _meta_table(db)
    if t is None or t.count_rows() == 0:
        return []
    rows = t.search().select(list(_META_SCHEMA.names)).limit(t.count_rows()).to_arrow().to_pylist()
    return sorted(rows, key=lambda r: r.get("created_at") or "", reverse=True)


def get_partition_meta(db, slug: str) -> dict | None:
    for r in list_partitions(db):
        if r["slug"] == slug:
            return r
    return None


def upsert_partition_meta(db, slug: str, *, blocks: int | None = None,
                          files: int | None = None, **fields) -> dict:
    """写入/更新分区元数据。不存在则插入,存在则删旧行后插入(单行表,无需 update)。"""
    t = _meta_table(db, create=True)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    cur = get_partition_meta(db, slug) or {}
    row = {
        "slug": slug,
        "model": fields.get("model", cur.get("model", str(config.get("embed_model")))),
        "dim": fields.get("dim", cur.get("dim", config.get("embed_dimensions"))),
        "input_type_doc": fields.get("input_type_doc",
                                     cur.get("input_type_doc",
                                             str(config.get("embed_input_type_doc") or ""))),
        "input_type_query": fields.get("input_type_query",
                                       cur.get("input_type_query",
                                               str(config.get("embed_input_type_query") or ""))),
        "base_url": fields.get("base_url", cur.get("base_url",
                                                   str(config.get("embed_base_url")))),
        "created_at": cur.get("created_at") or now,
        "updated_at": now,
        "blocks": blocks if blocks is not None else cur.get("blocks", 0),
        "files": files if files is not None else cur.get("files", 0),
    }
    t.delete(f"slug = '{slug}'")
    t.add([row])
    return row


def drop_partition(db, slug: str) -> bool:
    """删除分区表与元数据行。返回是否真的删了表。"""
    name = partition_table_name(slug)
    names = table_names(db)
    existed = name in names
    if existed:
        db.drop_table(name)
    t = _meta_table(db)
    if t is not None:
        t.delete(f"slug = '{slug}'")
    return existed


# ---------- 分区表 ----------

def _vec_schema(dim: int) -> pa.schema:
    return pa.schema([
        pa.field("uid", pa.string()),
        pa.field("file", pa.string()),
        pa.field("page", pa.int32()),
        pa.field("category", pa.string()),
        pa.field("md5", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), dim)),
    ])


def open_partition(db, slug: str):
    """打开分区表;不存在返回 None。"""
    name = partition_table_name(slug)
    if name not in table_names(db):
        return None
    return db.open_table(name)


def ensure_partition(db, slug: str, dim: int):
    """打开或创建分区表。维度不符时抛 ValueError(不同维度的向量不能同表)。"""
    t = open_partition(db, slug)
    if t is None:
        return db.create_table(partition_table_name(slug), schema=_vec_schema(dim))
    have = t.schema.field("vector").type.list_size
    if have != dim:
        raise ValueError(f"分区 {slug} 维度为 {have},与请求的 {dim} 不符")
    return t


def add_rows(table, rows: list[dict]) -> None:
    table.add(rows) if rows else None


def delete_file(table, file: str) -> None:
    table.delete(f"file = '{file.replace(chr(39), chr(39) * 2)}'")


# ---------- 覆盖率 ----------

def coverage(db, main_table, slug: str) -> dict:
    """分区对主表的覆盖情况。**按块统计**——向量化的输入单位就是块。

    同一文件可能只有部分块有向量(限流中断、按块补算),按文件统计会把这种缺口
    四舍五入掉。降级判定只看 blocks 覆盖率;files 与 partial 仅供展示与调度参考。
    """
    from . import library
    main = library.scan_columns(main_table, ["uid", "file"])
    part = open_partition(db, slug)
    if part is None:
        return {"slug": slug, "exists": False, "blocks_covered": 0,
                "blocks_total": len(main), "files_covered": 0, "files_total": 0,
                "files_partial": 0, "ratio": 0.0}
    uids = {r["uid"] for r in part.search().select(["uid"]).limit(part.count_rows())
            .to_arrow().to_pylist()} if "uid" in [f.name for f in part.schema] else set()
    main_uids = {r["uid"] for r in main}
    covered = main_uids & uids
    files_total = len({r["file"] for r in main})
    files_covered = len({r["file"] for r in main if r["uid"] in covered})
    # 部分覆盖:该文件有块但没全覆盖
    per_file_total: dict[str, int] = {}
    per_file_cov: dict[str, int] = {}
    for r in main:
        per_file_total[r["file"]] = per_file_total.get(r["file"], 0) + 1
        if r["uid"] in covered:
            per_file_cov[r["file"]] = per_file_cov.get(r["file"], 0) + 1
    partial = sum(1 for f, n in per_file_cov.items() if n < per_file_total.get(f, 0))
    return {
        "slug": slug, "exists": True,
        "blocks_covered": len(covered), "blocks_total": len(main_uids),
        "files_covered": files_covered, "files_total": files_total,
        "files_partial": partial,
        "ratio": (len(covered) / len(main_uids)) if main_uids else 1.0,
    }
