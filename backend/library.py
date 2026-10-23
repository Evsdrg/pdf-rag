"""文档库的共享读取/检索逻辑(与传输层无关)。

MCP(server.py)与 HTTP API(backend/main.py)共用本模块。此前 grep / read_pages /
get_outline 只在 MCP 侧实现,HTTP 侧缺失,非 MCP 客户端(如 pi)因此拿不到等价能力;
read_page 又两侧各写一份、错误文案靠人工对齐。收拢到这里后,两侧只做
「参数 → 调用 → 序列化」,不再产生行为漂移。

本模块还持有 **LanceDB 连接与表句柄的单例**(`get_table`)—— 两侧此前各写了一份
几乎逐字的实现,且 MCP 侧每次调用都重新 connect。句柄管理天然属于"数据访问层"。

约定:本模块返回 Python 原生结构(dict / tuple),**不返回 JSON 字符串** ——
序列化交给调用方(MCP 工具 json.dumps,HTTP 端点直接返回 dict)。
可预期错误一律抛 LibraryError 子类,由调用方决定呈现方式:
MCP 序列化成 {"error": ...},HTTP 映射成 4xx 状态码。
"""
import os
import re

import fitz

from . import config, doc_utils


class LibraryError(Exception):
    """可预期的调用错误(参数非法 / 页码越界)。HTTP 侧映射成 4xx。"""

    status = 400


class NotFound(LibraryError):
    """目标文件不存在 —— HTTP 侧映射成 404。"""

    status = 404


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


def grep_rows(table, pattern: str, category: str = "", file: str = "",
              max_hits: int = 20, context: int = 60,
              flex_separator: bool = True) -> dict:
    """按字面/正则精确检索文本,返回命中行及上下文(不走向量)。

    这条路天然不受嵌入服务可用性影响,定位具体字面值(如 VDD_APC、IddHP)最可靠。
    pattern 为正则;flex_separator=True 时把下划线/空白视为等价(见 flex_pattern)。
    """
    import pyarrow.compute as pc

    _, rx = compile_search_regex(pattern, flex_separator)
    # 投影下推取列(排除 26MB vector 列),但保留 arrow 级正则过滤 —— 比逐行 Python 快得多
    df = scan_arrow(table, ["file", "page", "text", "category", "model_no"])
    try:
        rows = df.filter(pc.match_substring_regex(df["text"], rx.pattern)).to_pylist()
    except Exception as e:
        raise LibraryError(f"检索失败: {e}") from e

    out = []
    for r in rows:
        if category and r["category"] != category:
            continue
        if file and file not in r["file"]:
            continue
        m = rx.search(r["text"])
        if not m:
            continue
        text = r["text"]
        s, e = max(0, m.start() - context), min(len(text), m.end() + context)
        out.append({
            "file": r["file"], "page": int(r["page"]) + 1,
            "model_no": r["model_no"], "match": m.group(0),
            "matches_in_page": len(rx.findall(text)),
            "context": re.sub(r"\s+", " ", text[s:e]).strip(),
        })
        if len(out) >= max_hits:
            break
    return {"pattern": pattern, "flex_separator": flex_separator,
            "hits": len(out), "results": out}


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

def read_page_raw(pdf_root: str, file: str, page: int) -> tuple[str, str]:
    """读单页完整文本(含表格 markdown,低文本页回退 OCR)。返回 (文本, 错误)。

    文件不存在抛 NotFound;页码越界抛 LibraryError。PDF 与 Markdown 行为一致
    (Markdown 按一级标题切"伪页")。
    """
    try:
        full = doc_utils.resolve_under(pdf_root, file)
    except FileNotFoundError:
        raise NotFound(f"文件不存在或路径越界: {file}")
    if not os.path.isfile(full):
        raise NotFound(f"文件不存在: {file}")
    if doc_utils.is_markdown(full):
        text, err = doc_utils.read_md_page(full, page)
        if err:
            raise LibraryError(err)
        return text, ""
    doc = fitz.open(full)
    try:
        if page < 1 or page > len(doc):
            raise LibraryError(f"页码越界: {page} (共 {len(doc)} 页)")
        return doc_utils.read_page_text(doc, page)
    finally:
        doc.close()


def parse_page_spec(spec: str) -> list[int]:
    """解析页码列表,如 "62,63,64" 或 "62-65"。"""
    spec = (spec or "").strip()
    nums: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            try:
                nums.extend(range(int(a), int(b) + 1))
            except ValueError:
                raise LibraryError(f"页码格式无效: {part}") from None
        else:
            try:
                nums.append(int(part))
            except ValueError:
                raise LibraryError(f"页码格式无效: {part}") from None
    if not nums:
        raise LibraryError('未解析出页码,示例:pages="62,63" 或 "62-65"')
    return nums


def read_pages(pdf_root: str, file: str, spec: str) -> dict:
    """一次读取多页。返回 {file, total_pages, pages:[{page,text|error}]}。

    规格表常跨页(绝对最大值表、PDN 表),逐页读要多跑数次。单页越界不中断,
    在对应项里回报错误,其余页照常返回。
    """
    nums = parse_page_spec(spec)
    try:
        full = doc_utils.resolve_under(pdf_root, file)
    except FileNotFoundError:
        raise NotFound(f"文件不存在或路径越界: {file}")
    if not os.path.isfile(full):
        raise NotFound(f"文件不存在: {file}")
    if doc_utils.is_markdown(full):
        pages = doc_utils.md_pages(full)
        out = []
        for p in nums:
            if p < 1 or p > len(pages):
                out.append({"page": p, "error": f"越界(共 {len(pages)} 页)"})
            else:
                out.append({"page": p, "text": pages[p - 1]})
        return {"file": file, "total_pages": len(pages), "pages": out}
    doc = fitz.open(full)
    try:
        from .ocr_policy import DocumentPolicy
        policy = None
        out = []
        for p in nums:
            if p < 1 or p > len(doc):
                out.append({"page": p, "error": f"越界(共 {len(doc)} 页)"})
                continue
            if policy is None and config.get("ocr_smart_filter"):
                try:
                    thin = len(doc[p - 1].get_text("text").strip()) < config.get("ocr_min_chars")
                except Exception:
                    thin = True
                if thin:
                    policy = DocumentPolicy(doc)
            text, _err = doc_utils.read_page_text(doc, p, policy)
            out.append({"page": p, "text": text})
        return {"file": file, "total_pages": len(doc), "pages": out}
    finally:
        doc.close()


def doc_outline(pdf_root: str, file: str) -> dict:
    """取文档书签/标题目录(章节 + 页码),用于在大手册里导航后再精确读页。"""
    try:
        full = doc_utils.resolve_under(pdf_root, file)
    except FileNotFoundError:
        raise NotFound(f"文件不存在或路径越界: {file}")
    if not os.path.isfile(full):
        raise NotFound(f"文件不存在: {file}")
    if doc_utils.is_markdown(full):
        outline = doc_utils.md_outline(full)
        return {"file": file, "total_pages": len(doc_utils.md_pages(full)),
                "outline": outline,
                "note": "" if outline else "该文档无标题结构,可用 grep 定位关键节标题"}
    doc = fitz.open(full)
    try:
        toc = doc.get_toc() or []
        return {"file": file, "total_pages": len(doc),
                "outline": [{"level": lv, "title": ti, "page": pg} for lv, ti, pg in toc],
                "note": "" if toc else "该 PDF 无书签目录,可用 grep 定位关键节标题"}
    finally:
        doc.close()
