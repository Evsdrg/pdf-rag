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
    """当前分区的向量维度。

    主表已无 vector 列(向量在 vec_<slug> 分区),维度从分区表读;分区不存在时
    退回配置值 —— 数据包仍要带上维度,导入方凭它校验。
    """
    from . import vecstore
    import lancedb
    db = lancedb.connect(config.DB_PATH)
    part = vecstore.open_partition(db, vecstore.current_slug())
    if part is not None:
        try:
            return part.schema.field("vector").type.list_size
        except Exception:
            pass
    return config.get("embed_dimensions") or None


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
        # 包内可能带多个模型的分区(用户换着用过)。列出契约,导入方才能知道
        # 自己能用哪些、缺哪些;单分区时这就是现役模型那一条。
        "vector_partitions": _partition_block(),
        "documents": docs,
    }


def _partition_block() -> list[dict]:
    """包内各向量分区的契约与覆盖量(不含向量本身)。"""
    from . import vecstore
    import lancedb
    db = lancedb.connect(config.DB_PATH)
    metas = vecstore.list_partitions(db)
    main = db.open_table("chunks") if "chunks" in vecstore.table_names(db) else None
    out = []
    for m in metas:
        item = {k: m.get(k) for k in ("slug", "model", "dim", "input_type_doc",
                                      "input_type_query", "blocks", "files",
                                      "created_at", "updated_at")}
        if main is not None:
            cov = vecstore.coverage(db, main, m["slug"])
            item["blocks_covered"] = cov["blocks_covered"]
            item["ratio"] = round(cov["ratio"], 4)
        out.append(item)
    return out


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


def _local_usable_partitions(manifest: dict) -> list[str]:
    """包内分区里,本地**无需切换配置就能直接用**的那些。

    判据:模型名与本地 `embed_model` 相同(维度/input_type 保持包内契约,查询侧
    会按分区记录成对生成向量,所以不必要求与本地配置完全一致)。
    老包(v1)没有 vector_partitions,退回看 embedding 块。
    """
    from . import vecstore
    parts = manifest.get("vector_partitions")
    if not parts:
        emb = manifest.get("embedding") or {}
        model = emb.get("model")
        return [vecstore.model_slug(model, emb.get("dim"))] if model == config.get("embed_model") else []
    cur_model = str(config.get("embed_model"))
    return [p["slug"] for p in parts if p.get("model") == cur_model]


def _check_compatible(manifest: dict, apply_provider: bool = True) -> str:
    """返回空串表示可导入,否则返回拒绝原因。

    向量与嵌入模型强绑定,所以"是否应用包内的服务配置"决定了本次导入是否可行:

    * **apply_provider=True**:按包内配置切换嵌入服务,数据与模型重新配对,可用。
    * **apply_provider=False**:保留本地配置。此时**只要包内有本地模型能用的分区**
      就允许导入——包里可能带多个模型的分区,本地与其一匹配即可;一个都匹配不上
      才拒绝,否则导入的是一堆当前用不了的向量。
    """
    if manifest.get("format") != BUNDLE_FORMAT:
        return "不是本系统的数据包"
    if int(manifest.get("version", 0)) > BUNDLE_VERSION:
        return f"包版本 {manifest.get('version')} 高于当前支持的 {BUNDLE_VERSION}"
    if apply_provider:
        return ""
    usable = _local_usable_partitions(manifest)
    if usable:
        return ""
    parts = manifest.get("vector_partitions") or []
    have = ", ".join(sorted({str(p.get("model")) for p in parts})) or "（包内无分区清单）"
    return (f"包内没有本地模型({config.get('embed_model')})可用的向量分区:"
            f"包内为 {have}。可勾选「应用包内服务配置」后导入,或先用本地模型重建向量")


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

        picked = _apply_partition_priority(manifest) if replaced else []
        if picked:
            say(f"已把包内可用分区写入优先级: {', '.join(picked)}")

        return {
            "ok": True, "documents_written": written, "documents_skipped": skipped,
            "index_replaced": replaced, "index_backup": backup,
            "provider_applied": applied, "partition_priority": picked,
            "elapsed": round(time.time() - t0, 1), "manifest": manifest,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _apply_partition_priority(manifest: dict) -> list[str]:
    """导入后把包内**本地可用**的分区写进优先级,否则多分区包等于白带。

    只在用户没有显式设过优先级时才写——尊重既有选择,不覆盖用户配置。
    返回写入的分区列表(未写时为空)。
    """
    from . import vecstore
    usable = _local_usable_partitions(manifest)
    if not usable or str(config.get("vector_models_priority") or "").strip():
        return []
    try:
        config.set_many({"vector_models_priority": ", ".join(usable)})
    except Exception:
        return []
    return usable


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
