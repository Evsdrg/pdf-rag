"""MCP 传输适配:单份 JSON 文本,领域逻辑与 REST v2 共用。"""
import json
import os
import sys
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.tools.base import ToolResult

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend import agent_api

mcp = FastMCP("pdf-rag")


def _call(function, **kwargs) -> ToolResult:
    payload, status = agent_api.invoke(function, **kwargs)
    return ToolResult(content=json.dumps(payload, ensure_ascii=False), is_error=status >= 400)


@mcp.tool(name="pdf_rag_search", output_schema=None)
def pdf_rag_search(query: str, category: str = "", top_k: int = 5,
                   file: str = "", max_per_doc: int = 0) -> ToolResult:
    """在手册库做 BM25 + 型号子串 + 向量混合检索,不是工作区文件搜索。

    query 支持中文/英文;category 按类别,file 按文件路径字面子串筛选。
    返回 schema_version=2 的 JSON:results 含 file/page/snippet/score/rerank_score。
    degraded/notice 标明降级;重排分是相关性信号,不是答案正确率。
    file/page 可直接传给读页工具;max_per_doc 限制同一文件条数(0 使用服务配置)。
    """
    return _call(agent_api.search, query=query, category=category, top_k=top_k,
                 file=file, max_per_doc=max_per_doc)


@mcp.tool(name="pdf_rag_grep", output_schema=None)
def pdf_rag_grep(pattern: str, category: str = "", file: str = "",
                 max_hits: int = 20, context: int = 60,
                 flex_separator: bool = True) -> ToolResult:
    """在已索引的手册文本中精确查符号/正则,不经过向量或上游模型。

    flex_separator 默认把下划线和空白视为等价;正则特殊字符需要转义。
    返回 JSON results 与上下文,文件和页码可直接用于回读。
    """
    return _call(agent_api.grep, pattern=pattern, category=category, file=file,
                 max_hits=max_hits, context=context, flex_separator=flex_separator)


@mcp.tool(name="pdf_rag_read_page", output_schema=None)
def pdf_rag_read_page(file: str, page: int, max_chars: int = 8000,
                      cursor: str = "") -> ToolResult:
    """读取库内文档页,返回 JSON file/page/text/ocr/warnings,错误含稳定 code。

    PDF 为从 1 开始的物理页;Markdown 按一级标题分页(page_basis=h1_section)。
    低文本页按内容策略调用 OCR;OCR 失败保留原生文本并给出警告。
    max_chars 为文本预算(256–12000),truncated=true 时原样传 next_cursor 继续读取。
    """
    return _call(agent_api.read_page, file=file, page=page, max_chars=max_chars, cursor=cursor)


@mcp.tool(name="pdf_rag_read_pages", output_schema=None)
def pdf_rag_read_pages(file: str, pages: str, max_chars: int = 8000,
                       cursor: str = "") -> ToolResult:
    """一次读多页,如 pages="62,63" 或 "62-65";返回 JSON pages 数组。

    最多请求50页,max_chars是整次文本预算;truncated时传next_cursor续读。
    单页越界在对应项给出 error,其余页继续。PDF 页号不等于页内印刷页码。
    """
    return _call(agent_api.read_pages, file=file, pages=pages, max_chars=max_chars, cursor=cursor)


@mcp.tool(name="pdf_rag_read_section", output_schema=None)
def pdf_rag_read_section(file: str, section_id: str, max_chars: int = 8000,
                         cursor: str = "") -> ToolResult:
    """按 get_outline 返回的 section_id 读取章节,避免整章/整篇超长输出。

    Markdown 精确到标题范围;PDF 按书签物理页范围,共享页可能包含相邻节。
    truncated=true 时传 next_cursor 继续;文档变化/服务重启后需重新获取目录。
    """
    return _call(agent_api.read_section, file=file, section_id=section_id,
                 max_chars=max_chars, cursor=cursor)


@mcp.tool(name="pdf_rag_get_outline", output_schema=None)
def pdf_rag_get_outline(file: str, max_level: int = 2, limit: int = 60,
                        cursor: str = "") -> ToolResult:
    """分页取 PDF 书签/Markdown 标题目录,返回 JSON outline 和 section_id。

    默认前两级,可用max_level=6展开;limit最多100。truncated时传next_cursor。
    section_id可传read_section;没有目录时用grep,不猜测章节。
    """
    return _call(agent_api.get_outline, file=file, max_level=max_level, limit=limit, cursor=cursor)


@mcp.tool(name="pdf_rag_list_categories", output_schema=None)
def pdf_rag_list_categories() -> ToolResult:
    """列出已索引手册类别,返回 JSON categories 与 count,不访问上游模型。"""
    return _call(agent_api.list_categories)


@mcp.tool(name="pdf_rag_list_files", output_schema=None)
def pdf_rag_list_files(category: str = "", file: str = "", model_no: str = "",
                       kind: str = "", limit: int = 30, cursor: str = "") -> ToolResult:
    """分页列出已索引文件,返回files/count/total/next_cursor。

    可筛选category、文件路径子串file、型号子串model_no、kind(pdf/md)。
    默认30份,最多100份;truncated时保持筛选条件并传next_cursor继续。
    pages_basis=indexed_max_page表示索引内最大页号,不是物理总页数。
    """
    return _call(agent_api.list_files, category=category, file=file, model_no=model_no,
                 kind=kind, limit=limit, cursor=cursor)


@mcp.tool(name="pdf_rag_status", output_schema=None)
def pdf_rag_status() -> ToolResult:
    """只读索引规模与 OCR 最近一次真实调用记录,不主动探测任何上游服务。"""
    return _call(agent_api.status)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    kwargs = {}
    if transport != "stdio":
        kwargs = dict(host=os.getenv("MCP_HOST", "0.0.0.0"),
                      port=int(os.getenv("MCP_PORT", "8101")),
                      path=os.getenv("MCP_PATH", "/mcp"))
    mcp.run(transport=transport, **kwargs)
