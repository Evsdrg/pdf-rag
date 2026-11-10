"""共享索引句柄、元数据聚合、参数解析与领域错误;读取入口在 agent_documents。"""
import json
import os
import re
from pathlib import Path

from . import config, doc_utils


class LibraryError(Exception):
    """可预期的调用错误,同时返回稳定错误码与安全文案。"""

    status = 400
    code = "INVALID_ARGUMENT"

    def __init__(self, message: str, *, code: str | None = None, details: dict | None = None):
        super().__init__(message)
        self.code = code or self.code
        self.details = details or {}


class NotFound(LibraryError):
    """目标文件不存在 —— HTTP 侧映射成 404。"""

    status = 404
    code = "FILE_NOT_FOUND"


# ---------- 连接与表句柄(两侧共用) ----------

_DB_CACHE = None
_TABLE_CACHE = None
_TABLE_VERSION = -1


def get_db():
    """LanceDB 连接单例:避免每个请求/工具调用重复 connect。

    注意 lance 的 DBConnection 本身开销不大,但重复创建会让句柄与内部缓存
    反复重建;单例是两侧原本就该有的一致性。

    判定"库非空"必须看表名列表而不是 `if db.list_tables():` —— 后者返回
    `ListTablesResponse` 对象,空库时 `bool()` 依然为真(实测),那样这层
    保护形同虚设,后面 open_table 直接抛异常。
    """
    global _DB_CACHE
    if not os.path.isdir(config.DB_PATH):
        return None
    if _DB_CACHE is None:
        import lancedb
        db = lancedb.connect(config.DB_PATH)
        if "chunks" in db_table_names(db):
            _DB_CACHE = db
    return _DB_CACHE


def db_table_names(db) -> list[str]:
    """库内表名列表(LanceDB 0.36 的 list_tables() 返回对象,不是 list)。

    放在 library 而非 vecstore:vecstore 依赖 library(取 scan_columns 等),
    反向导入会成环。
    """
    res = db.list_tables()
    return list(getattr(res, "tables", res))


def get_table():
    """表句柄单例;按 manifest 版本检测跨进程写入(ingest 增删)并自动重开。

    版本相等即句柄有效 —— 曾额外跑 `to_arrow().num_rows` 做"有效性探测",
    实为把整表(含向量列)物化进内存只为读一个行数(8.5k 行 37ms),且每个请求
    都付这笔开销。manifest 比对本身已足够。

    索引不存在时返回 None(HTTP 侧据此返回空结果;MCP 侧由调用方转成错误)。
    """
    global _TABLE_CACHE, _TABLE_VERSION
    db = get_db()
    if db is None:
        return None
    try:
        fresh = db.open_table("chunks")  # 轻量:仅读最新 manifest/schema
        if _TABLE_CACHE is not None and _TABLE_VERSION == fresh.version:
            return _TABLE_CACHE
        _TABLE_CACHE = fresh
        _TABLE_VERSION = fresh.version
        return _TABLE_CACHE
    except Exception:
        _TABLE_CACHE = None
        _TABLE_VERSION = -1
        return None


def reset_table():
    """丢弃缓存的连接与句柄(数据包导入替换索引后必须调用)。

    替换 `index.lance` 目录后,旧句柄指向已删除的 inode;不重置会一直读到旧数据。
    """
    global _DB_CACHE, _TABLE_CACHE, _TABLE_VERSION
    _DB_CACHE = None
    _TABLE_CACHE = None
    _TABLE_VERSION = -1


def source_inventory(indexed: list[dict]) -> dict:
    """只扫描文件名,对比源目录与索引;不读取手册正文,不访问上游。"""
    root = os.path.realpath(config.PDF_ROOT)
    if not os.path.isdir(root):
        raise LibraryError("源手册目录不可读", code="SOURCE_UNAVAILABLE")
    source = {}

    def fail(error):
        raise error

    try:
        for directory, _, names in os.walk(root, onerror=fail):
            for name in names:
                kind = "md" if doc_utils.is_markdown(name) else "pdf" if name.lower().endswith(".pdf") else ""
                if not kind:
                    continue
                full = os.path.join(directory, name)
                if not os.path.isfile(full):
                    continue
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                source[rel] = kind
    except OSError:
        raise LibraryError("源手册目录扫描失败", code="SOURCE_UNAVAILABLE") from None
    indexed_paths = {item["file"].replace("\\", "/"): item["kind"] for item in indexed}
    unindexed = sorted(set(source) - set(indexed_paths))
    missing = sorted(set(indexed_paths) - set(source))

    def counts(paths, mapping):
        return {kind: sum(mapping[path] == kind for path in paths) for kind in ("pdf", "md")}

    return {
        "source_files": len(source),
        "indexed_files": len(indexed_paths),
        "source_by_kind": counts(source, source),
        "indexed_by_kind": counts(indexed_paths, indexed_paths),
        "unindexed_files": len(unindexed),
        "unindexed_by_kind": counts(unindexed, source),
        "missing_source_files": len(missing),
        "unindexed_examples": unindexed[:5],
        "missing_source_examples": missing[:5],
    }


# ---------- 变体正则(grep) ----------

# PDF 提取时下标经常丢失,同一符号在库里有两种形态("VDD_APC" 与 "VDD APC",
# 实测空格形态占 71%);不宽容匹配会漏掉另一部分实例。
SEP_CLASS = r"[_\s]+"


def flex_pattern(pattern: str) -> str:
    """把模式里的下划线/连续空白统一放宽成 [_\\s]+。"""
    out: list[str] = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\" and i + 1 < len(pattern):
            out.append(pattern[i:i + 2])
            i += 2
            continue
        if ch == "[":
            end = i + 1
            while end < len(pattern):
                if pattern[end] == "\\":
                    end += 2
                elif pattern[end] == "]":
                    end += 1
                    break
                else:
                    end += 1
            out.append(pattern[i:end])
            i = end
            continue
        if ch == "{":
            end = pattern.find("}", i + 1)
            if end >= 0:
                out.append(pattern[i:end + 1])
                i = end + 1
                continue
        if ch != "_" and not ch.isspace():
            out.append(ch)
            i += 1
            continue
        while i < len(pattern) and (pattern[i] == "_" or pattern[i].isspace()):
            i += 1
        out.append(SEP_CLASS)
    return "".join(out)


def compile_search_regex(pattern: str, flex: bool):
    """返回 (校验用正则, 检索用正则)。宽容版本编译失败时退回原模式。"""
    try:
        rx = re.compile(pattern)
    except re.error as e:
        raise LibraryError(f"正则无效: {e}") from e
    if not flex:
        return rx, rx
    flexed = flex_pattern(pattern)
    if SEP_CLASS not in flexed:
        return rx, rx
    try:
        return rx, re.compile(flexed)
    except re.error:
        return rx, rx


# ---------- 共享扫描 ----------

def scan_arrow(table, columns: list[str]):
    """投影下推读取指定列,返回 arrow 表。

    避免 `to_arrow()` 先把整表(含 768 维 vector 列)物化再 select ——
    实测本机 8.5k 行:to_arrow().select() 54ms / 峰值 RSS +273MB;下推 16ms,
    只读所需列(省掉 26MB 向量)。空查询默认返回全表,但显式传
    limit=count_rows() 兜底,不依赖该默认行为(跨版本可能被改成默认截断)。
    """
    return table.search().select(list(columns)).limit(table.count_rows()).to_arrow()


def scan_columns(table, columns: list[str]) -> list[dict]:
    """scan_arrow 的 list[dict] 形式。MCP 与 HTTP 两侧共用。"""
    return scan_arrow(table, columns).to_pylist()


# ---------- 元数据派生结果缓存 ----------
# /api/files 与 /api/extract/report 各扫一遍全表(后者还要物化 text 列),
# 而这两份数据只在 ingest 时变化 —— 用 table.version 做失效信号。
# 放在 library 是为了让 HTTP(main.py)与同进程的 MCP(server.py)共享一份。
_META_CACHE: dict[str, tuple[int, object]] = {}


def cached(key: str, table, produce):
    """按 (key, table.version) 缓存 produce() 的结果。

    版本一变(ingest 增删)整项重建。并发请求可能各算一次,不影响正确性,
    代价远低于每次都扫全表。MCP_INPROC=1 时两侧进程内共享同一份。
    """
    ver = table.version
    hit = _META_CACHE.get(key)
    if hit is not None and hit[0] == ver:
        return hit[1]
    val = produce()
    _META_CACHE[key] = (ver, val)
    return val


def files_index(table) -> list[dict]:
    """全部文件的聚合元数据(file/category/model_no/product/kind/pages/chunks)。

    含 version(MCP 侧历史契约里有它,HTTP 侧不用但多带一个字段无妨)。
    """
    def build():
        records = scan_columns(
            table, ["file", "category", "model_no", "c_id", "version", "md5", "page"])
        seen: dict[str, dict] = {}
        for r in records:
            k = r["file"]
            # if-not-in 而非 setdefault:后者每行都无条件构造默认 dict,
            # 等于对每块(而非每文件)跑一次 product_label 正则(实测 20ms → 1ms)
            if k not in seen:
                seen[k] = {
                    "file": k, "category": r["category"], "model_no": r["model_no"],
                    "c_id": r["c_id"], "version": r["version"], "pages": 0, "chunks": 0,
                    "product": doc_utils.product_label(k),
                    "kind": "md" if doc_utils.is_markdown(k) else "pdf",
                }
            f = seen[k]
            f["chunks"] += 1
            f["pages"] = max(f["pages"], int(r["page"]) + 1)
        return sorted(seen.values(), key=lambda x: x["file"])
    return cached("files", table, build)


def categories(table) -> list[str]:
    """全部类别目录(去重排序)。"""
    return cached("categories", table, lambda: sorted(
        {r["category"] for r in scan_columns(table, ["category"]) if r["category"]}))


def _arrow_bytes(table) -> int:
    """主表与全部分区表的真实数据字节数(含向量列),作为碎片比的分母。

    用 `to_arrow().nbytes` 而不是按块数估算:向量列每块 768×4 字节,是文本的
    数倍,漏掉它会把正常索引误判成高度碎片化。
    """
    total = 0
    try:
        total += table.to_arrow().nbytes
    except Exception:
        return 0
    try:
        import lancedb

        db = lancedb.connect(str(config.DB_PATH))
        for name in db.list_tables().tables:
            if name.startswith("vec_") and name != "vec_meta":
                total += db.open_table(name).to_arrow().nbytes
    except Exception:
        return total or 0
    return total


def ingest_history_file() -> Path:
    """持久化的索引历史路径。

    历史是运行数据,必须放在 data/ 挂载里。早期写到代码根目录(容器内 /app),
    每次重建容器都会被清空,资料库的“索引历史”因此一直为空。
    """
    return Path(config.SETTINGS_FILE).parent / "ingest_history.json"


def read_ingest_history() -> list[dict]:
    """读取索引历史;新路径不存在时兼容旧的容器内/仓库根目录文件。"""
    candidates = [ingest_history_file(),
                  Path(config.DB_PATH).parent / "ingest_history.json",
                  Path(__file__).resolve().parent.parent / "ingest_history.json"]
    seen = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        except (OSError, ValueError, TypeError):
            continue
    return []


def write_ingest_history(records: list[dict]) -> None:
    """原子写入最近 100 条记录,避免中断留下半个 JSON 文件。"""
    path = ingest_history_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(records[-100:], ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def append_ingest_history(record: dict) -> None:
    """追加一条真实入库记录,读取旧路径后写到新的持久路径。"""
    write_ingest_history([*read_ingest_history(), record])


def index_health(table) -> dict:
    """索引健康度:回答"索引是否可用、有哪些已知问题"。

    只读本地文件与表元数据,不扫描正文、不访问上游。规模变大后,单看
    "有多少文件"已经不够——还需要知道索引索引是否过期、磁盘是否被历史版本
    撑大、上次索引进程是否留下了未处理的文件。

    各字段的口径都写在返回值里,避免把代理量当成精确值:
    * `fragmentation_ratio` 是目录体积 / 估算数据体积,>3 说明历史版本在堆积;
    * `pending_ingest` 只表示"上次记录里有未完成项",不代表当前正在运行。
    """
    from pathlib import Path

    db_path = Path(config.DB_PATH)
    health: dict = {"status": "unknown", "warnings": []}

    if table is None:
        health["status"] = "missing"
        health["warnings"].append({"code": "INDEX_MISSING", "message": "索引表不存在"})
        return health

    rows = table.count_rows()
    health.update(rows=rows, table_version=int(table.version))

    # 1) FTS 与向量索引是否就位:缺了会让检索静默降级或退化成暴力扫描。
    try:
        indices = list(table.list_indices())
        health["fts_index"] = [i.name for i in indices if str(i.index_type).upper().find("FTS") >= 0
                               or str(i.index_type).upper().find("INVERT") >= 0]
        if not health["fts_index"]:
            health["warnings"].append(
                {"code": "FTS_INDEX_MISSING", "message": "主表没有全文索引,关键词检索会失败或退化"})
    except Exception:
        health["fts_index"] = None

    try:
        import lancedb

        db = lancedb.connect(str(db_path))
        names = [n for n in db.list_tables().tables if n.startswith("vec_") and n != "vec_meta"]
        parts = []
        for name in names:
            part = db.open_table(name)
            parts.append({"table": name, "rows": part.count_rows(),
                          "indices": [i.name for i in part.list_indices()]})
        health["vector_partitions"] = parts
        if not parts:
            health["warnings"].append(
                {"code": "VECTOR_MISSING", "message": "没有向量分区,语义检索不可用"})
        for part in parts:
            if part["rows"] and not part["indices"]:
                health["warnings"].append(
                    {"code": "VECTOR_INDEX_MISSING",
                     "message": f"{part['table']} 未建向量索引,检索会退化为暴力扫描"})
            if part["rows"] != rows:
                health["warnings"].append(
                    {"code": "VECTOR_ROW_MISMATCH",
                     "message": f"{part['table']} 有 {part['rows']} 行,主表 {rows} 行"})
    except Exception as error:
        health["vector_partitions"] = None
        health["warnings"].append({"code": "VECTOR_UNAVAILABLE",
                                   "message": f"向量分区不可读: {type(error).__name__}"})

    # 2) 磁盘体积与碎片:长期增量会让历史版本堆积(实测曾达 9 倍开销)。
    try:
        files = [p for p in db_path.rglob("*") if p.is_file()]
        total = sum(p.stat().st_size for p in files)
        health["disk_bytes"] = total
        health["disk_files"] = len(files)
        # 基准必须是**真实数据量**:主表文本 + 向量列,不是按块数瞎估。
        # 早先按 400 字节/块估算,把 768 维向量漏掉,导致 2.2 倍的正常索引
        # 被误报成 28 倍碎片。拿不到数据量时不报这个指标,而不是给个错数。
        data_bytes = _arrow_bytes(table)
        if data_bytes:
            health["data_bytes"] = data_bytes
            ratio = total / data_bytes
            health["fragmentation_ratio"] = round(ratio, 2)
            # 小索引的固定开销(manifest、schema、footer)会让比值天然偏高,
            # 例如 20 行的测试表也有 5 倍。低于 1MB 数据量时不判碎片,避免误报。
            if data_bytes >= 1_000_000 and ratio > 4:
                health["warnings"].append(
                    {"code": "INDEX_FRAGMENTED",
                     "message": f"索引目录约 {total/1048576:.0f}MB,为数据量的 {ratio:.1f} 倍;"
                                "可运行 tools/compact_index.py 合并历史版本"})
    except Exception:
        health["disk_bytes"] = None

    # 3) 上次索引的结果:未索引/失效引用/跳过的文件/错误。
    try:
        records = read_ingest_history()
        if not records:
            health["last_ingest"] = None
            last = {}
            skipped = []
        else:
            last = records[-1]
            skipped = last.get("skipped") or []
            health["last_ingest"] = {
                "time": last.get("time"), "added": last.get("added"),
                "removed": last.get("removed"), "chunks": last.get("chunks"),
                "elapsed": last.get("elapsed"), "skipped": len(skipped),
                "skipped_examples": skipped[:5],
            }
        if skipped:
            health["warnings"].append(
                {"code": "FILES_SKIPPED",
                 "message": f"上次索引有 {len(skipped)} 个文件未产生文本,未进入索引"})
    except Exception:
        health["last_ingest"] = None

    # 4) 实体桥快照:存在即说明 structured 查询可以秒级启动。
    try:
        snapshot = Path(config.SETTINGS_FILE).parent / "entity_index.pkl"
        if snapshot.exists():
            stat = snapshot.stat()
            health["entity_snapshot"] = {"bytes": stat.st_size,
                                         "mtime": int(stat.st_mtime)}
    except Exception:
        pass

    health["status"] = "degraded" if health["warnings"] else "ok"
    return health

def extract_report(table, threshold: float) -> list[dict]:
    """逐文档提取质量(每页字符数、suspect 标记),按每页字符数升序。

    缓存键含 threshold:改了"每页字数告警线"后 suspect 必须跟着变。
    """
    def build():
        rows = scan_columns(table, ["file", "category", "model_no", "page", "text"])
        agg: dict[str, dict] = {}
        for r in rows:
            k = r["file"]
            if k in agg:
                item = agg[k]
            else:
                item = agg[k] = {
                    "file": k, "category": r["category"], "model_no": r["model_no"],
                    "chunks": 0, "chars": 0, "pages": 0,
                }
            item["chunks"] += 1
            item["chars"] += len(r["text"])
            item["pages"] = max(item["pages"], int(r["page"]) + 1)
        out = []
        for item in agg.values():
            per_page = item["chars"] / max(1, item["pages"])
            item["chars_per_page"] = round(per_page, 1)
            item["suspect"] = per_page < threshold
            out.append(item)
        out.sort(key=lambda x: x["chars_per_page"])
        return out
    return cached(f"report:{threshold}", table, build)


# ---------- 读页 ----------

def parse_page_spec(spec: str, max_pages: int = 1000) -> list[int]:
    """解析有界页码列表,在展开范围前校验容量。"""
    spec = (spec or "").strip()
    nums: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            if "-" in part:
                a, _, b = part.partition("-")
                start, stop = int(a), int(b)
                count = stop - start + 1
                if count < 1:
                    raise ValueError
            else:
                start = stop = int(part)
                count = 1
        except ValueError:
            raise LibraryError(f"页码格式无效: {part}") from None
        if len(nums) + count > max_pages:
            raise LibraryError(f"单次最多请求 {max_pages} 页", code="TOO_MANY_PAGES")
        nums.extend(range(start, stop + 1))
    if not nums:
        raise LibraryError('未解析出页码,示例:pages="62,63" 或 "62-65"')
    return nums
