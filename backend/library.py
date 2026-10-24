"""共享索引句柄、元数据聚合、参数解析与领域错误;读取入口在 agent_documents。"""
import os
import re

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
