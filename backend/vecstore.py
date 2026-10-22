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
import logging
import re
import time

import pyarrow as pa

from . import config

log = logging.getLogger("pdfrag.vecstore")

META_TABLE = "vec_meta"
UID_LEN = 20


# ---------- uid ----------

def make_uid(file: str, page: int, seq: int) -> str:
    """块级稳定标识:文件名 + 页号(0-based) + 页内块序号。

    不能把 text 也算进哈希:实测现有 8561 块里有 9 个碰撞(同页存在逐字相同的块),
    会让不同块互相覆盖。块序是提取阶段的确定性输出,加上它即唯一。

    唯一性由 (file, page, seq) 保证 —— 同一文件的同一页里,seq 从 0 递增,
    因此同页逐字相同的块也能区分开。
    """
    raw = f"{file}\x00{page}\x00{seq}".encode()
    return hashlib.sha256(raw).hexdigest()[:UID_LEN]


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
    不是 list —— 直接 `in` 判断会永远为假(踩过:迁移脚本误判"主表不存在",
    数据包导出在空库上直接抛 ValueError)。实现收敛到 library,避免两处漂移。
    """
    from . import library
    return library.db_table_names(db)


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


# ---------- 向量索引 ----------
# 建 IVF_FLAT 索引后,分区检索从"全表暴力扫描"变成"先定位若干簇再精算"。
# 实测(8561 块 / 768 维 / limit=80):25.1ms → 12.1ms;固定开销 15.1ms → 2.3ms。
#
# 为什么配 refine_factor:IVF 只搜最近的一小部分簇,真实近邻可能落在没搜的簇里,
# 表现为**静默漏召回**。refine_factor 让索引先取 rf×k 个候选,再对这批候选做
# 精确距离重算,把漏掉的捞回来。实测 nlist=16 时:
#   rf=1(默认): 400 条查询 x top80 漏 17 条(召回 0.99947)
#   rf=2       : 漏 0 条(召回 1.0),代价 +2ms
# 参数必须按数据规模实测,不能按索引类型名假设"无损" —— nlist=128/256 时
# 即使 rf=2 也开始漏(78/80、73/80)。

# 索引参数。nlist=16 对应本库 ~500 行/簇;数据量显著增长时应重测。
IVF_PARTITIONS = 16
# 查询侧精算倍数。小于 2 会漏召回,大于 2 只增加代价不再提升召回(实测)。
REFINE_FACTOR = 2
# 低于该行数不建索引。Lance 的 KMeans 在 40 行上会警告 "40 < 4096" 并产出
# 大量空簇,此时索引结果与暴力扫描**完全不一致**(实测 top10 无一相同),
# 而暴力扫描在几千行内本来就只要 20ms 上下 —— 小库建索引是纯亏。
MIN_ROWS_FOR_INDEX = 4096


def has_vector_index(table) -> bool:
    """分区是否已有向量索引。没有时检索仍正确,只是退化为暴力扫描。"""
    try:
        return any(i.index_type != "FTS" for i in table.list_indices())
    except Exception:
        return False


def ensure_vector_index(table, replace: bool = False) -> bool:
    """给分区建向量索引。返回是否真的建了(已存在且不 replace 时返回 False)。

    索引纯属加速:建不成、或数据太小不值得建,都应返回 False 而不影响主流程。
    调用方据此决定查询侧是否加 refine_factor —— **没有索引绝对不能加**,
    否则 refine 会作用在暴力扫描结果上,行为未定义。
    """
    if not replace and has_vector_index(table):
        return False
    try:
        rows = table.count_rows()
        if rows < MIN_ROWS_FOR_INDEX:
            return False
        import lancedb.index as LI
        table.create_index("vector",
                           config=LI.IvfFlat(distance_type="cosine",
                                             num_partitions=IVF_PARTITIONS),
                           replace=replace)
        return True
    except Exception as e:                      # 索引是可选加速,不能让主流程失败
        log.warning("建向量索引失败(将退化为暴力扫描): %s", e)
        return False


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
