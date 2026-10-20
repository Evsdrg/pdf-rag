"""向量索引与手册的打包导出 / 导入。

包格式(单文件 `.tar.zst`,流式读写):

    manifest.json        版本、时间、计数、嵌入模型与维度、配置、文件清单(路径+md5)
    index/               LanceDB 索引目录原样打包
    docs/<相对路径>       索引引用到的 PDF,保持相对路径
    settings.json        可调参数的运行时覆盖

设计要点:

* **向量与嵌入模型绑定**。向量只有在同一模型、同一维度下才可比,换模型后旧向量
  与新查询向量不在同一空间,检索会静默变差。因此清单记录模型与维度,导入时校验,
  不一致则拒绝,避免"导入成功但检索全错"。
* **配置导出不含密钥**。EMBED_API_KEY 等只从环境读取,绝不写入包与配置文件。
* **导入不盲覆盖**。先备份现有索引再替换;已存在且 md5 相同的 PDF 跳过不重复写。
* **tar 成员路径做穿越校验**,防止 `../` 写到目标目录之外。
"""
import json
import os
import shutil
import tarfile
import tempfile
import time
from datetime import datetime
from pathlib import Path

import zstandard as zstd

from . import config, library

BUNDLE_FORMAT = "pdf-rag-bundle"
BUNDLE_VERSION = 1
MANIFEST_NAME = "manifest.json"
INDEX_ARCNAME = "index"
DOCS_ARCNAME = "docs"
SETTINGS_NAME = "settings.json"
DEFAULT_LEVEL = 10
_TRUTHY = ("1", "true", "yes", "on")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ==================== 配置导出 ====================

def config_payload() -> dict:
    """可导出的配置:可调参数的生效值 + 元数据 + 非敏感环境项。**不含任何密钥**。"""
    return {
        "format": "pdf-rag-config",
        "version": BUNDLE_VERSION,
        "exported_at": _now(),
        "tunables": config.snapshot(),
        # environment 只留真正 env-only 的部署项(路径)。索引吞吐/OCR 后端等
        # 已从常量迁入 tunables(config.snapshot 全量携带),不再重复。
        "environment": {
            "PDF_ROOT": config.PDF_ROOT,
            "DB_PATH": config.DB_PATH,
            "EMBED_BASE_URL": config.get("embed_base_url"),
            "EMBED_MODEL": config.get("embed_model"),
            "RERANKER_MODEL": config.get("reranker_model"),
            "ADMIN_TOKEN_CONFIGURED": bool(config.ADMIN_TOKEN),
        },
    }


def export_config(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(config_payload(), ensure_ascii=False, indent=1), encoding="utf-8")
    return dest


# ==================== 索引侧信息 ====================

def _indexed_files() -> list[dict]:
    """索引里引用到的文件清单(路径 + md5 + 页数)。"""
    import lancedb
    db = lancedb.connect(config.DB_PATH)
    if not db.list_tables():
        return []
    rows = db.open_table("chunks").to_arrow().select(
        ["file", "page", "md5"]).to_pylist()
    agg: dict[str, dict] = {}
    for r in rows:
        item = agg.setdefault(r["file"], {"file": r["file"], "md5": r["md5"], "pages": 0})
        item["pages"] = max(item["pages"], int(r["page"]) + 1)
    return sorted(agg.values(), key=lambda x: x["file"])


def _embedding_dim() -> int | None:
    import lancedb
    db = lancedb.connect(config.DB_PATH)
    if not db.list_tables():
        return None
    table = db.open_table("chunks")
    field = table.schema.field("vector") if hasattr(table.schema, "field") else None
    try:
        return field.type.list_size
    except Exception:
        return None


# 随包导出、导入可一并应用的嵌入服务项。密钥不在其中 —— 包可能被传给他人,
# 而服务地址与模型名不是秘密;导入方用自己的密钥访问同一个服务即可。
# input_type 与向量维度也在其中:它们是嵌入契约的一部分(建库与查询必须配对),
# 漏了它们,导入方算出的查询向量会和包内向量对不上。
PROVIDER_KEYS = ("embed_base_url", "embed_model", "reranker_model",
                 "embed_input_type_doc", "embed_input_type_query", "embed_dimensions")


def provider_block() -> dict:
    """当前嵌入服务配置(与向量强绑定,需随数据一起走)。**不含密钥**。"""
    return {k: config.get(k) for k in PROVIDER_KEYS}


def provider_diff(manifest: dict) -> dict:
    """比较包内与当前的嵌入服务配置。

    数据与模型强绑定的意义:向量只在同一模型、同一空间下才可比。把服务配置随
    数据一起带走,导入方就不必猜"这份向量是哪个模型生成的",也不必靠人记住。
    """
    bundled = manifest.get("provider") or manifest.get("embedding") or {}
    current = provider_block()
    changed = {
        k: {"bundle": bundled.get(k), "current": v}
        for k, v in current.items()
        if bundled.get(k) and bundled[k] != v
    }
    return {"bundle": bundled, "current": current, "changed": changed}


def _manifest() -> dict:
    docs = _indexed_files()
    provider = provider_block()
    return {
        "format": BUNDLE_FORMAT,
        "version": BUNDLE_VERSION,
        "created_at": _now(),
        "source": {"pdf_root": config.PDF_ROOT, "db_path": config.DB_PATH},
        "counts": {"documents": len(docs), "chunks": _chunk_count()},
        # 数据自带解释自己所需的模型:导入方据此对齐,而不是靠人记住
        "provider": provider,
        "embedding": {"base_url": provider["embed_base_url"],
                      "model": provider["embed_model"],
                      "dim": _embedding_dim()},
        "documents": docs,
    }


def _chunk_count() -> int:
    import lancedb
    db = lancedb.connect(config.DB_PATH)
    if not db.list_tables():
        return 0
    return db.open_table("chunks").to_arrow().num_rows


# ==================== 导出 ====================

def export_bundle(dest: Path, include_docs: bool = True, level: int = DEFAULT_LEVEL,
                  progress=None) -> dict:
    """打包索引(可选含 PDF)到 `dest`(.tar.zst)。返回统计信息。"""
    def say(msg: str):
        if progress:
            progress(msg)

    manifest = _manifest()
    manifest["includes_documents"] = bool(include_docs)
    dest.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    cctx = zstd.ZstdCompressor(level=level, threads=-1)
    with open(dest, "wb") as fh:
        with cctx.stream_writer(fh) as zw:
            # 流式写(不可 seek),避免在磁盘上落一个中间 tar
            with tarfile.open(fileobj=zw, mode="w|") as tar:
                say("写入清单")
                _tar_add_bytes(tar, MANIFEST_NAME,
                               json.dumps(manifest, ensure_ascii=False, indent=1).encode())
                say("写入索引")
                tar.add(config.DB_PATH, arcname=INDEX_ARCNAME)
                if include_docs:
                    _add_documents(tar, manifest["documents"], say)
                if config.SETTINGS_FILE.is_file():
                    say("写入配置")
                    tar.add(config.SETTINGS_FILE, arcname=SETTINGS_NAME)

    return {
        "path": str(dest), "bytes": dest.stat().st_size,
        "documents": len(manifest["documents"]), "includes_documents": bool(include_docs),
        "elapsed": round(time.time() - t0, 1), "manifest": manifest,
    }


def _add_documents(tar: tarfile.TarFile, docs: list[dict], say):
    missing = []
    for i, doc in enumerate(docs, 1):
        full = Path(config.PDF_ROOT) / doc["file"]
        if not full.is_file():
            missing.append(doc["file"])
            continue
        if i % 20 == 1:
            say(f"写入 PDF {i}/{len(docs)}")
        tar.add(full, arcname=f"{DOCS_ARCNAME}/{doc['file'].replace(os.sep, '/')}")
    if missing:
        say(f"警告:{len(missing)} 份 PDF 不在语料库中,已跳过")


def _tar_add_bytes(tar: tarfile.TarFile, name: str, data: bytes):
    import io
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = int(time.time())
    tar.addfile(info, io.BytesIO(data))


# ==================== 导入 ====================

def _safe_members(tar: tarfile.TarFile):
    """过滤掉会写到目标目录之外的成员(路径穿越)。"""
    for m in tar:
        parts = Path(m.name).parts
        if m.name.startswith(("/", "\\")) or ".." in parts:
            continue
        yield m


def _safe_extract(tar: tarfile.TarFile, dest: Path) -> list[str]:
    names = []
    for m in _safe_members(tar):
        tar.extract(m, path=dest, filter="data")
        names.append(m.name)
    return names


def inspect_bundle(src: Path) -> dict:
    """只读清单,不解包(供前端预览后再决定是否导入)。"""
    dctx = zstd.ZstdDecompressor()
    with open(src, "rb") as fh:
        with dctx.stream_reader(fh) as zr:
            with tarfile.open(fileobj=zr, mode="r|") as tar:
                for m in _safe_members(tar):
                    if m.name == MANIFEST_NAME:
                        data = tar.extractfile(m).read()
                        return json.loads(data)
    raise ValueError("包内缺少 manifest.json")


def _check_compatible(manifest: dict, apply_provider: bool = True) -> str:
    """返回空串表示可导入,否则返回拒绝原因。

    向量与嵌入模型强绑定,所以"是否应用包内的服务配置"决定了本次导入是否可行:

    * **apply_provider=True**:按包内配置切换嵌入服务,数据与模型重新配对,可用。
    * **apply_provider=False**:保留本地配置。此时模型不一致就无法使用 ——
      新旧向量不在同一空间,检索会静默劣化,宁可拒绝也不留一堆无用的向量。
    """
    if manifest.get("format") != BUNDLE_FORMAT:
        return "不是本系统的数据包"
    if int(manifest.get("version", 0)) > BUNDLE_VERSION:
        return f"包版本 {manifest.get('version')} 高于当前支持的 {BUNDLE_VERSION}"
    if apply_provider:
        return ""
    bundled = manifest.get("provider") or manifest.get("embedding") or {}
    if bundled.get("embed_model") and bundled["embed_model"] != config.get("embed_model"):
        return (f"嵌入模型不一致:包内 {bundled['embed_model']},"
                f"当前 {config.get('embed_model')}。可勾选「应用包内服务配置」后导入")
    emb = manifest.get("embedding") or {}
    if emb.get("dim") and _embedding_dim() and emb["dim"] != _embedding_dim():
        return f"向量维度不一致:包内 {emb['dim']},当前 {_embedding_dim()}"
    return ""


def apply_provider_config(manifest: dict) -> dict:
    """把包内的嵌入服务配置落为本地覆盖值(密钥仍取自本地环境)。

    这样"数据 + 解释它的模型"作为整体迁移:导入后不需要人工回忆/询问
    这份向量是用哪个服务、哪个模型生成的。
    """
    block = manifest.get("provider") or {}
    # 只写真正有差异的项:与本地一致时不制造多余的"已覆盖"状态,
    # 否则导入后配置面板里每项都显示被覆盖,掩盖了真正被改动的那几项。
    values = {k: block[k] for k in PROVIDER_KEYS
              if block.get(k) and block[k] != config.get(k)}
    if not values:
        return {}
    config.set_many(values)
    return values


def import_bundle(src: Path, restore_docs: bool = True, replace_index: bool = True,
                  apply_provider: bool = True, progress=None) -> dict:
    """导入数据包。

    replace_index=True 时先备份现有索引再替换;False 时只导入缺失的 PDF。
    apply_provider=True 时应用包内的嵌入服务配置(数据与模型强绑定)。
    """
    def say(msg: str):
        if progress:
            progress(msg)

    manifest = inspect_bundle(src)
    reason = _check_compatible(manifest, apply_provider=apply_provider)
    if reason:
        return {"ok": False, "error": reason}
    if not replace_index and not restore_docs:
        return {"ok": False, "error": "未指定要恢复的内容"}

    workdir = Path(tempfile.mkdtemp(prefix="pdfrag_bundle_"))
    backup = None
    t0 = time.time()
    try:
        say("解包")
        dctx = zstd.ZstdDecompressor()
        with open(src, "rb") as fh:
            with dctx.stream_reader(fh) as zr:
                with tarfile.open(fileobj=zr, mode="r|") as tar:
                    _safe_extract(tar, workdir)      # 流式:只能解到临时目录再搬

        applied = {}
        if apply_provider:
            applied = apply_provider_config(manifest)
            if applied:
                say("已应用包内嵌入服务配置")

        written = skipped = 0
        if restore_docs:
            written, skipped = _restore_documents(workdir / DOCS_ARCNAME, manifest, say)

        replaced = False
        if replace_index:
            new_index = workdir / INDEX_ARCNAME
            if not new_index.is_dir():
                return {"ok": False, "error": "包内没有索引目录"}
            backup = _backup_index()
            say("替换索引")
            shutil.rmtree(config.DB_PATH, ignore_errors=True)
            shutil.move(str(new_index), config.DB_PATH)
            # 旧表句柄指向已被删除的 inode;不重置会继续读旧数据或报错
            library.reset_table()
            replaced = True

        settings = workdir / SETTINGS_NAME
        if settings.is_file():
            config.SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(settings, config.SETTINGS_FILE)
            say("已恢复配置覆盖值")

        return {
            "ok": True, "documents_written": written, "documents_skipped": skipped,
            "index_replaced": replaced, "index_backup": backup,
            "provider_applied": applied,
            "elapsed": round(time.time() - t0, 1), "manifest": manifest,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _restore_documents(docs_dir: Path, manifest: dict, say) -> tuple[int, int]:
    """把包内 PDF 还原到语料库;已存在且 md5 相同的跳过。"""
    if not docs_dir.is_dir():
        return 0, 0
    import hashlib
    known = {d["file"]: d.get("md5") for d in manifest.get("documents", [])}
    written = skipped = 0
    for i, path in enumerate(sorted(docs_dir.rglob("*")), 1):
        if not path.is_file():
            continue
        rel = path.relative_to(docs_dir).as_posix().replace("/", os.sep)
        target = Path(config.PDF_ROOT) / rel
        want = known.get(rel)
        if target.is_file() and want:
            digest = hashlib.md5(target.read_bytes()).hexdigest()
            if digest == want:
                skipped += 1
                continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        written += 1
        if written % 20 == 1:
            say(f"还原 PDF {i}(新增 {written})")
    return written, skipped


def _backup_index() -> str | None:
    """替换索引前先备份,返回备份路径。"""
    if not Path(config.DB_PATH).exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = f"{config.DB_PATH}.bak-{stamp}"
    shutil.move(config.DB_PATH, dest)
    return dest
