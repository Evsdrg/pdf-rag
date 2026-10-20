"""PDF-RAG 的 MCP 服务(FastMCP)。

工具命名统一用 `pdf_rag_` 前缀,与 agent 框架自带命令(read/grep/ls/find)明确区分 ——
框架内置的 `grep` 搜的是**工作区文件系统**,本库的 `pdf_rag_grep` 搜的是**已索引的
元器件手册语料**,两者同名会让模型选错工具。

约定:
* 所有工具都声明 output_schema=None 并返回 JSON 字符串。若返回结构化类型,
  FastMCP 会同时发出 content 与 structuredContent 两份等价载荷,白白翻倍 token。
* 检索类工具一律把 degraded 透出到结果里。历史上三处 except Exception: pass
  把"嵌入/重排不可用"完全藏住了 —— 调用方看不出结果已被降级。
* 读取/检索的实体逻辑在 backend/library.py(与 HTTP API 共用),本文件只做
  「参数 → 调用 → 序列化」。
"""
import json
import os
import sys
from pathlib import Path

from fastmcp import FastMCP

# 确保 backend 包可导入:无论以何种 cwd 启动(如 MCP 全局配置),都以本文件所在目录为项目根
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend import config, library, retrieval

mcp = FastMCP("pdf-rag")


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _get_table():
    """表句柄(实现见 library.get_table,与 HTTP 侧共用同一单例)。

    此前本文件有一份几乎逐字的副本,且**每次工具调用都重新 lancedb.connect()**;
    收进 library 后连接也只建一次。
    """
    table = library.get_table()
    if table is None:
        raise RuntimeError("索引不存在,请先运行 ingest.py")
    return table


# ---------- 检索 ----------

@mcp.tool(name="pdf_rag_search", output_schema=None)
def pdf_rag_search(query: str, category: str = "", top_k: int = 5,
                  file: str = "", max_per_doc: int = 0) -> str:
    """在元器件手册库(已索引的手册语料)中做混合检索——与工作区的 grep/find 无关。

    这是首选入口:BM25 + 型号子串 + 向量三路召回,RRF 融合后重排,返回已定位到
    答案的片段窗口。

    query: 查询内容,如 "W25Q32 供电电压"(中文/英文均可)
    category: 可选,按类别过滤,如 "02_存储"
    top_k: 返回条数
    file: 可选,只在文件名含该子串的文档内检索,如 "QMC6309"
    max_per_doc: 同一文件最多返回几条(0=不限)

    返回 JSON:results[] 每项含 file/page/snippet/score/rerank_score;
    若 degraded 非空,说明走了降级路径,结果可能不完整。
    """
    table = _get_table()
    diag: dict = {}
    hits = retrieval.search(table, query, category=category or None, top_k=top_k,
                            file=file or None,
                            max_per_doc=max_per_doc, diagnostics=diag)
    return _json({
        "query": query, "count": len(hits),
        "degraded": diag.get("degraded", []),
        "notice": diag.get("notice", ""),
        "counts": diag.get("counts", {}),
        "cached": diag.get("cached", False),
        "results": hits,
    })


@mcp.tool(name="pdf_rag_grep", output_schema=None)
def pdf_rag_grep(pattern: str, category: str = "", file: str = "",
                max_hits: int = 20, context: int = 60,
                flex_separator: bool = True) -> str:
    """在**手册库文本**里按字面/正则精确检索(不等于工作区的 grep,后者搜文件系统)。

    适合查精确符号:如 "VDD_APC"、"IddHP"、"SMPA1"、"2\\.4MHz"。
    这条路不经过向量检索,天然不受嵌入服务可用性影响,定位具体字面值最可靠。

    flex_separator=True(默认):把模式里的下划线/空白视为等价(PDF 下标丢失,
    同一符号常见 "VDD_APC"/"VDD APC" 两种形态)。
    pattern 为正则;纯字面查找直接写字符串即可(特殊字符需转义)。
    """
    table = _get_table()
    return _json(library.grep_rows(table, pattern, category=category, file=file,
                                   max_hits=max_hits, context=context,
                                   flex_separator=flex_separator))


# ---------- 读取 ----------

@mcp.tool(name="pdf_rag_read_page", output_schema=None)
def pdf_rag_read_page(file: str, page: int) -> str:
    """读取手册某页的完整原文(与工作区的 read 不同,这里读的是库内手册,非工作区文件)。

    file: pdf_rag_search 返回的 file 字段(库内相对路径);page: 页码,从 1 开始。
    支持 PDF 与 Markdown(.md 按一级标题分页);扫描页自动回退 OCR。
    """
    try:
        text, _err = library.read_page_raw(config.PDF_ROOT, file, page)
        return text
    except library.LibraryError as e:
        return str(e)


@mcp.tool(name="pdf_rag_read_pages", output_schema=None)
def pdf_rag_read_pages(file: str, pages: str) -> str:
    """一次读取手册多页(file: 库内相对路径; pages: 如 "62,63,64" 或 "62-65")。

    规格表常跨页(绝对最大值表、PDN 表跨两页),逐页读要多跑数次。
    """
    try:
        return _json(library.read_pages(config.PDF_ROOT, file, pages))
    except library.LibraryError as e:
        return _json({"error": str(e)})


@mcp.tool(name="pdf_rag_get_outline", output_schema=None)
def pdf_rag_get_outline(file: str) -> str:
    """取手册的书签/标题目录(章节 + 页码),用于在大手册里导航后再精确读页。

    支持 PDF 与 Markdown。无目录时 note 会提示改用 pdf_rag_grep 定位关键节标题。
    """
    try:
        return _json(library.doc_outline(config.PDF_ROOT, file))
    except library.LibraryError as e:
        return _json({"error": str(e)})


# ---------- 索引信息 ----------

@mcp.tool(name="pdf_rag_list_categories", output_schema=None)
def pdf_rag_list_categories() -> str:
    """列出手册库中的所有类别目录。"""
    return _json(library.categories(_get_table()))


@mcp.tool(name="pdf_rag_list_files", output_schema=None)
def pdf_rag_list_files(category: str = "") -> str:
    """列出手册库中已索引的文件及其元数据(category: 可选,按类别过滤)。

    返回 file/category/model_no/product/pages/chunks —— 只给路径无法判断
    某份文档是否已入库、有多少页,会导致不必要地去本地翻手册。
    """
    files = library.files_index(_get_table())
    if category:
        files = [f for f in files if f["category"] == category]
    return _json(files)


@mcp.tool(name="pdf_rag_status", output_schema=None)
def pdf_rag_status() -> str:
    """手册库索引与依赖的健康状态。

    只读本地状态:索引规模、最后入库时间、OCR 配置与其**最近一次真实调用**的结果。
    **不主动探测任何上游服务**(嵌入/重排/OCR)——那会给服务商带来无意义负载,
    且可用性不会在几秒内变化。需要验证上游是否可用,跑一次真实查询/读页即可。
    结果是"结果质量突然变差"时的排查第一站:看 ocr.last_call.ok 与检索降级信息。
    """
    from datetime import datetime
    out: dict = {"pdf_root": config.PDF_ROOT, "db_path": config.DB_PATH}
    try:
        table = _get_table()
        rows = library.scan_columns(table, ["file", "category"])
        files = {r["file"] for r in rows}
        out.update({
            "indexed": True,
            "chunks": len(rows),
            "files": len(files),
            "categories": len({r["category"] for r in rows if r["category"]}),
        })
    except Exception as e:
        out.update({"indexed": False, "error": str(e)})
        return _json(out)

    hist_file = Path(config.DB_PATH).parent / "ingest_history.json"
    try:
        hist = json.loads(hist_file.read_text(encoding="utf-8"))
        out["last_ingest"] = hist[-1].get("time") if hist else None
    except Exception:
        out["last_ingest"] = None

    from backend import ocr as ocr_mod
    out["ocr"] = ocr_mod.status()   # 配置 + 最近一次真实调用;零网络请求
    out["checked_at"] = datetime.now().isoformat(timespec="seconds")
    return _json(out)


if __name__ == "__main__":
    # 传输方式可配:默认 stdio(本地 MCP 客户直接拉起);容器/远程场景用
    # MCP_TRANSPORT=http + MCP_HOST/MCP_PORT 走 streamable HTTP(.env 即可配置,
    # import backend.config 时 load_dotenv 已把它们载入环境)。
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    kwargs: dict = {}
    if transport != "stdio":
        kwargs = dict(
            host=os.getenv("MCP_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_PORT", "8101")),
            path=os.getenv("MCP_PATH", "/mcp"),
        )
    mcp.run(transport=transport, **kwargs)
