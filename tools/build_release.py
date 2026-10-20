# -*- coding: utf-8 -*-
"""构建交付包:项目源码 + 原始手册 PDF + 解析后数据 + 预处理索引,打成可分发的包。

产出(默认落在 dist/ 下,该目录已被 .gitignore 忽略):

    pdf-rag-<日期>/              可直接拷贝运行的目录
    pdf-rag-<日期>.tar.zst       压缩包(zstd;PDF 已是压缩格式,收益主要在索引与文本)

用法:

    uv run python tools/build_release.py                   # 默认 tar.zst
    uv run python tools/build_release.py --format zip      # 改打 zip
    uv run python tools/build_release.py --format both     # 两种都出
    uv run python tools/build_release.py --out E:\\交付      # 指定输出目录
    uv run python tools/build_release.py --no-archive      # 只生成目录,不压缩
    uv run python tools/build_release.py --no-docs         # 不带 PDF(只交代码+索引+解析数据)

前置:工作区已提交(git archive HEAD 取源码),PDF 与索引就位。
"""
import argparse
import io
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
from pathlib import Path

import zstandard as zstd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend import bundle, config   # noqa: E402  (需先设置 sys.path)

DOCS_DIRNAME = "pdf"          # 包内手册目录,与 config 的 PDF_ROOT 默认值一致
INDEX_DIRNAME = "index.lance"  # 包内索引目录,与 config 的 DB_PATH 默认值一致
PARSED_DIRNAME = "parsed"      # 包内解析后数据(块级 jsonl + 页级文本)
MANIFEST_NAME = "MANIFEST.txt"
STORED_SUFFIXES = {".pdf"}     # zip 时原样存储:已是压缩格式,再 deflate 只费 CPU
ZSTD_LEVEL = 10                # 文本与索引收益明显,选个适中的档位
FRONTEND_DIST = ROOT / "web" / "dist"


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, check=True, **kw)


def stage_source(dest: Path) -> int:
    """用 git archive 取 HEAD 的源码 —— 天然排除运行期产物、.env、node_modules。"""
    proc = _run(["git", "archive", "--format=tar", "HEAD"], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=io.BytesIO(proc.stdout), mode="r|") as tar:
        tar.extractall(dest, filter="data")   # 显式过滤:git 产物无需保留权限位
    return sum(1 for _ in dest.rglob("*") if _.is_file())


def stage_frontend(dest: Path) -> None:
    """前端构建产物不在版本库里(gitignore),需从工作区单独拷入。"""
    if not (FRONTEND_DIST / "index.html").is_file():
        raise SystemExit(f"缺少前端构建产物: {FRONTEND_DIST}\\index.html\n"
                         "先在 web/ 下执行 npm run build")
    shutil.copytree(FRONTEND_DIST, dest / "web" / "dist")


def stage_index(dest: Path) -> None:
    src = Path(config.DB_PATH)
    if not src.is_dir():
        raise SystemExit(f"索引不存在: {src}\n先跑 uv run python -m backend.ingest")
    shutil.copytree(src, dest / INDEX_DIRNAME)


def stage_docs(dest: Path) -> tuple[int, list[str]]:
    """按索引里记录的相对路径拷 PDF —— 保证包内每个被索引引用的文件都在。

    返回 (拷贝份数, 索引引用但磁盘缺失的文件)。
    """
    root = Path(config.PDF_ROOT)
    dest_root = dest / DOCS_DIRNAME
    copied = 0
    missing: list[str] = []
    for doc in bundle._indexed_files():
        rel = doc["file"]
        src = root / rel
        if not src.is_file():
            missing.append(rel)
            continue
        target = dest_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        copied += 1
    return copied, missing


def stage_parsed(dest: Path) -> None:
    """解析后数据(块级 jsonl + 页级文本),复用 export_parsed 以免逻辑重写一遍。"""
    tool = ROOT / "tools" / "export_parsed.py"
    subprocess.run([sys.executable, str(tool), "--out", str(dest / PARSED_DIRNAME)],
                   check=True, cwd=ROOT)


def write_manifest(dest: Path, docs: int) -> None:
    provider = bundle.provider_block()
    index_mb = sum(f.stat().st_size for f in (dest / INDEX_DIRNAME).rglob("*")
                   if f.is_file()) / 1048576
    parsed = dest / PARSED_DIRNAME
    n_chunks = sum(1 for _ in open(parsed / "chunks.jsonl", encoding="utf-8")) \
        if (parsed / "chunks.jsonl").is_file() else 0
    lines = [
        "PDF-RAG 交付包",
        "=" * 40,
        f"构建时间    : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"源码提交    : {_git_rev()}",
        "",
        f"手册文档数  : {docs}",
        f"索引块数    : {bundle._chunk_count()}",
        f"索引体积    : {index_mb:.0f} MB",
        f"解析数据块  : {n_chunks} 条({PARSED_DIRNAME}/chunks.jsonl)",
        "",
        "包内三份数据:",
        f"  {DOCS_DIRNAME}/        原始 PDF(未改动)",
        f"  {PARSED_DIRNAME}/      解析后数据:块级 jsonl + 按页重建的可读文本",
        f"  {INDEX_DIRNAME}/       向量索引(含全文索引),可直接检索,无需重建",
        "",
        "-- 索引所用嵌入服务(向量与模型强绑定) --",
        f"EMBED_BASE_URL = {provider['embed_base_url']}",
        f"EMBED_MODEL    = {provider['embed_model']}",
        f"RERANKER_MODEL = {provider['reranker_model']}",
        "",
        "⚠️ 部署时 .env 的 EMBED_MODEL 必须与上表一致,否则向量不可比、检索会静默变差;",
        "   确需换模型则必须全量重建索引:uv run python -m backend.ingest --rebuild",
        "⚠️ API 密钥不随包提供,需自行在 .env 填写 EMBED_API_KEY。",
        "",
        "部署步骤见 DEPLOY.md。",
    ]
    (dest / MANIFEST_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _git_rev() -> str:
    p = _run(["git", "log", "-1", "--format=%h %s"], stdout=subprocess.PIPE)
    return p.stdout.decode("utf-8", "replace").strip()


def _members(stage: Path):
    """按路径排序产出 (绝对路径, 归档内相对名),目录先于其内容。"""
    for path in sorted(stage.rglob("*")):
        yield path, path.relative_to(stage.parent).as_posix()


def make_tarzst(stage: Path, out: Path) -> int:
    """zstd 压缩包。流式写,不在磁盘上落中间 tar。"""
    count = 0
    cctx = zstd.ZstdCompressor(level=ZSTD_LEVEL, threads=-1)
    with open(out, "wb") as fh:
        with cctx.stream_writer(fh) as zw:
            with tarfile.open(fileobj=zw, mode="w|") as tar:
                tar.add(stage, arcname=stage.name, recursive=False)
                for path, arcname in _members(stage):
                    tar.add(path, arcname=arcname, recursive=False)
                    count += path.is_file()
    return count


def make_zip(stage: Path, out: Path) -> int:
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path, arcname in _members(stage):
            if not path.is_file():
                continue
            method = (zipfile.ZIP_STORED if path.suffix.lower() in STORED_SUFFIXES
                      else zipfile.ZIP_DEFLATED)
            zf.write(path, arcname, compress_type=method)
            count += 1
    return count


def verify(stage: Path, missing: list[str]) -> list[str]:
    """交付前的自检:该在的都在,且索引引用的手册一份不缺。"""
    problems = []
    if missing:
        problems.append(f"索引引用但磁盘缺失 {len(missing)} 份: {missing[:3]}")
    for rel in (".env.example", "DEPLOY.md", "MANIFEST.txt", "server.py",
                "run_backend.py", "backend/main.py", "web/dist/index.html",
                f"{PARSED_DIRNAME}/chunks.jsonl", f"{PARSED_DIRNAME}/README.txt"):
        if not (stage / rel).exists():
            problems.append(f"缺少 {rel}")
    n_pdf = sum(1 for f in (stage / DOCS_DIRNAME).rglob("*")
                if f.is_file() and f.suffix.lower() in STORED_SUFFIXES)
    if n_pdf == 0:
        problems.append("包内没有任何手册")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description="构建 PDF-RAG 交付包")
    ap.add_argument("--out", default=str(ROOT / "dist"), help="输出目录(默认 dist/)")
    ap.add_argument("--format", default="tar.zst", choices=["tar.zst", "zip", "both"],
                    help="压缩格式(默认 tar.zst)")
    ap.add_argument("--no-archive", action="store_true", help="只生成目录,不压缩")
    ap.add_argument("--no-docs", action="store_true", help="不带手册 PDF")
    args = ap.parse_args()

    out_root = Path(args.out).resolve()
    name = f"pdf-rag-{time.strftime('%Y%m%d')}"
    stage = out_root / name
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    print(f"输出目录: {out_root}")
    print("[1/6] 取源码(git archive HEAD) ...", end=" ", flush=True)
    n_src = stage_source(stage)
    print(f"{n_src} 个文件")

    print("[2/6] 前端构建产物 ...", end=" ", flush=True)
    stage_frontend(stage)
    print("ok")

    print("[3/6] 向量索引 ...", end=" ", flush=True)
    stage_index(stage)
    print("ok")

    print("[4/6] 解析后数据 ...", end=" ", flush=True)
    stage_parsed(stage)
    print("ok")

    docs = 0
    missing: list[str] = []
    if args.no_docs:
        print("[5/6] 原始 PDF ... 跳过(--no-docs)")
    else:
        print("[5/6] 原始 PDF ...", end=" ", flush=True)
        docs, missing = stage_docs(stage)
        print(f"{docs} 份" + (f",缺失 {len(missing)}" if missing else ""))

    write_manifest(stage, docs)
    print(f"[6/6] 写入 {MANIFEST_NAME}")

    problems = verify(stage, missing)
    size_mb = sum(f.stat().st_size for f in stage.rglob("*") if f.is_file()) / 1048576
    print(f"\n目录就绪: {stage}  ({size_mb:.0f} MB)")
    if problems:
        print("\n⚠️ 自检发现问题:")
        for p in problems:
            print(f"   - {p}")
    else:
        print("自检通过 ✓")

    if args.no_archive:
        print("\n完成(未压缩)。")
        return
    formats = ["tar.zst", "zip"] if args.format == "both" else [args.format]
    for fmt in formats:
        archive = out_root / (f"{name}.tar.zst" if fmt == "tar.zst" else f"{name}.zip")
        print(f"\n压缩为 {fmt} ...", end=" ", flush=True)
        t0 = time.time()
        n = make_tarzst(stage, archive) if fmt == "tar.zst" else make_zip(stage, archive)
        print(f"{n} 个文件, {archive.stat().st_size / 1048576:.0f} MB, "
              f"{time.time() - t0:.0f}s")
        print(f"压缩包: {archive}")
    print("\n完成。")


if __name__ == "__main__":
    main()
