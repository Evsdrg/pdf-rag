import json
import hmac
import os
import subprocess
import sys
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated

import fitz
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import bundle, config, doc_utils, library, retrieval, vecstore

ROOT = Path(__file__).resolve().parent

STATE_FILE = ROOT.parent / "run_state.json"
HISTORY_FILE = ROOT.parent / "ingest_history.json"
LOCK_FILE = ROOT.parent / "ingest.lock"

# MCP 可选内嵌:与 HTTP API 同进程同端口(见 config.MCP_INPROC),省一个 Python
# 进程的内存(lancedb/pyarrow/fitz 各加载一份是大头)。设 MCP_INPROC=0 则退回
# 双进程形态(独立 server.py 监听 8101)。
_mcp_subapp = None
if config.MCP_INPROC:
    try:
        sys.path.insert(0, str(ROOT.parent))
        from server import mcp as _mcp          # noqa: E402
        _mcp_subapp = _mcp.http_app(path="/")
    except Exception as _e:                     # 内嵌失败不应拖垮后端
        print(f"[warn] MCP 内嵌失败,将以纯 API 模式运行: {_e}", file=sys.stderr)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    if _mcp_subapp is not None:
        async with _mcp_subapp.lifespan(app):
            yield
    else:
        yield


app = FastAPI(title="PDF-RAG API", lifespan=_lifespan)


class SelectiveGZip:
    """JSON 响应压缩(纯 ASGI,包在 GZipMiddleware 外面按路径放行)。

    实测无压缩时:JS bundle 708KB 裸传(gzip 后 222KB,-69%)、/api/files 59KB。
    跳过两类端点:
    * /mcp —— fastmcp 走 SSE 流式,text/event-stream 与缓冲压缩语义相冲;
    * /api/pdf —— FileResponse 直传 PDF,文件本身已是压缩格式,服务端 CPU 白花。
    """

    def __init__(self, app, minimum_size: int = 1024):
        self.plain = app
        self.gzip = GZipMiddleware(app, minimum_size=minimum_size)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.plain(scope, receive, send)
        path = scope.get("path", "")
        if (path == config.MCP_PATH or path.startswith(config.MCP_PATH + "/")
                or path == "/api/pdf"):
            return await self.plain(scope, receive, send)
        return await self.gzip(scope, receive, send)


app.add_middleware(SelectiveGZip)
if _mcp_subapp is not None:
    # 挂在 / 静态资源之前注册:Starlette 按注册顺序匹配,否则被 StaticFiles 吞掉
    app.mount(config.MCP_PATH, _mcp_subapp)

    @app.api_route(config.MCP_PATH, methods=["GET", "POST", "DELETE", "OPTIONS"],
                   include_in_schema=False)
    async def _mcp_redirect():
        # 无尾斜杠直连时,挂在 "/" 的 StaticFiles 会先以 405 拦下
        # (Mount 的路径正则要求尾斜杠)。显式 307 到带斜杠形式,307 保留方法与请求体。
        from starlette.responses import RedirectResponse
        return RedirectResponse(config.MCP_PATH + "/", status_code=307)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 连接/表句柄的单例实现已收进 library(与同进程的 MCP 侧共用一份,见其模块 docstring)。
# 这里保留 `_db` / `_table` 作为本模块内的习惯叫法,内部直接委托。


def _db():
    """LanceDB 连接单例(实现见 library.get_db)。"""
    return library.get_db()


def _table():
    """表句柄单例(实现见 library.get_table):按 manifest 版本自动重开。"""
    return library.get_table()


def _load_state() -> dict:
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


@app.get("/api/page")
def read_page(
    file: Annotated[str, Query(description="pdfrag_search 返回的文件路径")],
    page: Annotated[int, Query(ge=1, description="页码,从 1 开始")],
) -> dict:
    try:
        full = doc_utils.resolve_under(config.PDF_ROOT, file)
    except FileNotFoundError:
        return {"error": f"文件不存在或路径越界: {file}", "text": "", "ocr": False}
    if not os.path.isfile(full):
        return {"error": f"文件不存在: {file}", "text": "", "ocr": False}
    if doc_utils.is_markdown(full):
        text, err = doc_utils.read_md_page(full, page)
        return {"text": text, "ocr": False, "error": err}
    doc = fitz.open(full)
    try:
        if page < 1 or page > len(doc):
            return {"error": f"页码越界: {page} (共 {len(doc)} 页)", "text": "", "ocr": False}
        from .doc_utils import read_page_text
        text, err = read_page_text(doc, page)
        return {"text": text, "ocr": bool(err), "error": err}
    finally:
        doc.close()


@app.get("/api/state")
def get_state() -> dict:
    return _load_state()


@app.get("/api/grep")
def api_grep(
    pattern: Annotated[str, Query(min_length=1, description="正则/字面,如 VDD_APC")],
    category: Annotated[str | None, Query(description="按类别过滤")] = None,
    file: Annotated[str | None, Query(description="只在文件名含该子串的文档内检索")] = None,
    max_hits: Annotated[int, Query(ge=1, le=200)] = 20,
    context: Annotated[int, Query(ge=0, le=500)] = 60,
    flex_separator: Annotated[bool, Query(description="下划线/空白视为等价")] = True,
) -> dict:
    """在库文本里精确检索(正则),不走向量。非 MCP 客户端(如 pi)的等价入口。"""
    table = _table()
    if table is None:
        return {"error": "索引不存在,请先运行 ingest"}
    try:
        return library.grep_rows(table, pattern, category=category or "",
                                 file=file or "", max_hits=max_hits,
                                 context=context, flex_separator=flex_separator)
    except library.LibraryError as e:
        raise HTTPException(status_code=e.status, detail=str(e)) from e


@app.get("/api/pages")
def api_pages(
    file: Annotated[str, Query(description="库内相对路径,同 /api/page")],
    pages: Annotated[str, Query(description='页码列表,如 "62,63" 或 "62-65"')],
) -> dict:
    """一次读多页(规格表常跨页)。单页越界在对应项内回报,不中断整体。"""
    try:
        return library.read_pages(config.PDF_ROOT, file, pages)
    except library.LibraryError as e:
        raise HTTPException(status_code=e.status, detail=str(e)) from e


@app.get("/api/outline")
def api_outline(
    file: Annotated[str, Query(description="库内相对路径,同 /api/page")],
) -> dict:
    """取文档书签/标题目录(章节 + 页码),用于在大手册里导航后精确读页。"""
    try:
        return library.doc_outline(config.PDF_ROOT, file)
    except library.LibraryError as e:
        raise HTTPException(status_code=e.status, detail=str(e)) from e


@app.get("/api/stats")
def get_stats() -> dict:
    table = _table()
    if table is None:
        return {"indexed": False, "files": 0, "chunks": 0, "categories": [],
                "last_index": None, "history": [], "skipped": []}
    records = library.scan_columns(table, ["file", "category"])
    files = sorted({r["file"] for r in records})
    cat_counts: dict[str, int] = {}
    for r in records:
        cat = r["category"] or "(未分类)"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    categories = [{"name": k, "chunks": v} for k, v in sorted(cat_counts.items())]
    hist = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
                hist = json.load(f)
        except Exception:
            pass
    state = _load_state()
    return {
        "indexed": True,
        "files": len(files),
        "chunks": len(records),
        "categories": categories,
        "last_index": state.get("finished_at"),
        "history": hist,
        "skipped": state.get("skipped", []),
        "vectors": _vector_status(table),
    }


def _vector_status(table) -> dict:
    """各向量分区的覆盖率与当前选用情况。

    覆盖率**按块**(向量化的输入单位就是块);同时报文件数与"部分覆盖的文件数"
    —— 后者是"某份文档只有一部分块有向量"的信号,最容易被人忽略。
    计算含全表扫描,按 (主表版本, 分区版本) 缓存,避免每次刷 stats 都算。
    """
    db = library.get_db()
    if db is None:
        return {"partitions": [], "selected": [], "current": None}
    metas = vecstore.list_partitions(db)

    def produce():
        out = []
        for m in metas:
            cov = vecstore.coverage(db, table, m["slug"])
            out.append({
                "slug": m["slug"], "model": m.get("model"), "dim": m.get("dim"),
                "input_type_doc": m.get("input_type_doc") or "",
                "blocks_covered": cov["blocks_covered"], "blocks_total": cov["blocks_total"],
                "files_covered": cov["files_covered"], "files_total": cov["files_total"],
                "files_partial": cov["files_partial"], "ratio": round(cov["ratio"], 4),
                "updated_at": m.get("updated_at"),
            })
        return out

    # library.cached 只按主表 version 失效,而补建/重建分区时主表并不变 ——
    # 必须把分区版本也进 key,否则覆盖率会一直显示旧值。
    ver_parts = []
    for m in metas:
        p = vecstore.open_partition(db, m["slug"])
        ver_parts.append(f"{m['slug']}@{p.version if p is not None else '-'}")
    key = "vecstatus:" + ",".join(ver_parts)
    parts = library.cached(key, table, produce)
    selected = [m["slug"] for m in vecstore.select_partitions(db)]
    return {"partitions": parts, "selected": selected,
            "current": vecstore.current_slug()}


@app.get("/api/categories")
def get_categories() -> list[str]:
    table = _table()
    if table is None:
        return []
    return library.categories(table)


@app.get("/api/files")
def list_files(
    category: Annotated[str | None, Query(description="按类别过滤")] = None,
) -> list[dict]:
    table = _table()
    if table is None:
        return []
    all_files = library.files_index(table)
    # 全量结果缓存一份,category 过滤在内存里做(287 条,过滤成本可忽略);
    # 每种 category 各缓存一份会让条目数随类别数膨胀,不划算。
    if category:
        return [f for f in all_files if f["category"] == category]
    return all_files


@app.get("/api/search")
def search(
    q: Annotated[str, Query(min_length=1, max_length=200, description="查询内容")],
    category: Annotated[str | None, Query(description="按类别过滤")] = None,
    top_k: Annotated[int, Query(ge=1, le=20)] = 5,
    mode: Annotated[str, Query(description="mixed/fts/vector")] = "mixed",
    rerank: Annotated[bool, Query(description="是否重排")] = True,
    file: Annotated[str | None, Query(description="只在文件名含该子串的文档内检索")] = None,
    max_per_doc: Annotated[int, Query(ge=0, le=20, description="同一文件最多返回几条,0=不限")] = 0,
) -> list[dict]:
    table = _table()
    if table is None:
        return []
    return retrieval.search(table, q, category=category, top_k=top_k, mode=mode, rerank=rerank,
                            file=file, max_per_doc=max_per_doc)


@app.get("/api/history")
def get_history() -> list[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _ingest_busy() -> str:
    """若已有 ingest 在跑则返回 PID 字符串,否则空串。"""
    if not os.path.exists(LOCK_FILE):
        return ""
    try:
        pid = int(open(LOCK_FILE, encoding="utf-8").read().strip())
    except (ValueError, OSError):
        return ""
    return str(pid) if pid and _pid_alive(pid) else ""


def _spawn_ingest(extra_args: list[str]) -> None:
    # CREATE_NO_WINDOW 是 Windows 专有常量;Linux 上该属性不存在会 AttributeError
    # (容器里点"增量索引"即触发)。按平台取,非 Windows 留空。
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    subprocess.Popen([sys.executable, "-m", "backend.ingest", *extra_args],
                     cwd=str(ROOT.parent), creationflags=flags)


@app.post("/api/ingest")
def trigger_ingest(
    rebuild: Annotated[bool, Query(description="全量重建")] = False,
) -> dict:
    busy = _ingest_busy()
    if busy:
        return {"ok": False, "error": f"ingest 已在运行 (PID {busy})"}
    _spawn_ingest(["--rebuild"] if rebuild else [])
    return {"ok": True, "rebuild": rebuild}


@app.post("/api/ingest/files")
def reingest_files(payload: dict) -> dict:
    """重新提取指定文档(含低文本页的 OCR 兜底)。

    用途:某些文档提取质量差(扫描页、矢量正文)或元数据不对时,在前端勾选后重跑。
    逐个文件走同一条 ingest 流水线,顺带刷新 FTS 索引。
    """
    files = [f for f in (payload or {}).get("files", []) if isinstance(f, str)]
    if not files:
        return {"ok": False, "error": "未选择文件"}
    busy = _ingest_busy()
    if busy:
        return {"ok": False, "error": f"ingest 已在运行 (PID {busy})"}
    # 指定重索引的文件清单同样来自客户端:既要防穿越,也不能收绝对路径
    # (os.path.join 遇绝对路径会丢前缀,等于把语料库外的东西索引进来)。
    missing = []
    for f in files:
        try:
            doc_utils.resolve_under(config.PDF_ROOT, f)
        except FileNotFoundError:
            missing.append(f)
    if missing:
        return {"ok": False, "error": f"文件不存在或路径越界: {missing[0]}"}
    _spawn_ingest(["--force", *files])
    return {"ok": True, "count": len(files), "files": files}


@app.get("/api/extract/report")
def extract_report(limit: Annotated[int, Query(ge=1, le=500)] = 60) -> list[dict]:
    """逐文档的提取质量体检:每页字符数、低文本页占比、分块数。

    文本量异常偏低的文档在库里基本不可检索(整份只有页眉),需要在前端标出来
    以便重跑 OCR —— 这类问题此前完全不可见。

    结论按 (table.version, min_chars_per_page) 缓存:版本管 ingest,
    阈值管"改了告警线后 suspect 标记要跟着变"。limit 只截断、缓存全量。
    """
    table = _table()
    if table is None:
        return []
    threshold = config.get("min_chars_per_page")
    full = library.extract_report(table, threshold)
    return full[:limit]


# ---------- 配置:可调参数的读写 ----------
# 仅暴露 config.SPECS 里的可调项;密钥、根目录等环境类配置不在此列。

@app.get("/api/config")
def get_config() -> dict:
    return {"specs": config.snapshot(), "groups": config.GROUPS}


@app.put("/api/config")
def put_config(payload: dict) -> dict:
    values = payload.get("values") if isinstance(payload, dict) else None
    if not isinstance(values, dict) or not values:
        raise HTTPException(400, "请求体需为 {\"values\": {名称: 值}}")
    try:
        config.set_many(values)
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(400, str(e))
    retrieval.reset_client()          # 超时/连接数等可能已变,重建连接池
    retrieval.reset_cache()           # 检索参数已变,旧结果不可再用
    return {"ok": True, "specs": config.snapshot()}


@app.post("/api/config/reset")
def reset_config(payload: dict | None = None) -> dict:
    names = (payload or {}).get("names") or None
    if names is not None and not isinstance(names, list):
        raise HTTPException(400, "names 需为数组")
    config.reset(names)
    retrieval.reset_client()
    retrieval.reset_cache()
    return {"ok": True, "specs": config.snapshot()}


@app.get("/api/ocr/health")
def ocr_health() -> dict:
    """当前 OCR 配置 + 最近一次真实调用的结果。

    路径名沿用 health 以兼容既有前端/客户端,但**不做任何网络探测** ——
    状态来自真实调用记录,OCR 后端是否可用会在实际使用时暴露。
    """
    from . import ocr as ocr_mod
    return ocr_mod.status()


# ---------- 导出 / 导入 ----------
# 数据包较大(含索引与手册),采用"先构建到磁盘、再下载"的两步流程:
# 同步返回一个几百 MB 的响应体容易超时,而且重复下载会重复构建。

EXPORT_DIR = ROOT.parent / "data" / "exports"
_BUNDLE_SUFFIX = ".tar.zst"


@app.get("/api/export/config")
def export_config_file() -> FileResponse:
    """导出可调参数配置(不含任何密钥)。"""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = EXPORT_DIR / f"pdf-rag-config-{stamp}.json"
    bundle.export_config(dest)
    return FileResponse(dest, media_type="application/json",
                        filename=dest.name)


@app.post("/api/import/config")
def import_config_file(payload: dict) -> dict:
    """导入配置:只应用包内的可调项覆盖值。"""
    tunables = (payload or {}).get("tunables")
    if not isinstance(tunables, dict):
        raise HTTPException(400, "配置内容缺少 tunables 字段")
    try:
        config.set_many({k: v["value"] for k, v in tunables.items()})
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(400, str(e))
    retrieval.reset_client()
    retrieval.reset_cache()
    return {"ok": True, "specs": config.snapshot()}


def _bundle_path(name: str) -> Path:
    """把前端传来的文件名限制在导出目录内,避免路径穿越。"""
    if not name.endswith(_BUNDLE_SUFFIX) or os.sep in name or "/" in name:
        raise HTTPException(400, "非法的包名")
    return EXPORT_DIR / name


@app.get("/api/export/bundles")
def list_bundles() -> list[dict]:
    """已构建的数据包(含大小与清单摘要)。"""
    if not EXPORT_DIR.is_dir():
        return []
    out = []
    for p in sorted(EXPORT_DIR.glob(f"*{_BUNDLE_SUFFIX}"), reverse=True):
        item = {"name": p.name, "bytes": p.stat().st_size,
                "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
                "manifest": None}
        try:
            item["manifest"] = bundle.inspect_bundle(p)
        except Exception as e:
            item["error"] = str(e)
        out.append(item)
    return out


@app.post("/api/export/bundle")
def build_bundle(
    include_docs: Annotated[bool, Query(description="是否把 PDF 一并打包")] = True,
    level: Annotated[int, Query(ge=1, le=19, description="zstd 压缩级别")] = 6,
) -> dict:
    """构建数据包(索引 + 可选 PDF)。"""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = EXPORT_DIR / f"pdf-rag-bundle-{stamp}{_BUNDLE_SUFFIX}"
    try:
        return bundle.export_bundle(dest, include_docs=include_docs, level=level)
    except Exception as e:
        raise HTTPException(500, f"构建失败: {type(e).__name__}: {e}")


@app.get("/api/export/download")
def download_bundle(name: Annotated[str, Query(description="包文件名")]) -> FileResponse:
    p = _bundle_path(name)
    if not p.is_file():
        raise HTTPException(404, f"包不存在: {name}")
    return FileResponse(p, media_type="application/zstd", filename=p.name)


@app.delete("/api/export/bundle")
def delete_bundle(name: Annotated[str, Query(description="包文件名")]) -> dict:
    p = _bundle_path(name)
    if not p.is_file():
        raise HTTPException(404, f"包不存在: {name}")
    p.unlink()
    return {"ok": True}


@app.post("/api/import/inspect")
def inspect_import(payload: dict) -> dict:
    """导入前预检:读清单并校验与当前环境是否兼容,不解包、不改动任何数据。"""
    src = _bundle_path(str((payload or {}).get("name", "")))
    if not src.is_file():
        raise HTTPException(404, f"包不存在: {src.name}")
    try:
        manifest = bundle.inspect_bundle(src)
    except Exception as e:
        raise HTTPException(400, f"无法读取包: {type(e).__name__}: {e}")
    return {
        "name": src.name,
        "manifest": manifest,
        "provider": bundle.provider_diff(manifest),
        # 应用包内服务配置后即可用;保留本地配置则可能因模型不一致而不可用
        "blocking_if_apply": bundle._check_compatible(manifest, apply_provider=True),
        "blocking_if_keep": bundle._check_compatible(manifest, apply_provider=False),
    }


@app.post("/api/import/bundle")
def apply_import(payload: dict) -> dict:
    """执行导入。replace_index 时会先备份现有索引。"""
    body = payload or {}
    src = _bundle_path(str(body.get("name", "")))
    if not src.is_file():
        raise HTTPException(404, f"包不存在: {src.name}")
    result = bundle.import_bundle(
        src,
        restore_docs=bool(body.get("restore_docs", True)),
        replace_index=bool(body.get("replace_index", True)),
        apply_provider=bool(body.get("apply_provider", True)),
    )
    if not result.get("ok"):
        raise HTTPException(400, result.get("error", "导入失败"))
    retrieval.reset_client()      # 嵌入服务地址/模型可能已变,重建连接池
    retrieval.reset_cache()       # 索引已替换、模型可能已变,旧向量与旧结果都失效
    return result


@app.get("/api/pdf")
def get_pdf(
    file: Annotated[str, Query(description="文件路径")],
) -> FileResponse:
    try:
        full = doc_utils.resolve_under(config.PDF_ROOT, file)
    except FileNotFoundError:
        raise HTTPException(404, f"文件不存在或路径越界: {file}")
    if not os.path.isfile(full):
        raise HTTPException(404, f"文件不存在: {file}")
    if doc_utils.is_markdown(full):
        # MD 没有浏览器内联呈现,保持下载(filename → attachment)
        return FileResponse(full, media_type="text/markdown; charset=utf-8",
                            filename=os.path.basename(full))
    # PDF 不带 filename → Content-Disposition 缺席,浏览器原生 PDF 查看器内联打开;
    # 配合前端 `#page=N` 深链可直接定位到命中页。
    return FileResponse(full, media_type="application/pdf")


# ---------- 管理接口:自行重启 / 关闭 ----------
# 用途:进程被其他会话/终端占用(无法从外部 kill)时,通过 HTTP 让后端自己退出。
# 鉴权:X-Admin-Token 头必须等于 .env 的 ADMIN_TOKEN;未配置令牌时接口一律 403。

def _pid_alive(pid: int) -> bool:
    """与 run_backend.py 同口径:权限拒绝(5)时保守认为存活。"""
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    import ctypes
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if h:
        ctypes.windll.kernel32.CloseHandle(h)
        return True
    return ctypes.GetLastError() == 5


def _supervised() -> bool:
    """本进程是否由 run_backend.py 守护拉起(守护会给子进程注入 BACKEND_DAEMON_PID)。

    不读 run_backend.lock:该文件里的 PID 可能被系统复用或残留半死进程,
    导致"守护仍在"的永久误判。
    """
    pid = os.getenv("BACKEND_DAEMON_PID", "")
    return pid.isdigit() and _pid_alive(int(pid))


def _require_admin(token: str) -> None:
    if not config.ADMIN_TOKEN or not hmac.compare_digest(token, config.ADMIN_TOKEN):
        raise HTTPException(403, "forbidden")


def _spawn_daemon() -> None:
    """分离式拉起 run_backend.py(它自带单例锁与端口等待,会接替本进程)。"""
    flags = 0
    if os.name == "nt":
        DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP = 0x00000008, 0x00000200
        flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(
        [sys.executable, str(ROOT.parent / "run_backend.py")],
        cwd=str(ROOT.parent),
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=flags, close_fds=True,
    )


def _exit_soon(code: int) -> None:
    """先让响应返回,再退出进程;code=0 表示守护不再重启,非 0 表示要求重启。"""
    def _bye() -> None:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            os._exit(code)
    threading.Timer(0.3, _bye).start()


@app.post("/api/admin/restart")
def admin_restart(x_admin_token: Annotated[str, Header()] = "") -> dict:
    """重启后端:有守护监管时退出后由守护拉起,否则自行派生守护再退出。"""
    _require_admin(x_admin_token)
    supervised = _supervised()
    if not supervised:
        _spawn_daemon()
    _exit_soon(1)
    return {"ok": True, "action": "restart", "supervised": supervised}


@app.post("/api/admin/shutdown")
def admin_shutdown(x_admin_token: Annotated[str, Header()] = "") -> dict:
    """关闭后端并以 rc=0 退出,守护进程收到后不再重启。"""
    _require_admin(x_admin_token)
    _exit_soon(0)
    return {"ok": True, "action": "shutdown"}


DIST = ROOT.parent / "web" / "dist"
if DIST.is_dir():
    @app.middleware("http")
    async def no_cache_index(request, call_next):
        response = await call_next(request)
        if request.url.path in ("/", "/index.html"):
            response.headers["Cache-Control"] = "no-store"
        return response

    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="web")
