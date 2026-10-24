"""Agent 协议的 HTTP 适配;旧 /api/* 响应形状保持不变。"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from . import agent_api

router = APIRouter(prefix="/api/v2")


def _call(function, **kwargs):
    payload, status = agent_api.invoke(function, **kwargs)
    return JSONResponse(payload, status_code=status)


@router.get("/search")
def search(query: str, category: str = "", top_k: int = 5, file: str = "",
           max_per_doc: int = 0, mode: str = "mixed", rerank: bool = True):
    return _call(agent_api.search, query=query, category=category, top_k=top_k,
                 file=file, max_per_doc=max_per_doc, mode=mode, rerank=rerank)


@router.get("/grep")
def grep(pattern: str, category: str = "", file: str = "", max_hits: int = 20,
         context: int = 60, flex_separator: bool = True, cursor: str = ""):
    return _call(agent_api.grep, pattern=pattern, category=category, file=file,
                 max_hits=max_hits, context=context, flex_separator=flex_separator, cursor=cursor)


@router.get("/page")
def read_page(file: str, page: int, max_chars: int = 8000, cursor: str = ""):
    return _call(agent_api.read_page, file=file, page=page, max_chars=max_chars, cursor=cursor)


@router.get("/pages")
def read_pages(file: str, pages: str, max_chars: int = 8000, cursor: str = ""):
    return _call(agent_api.read_pages, file=file, pages=pages, max_chars=max_chars, cursor=cursor)


@router.get("/section")
def read_section(file: str, section_id: str, max_chars: int = 8000, cursor: str = ""):
    return _call(agent_api.read_section, file=file, section_id=section_id,
                 max_chars=max_chars, cursor=cursor)


@router.get("/outline")
def outline(file: str, max_level: int = 2, limit: int = 60, cursor: str = ""):
    return _call(agent_api.get_outline, file=file, max_level=max_level, limit=limit, cursor=cursor)


@router.get("/files")
def files(category: str = "", file: str = "", model_no: str = "", kind: str = "",
          limit: int = 30, cursor: str = ""):
    return _call(agent_api.list_files, category=category, file=file, model_no=model_no,
                 kind=kind, limit=limit, cursor=cursor)


@router.get("/categories")
def categories():
    return _call(agent_api.list_categories)


@router.get("/status")
def status():
    return _call(agent_api.status)
