import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime

import fitz
import httpx
import lancedb
import pyarrow as pa

from . import config
from . import doc_utils
from .doc_utils import version_key

# 分块与 OCR 阈值统一由 config 提供,便于前端调整(见 config.SPECS「文档提取」组)
C_ID_RE = re.compile(r"^C\d+")
# 文档类型词:文件名不含 C 编号约定时,若 model_no 命中这些词则视为无效型号
DOC_TYPE_WORDS = ("规格书", "手册", "指南", "说明书", "原理图", "参考", "用户", "快速", "使用")

MB = 1024 * 1024


# ---------- 文件扫描 ----------

def iter_pdfs(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in config.SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith((".pdf",) + doc_utils.MD_SUFFIXES):
                full = os.path.join(dirpath, fn)
                # 归一为正斜杠:索引里的路径会被 bundle 导出、eval 断言、客户端
                # 引用,必须与平台无关。eval_queries.json 里 43/55 条 expect 曾是
                # Windows 反斜杠路径(早期在 Windows 上建索引),Linux 侧全部失配。
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                yield full, rel


def file_md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(MB), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- 元数据解析 ----------

def parse_version(stem: str) -> str:
    """从文件名提取版本号:V1.9 / V1.2.0 / RevD,无则空"""
    m = re.search(r"[Vv](\d+(?:\.\d+)*)", stem)
    if m:
        return m.group(1)
    m = re.search(r"Rev\.?\s*([A-Za-z]+)", stem)
    if m:
        return m.group(1).upper()
    return ""


# 版本号形态(V1.0 / V6.1.4 / 1.2.0 / revD 之类),不是型号
_VER_LIKE_RE = re.compile(r"^[VvRr]?[Ee]?[Vv]?\.?\s*\d+([._\-]\d+)*[A-Za-z]?$")


def _is_part_like(s: str) -> bool:
    """判断一个分段是否像料号。

    料号的共同特征:纯 ASCII、同时含字母与数字、且不是版本号。
    单看"含数字"会把 V1.0 / V6.1.4 这类版本段误当型号(实测踩过);
    不限 ASCII 则会把中文描述段(如 "4G系列")当型号。
    """
    if not s or not s.isascii():
        return False
    if not (re.search(r"[A-Za-z]", s) and re.search(r"\d", s)):
        return False
    if _VER_LIKE_RE.match(s):
        return False
    return not any(w in s for w in DOC_TYPE_WORDS)


def _pick_model(parts: list[str]) -> str:
    """从文件名分段里挑型号。找不到合格候选时返回空串 —— 宁可不填,也不填错。

    据此可跳过厂商/品牌段与版本段:
        Quectel_EC800M-CN_硬件设计手册_V1.2  → EC800M-CN(而不是 Quectel)
        Murata_BLM31_磁珠_规格书              → BLM31
        KEMET_T491_钽电容_规格书              → T491
        HTTP_HTTPS用户手册_V6.1.4             → ""(没有料号,也不该填 V6.1.4)
    """
    for p in parts[:3]:
        if _is_part_like(p):
            return p
    return ""


def parse_meta(rel: str, category_dir: str) -> dict:
    stem = os.path.splitext(os.path.basename(rel))[0]
    parts = stem.split("_")
    c_id = parts[0] if parts and C_ID_RE.match(parts[0]) else ""
    if c_id and len(parts) > 2:
        # C 编号约定:C<id>_<类别>_<型号>_<文档类型>_...
        model = parts[2] if _is_part_like(parts[2]) else _pick_model(parts[2:])
    elif parts and not c_id:
        model = _pick_model(parts)
    else:
        model = ""
    # 型号疑似文档类型词 → 清空,避免去重时被错误型号干扰
    if model and any(w in model for w in DOC_TYPE_WORDS):
        model = ""
    category = category_dir or (parts[1] if c_id and len(parts) > 1 else "")
    return {"c_id": c_id, "category": category, "model_no": model,
            "version": parse_version(stem)}


def category_from_dir(path: str, root: str) -> str:
    rel_dir = os.path.relpath(os.path.dirname(path), root)
    if rel_dir == ".":
        return ""
    top = rel_dir.split(os.sep)[0]
    return top


# ---------- PDF 提取与分块 ----------

def clean_text(s: str) -> str:
    return s.encode("utf-8", errors="ignore").decode("utf-8")


def split_into_chunks(text: str, max_chars: int = 0, overlap: int = -1) -> list[str]:
    """按空行(段落)边界贪心聚合到 max_chars,相邻块间保留 overlap 字重叠。

    优先在段落边界切断,避免参数表/句子被硬拆;重叠缓解边界处的信息断裂。
    单段落超长时按换行硬切,尽量保留表格/列表的行结构。
    """
    max_chars = max_chars or config.get("chunk_max_chars")
    overlap = config.get("chunk_overlap_chars") if overlap < 0 else overlap
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paras:
        return []
    chunks: list[str] = []
    cur = ""
    for p in paras:
        # 单段落超长:按换行硬切
        while len(p) > max_chars:
            if cur:
                chunks.append(cur)
                cur = cur[-overlap:] if overlap else ""
            cut = p.rfind("\n", 0, max_chars)
            if cut < max_chars // 2:
                cut = max_chars
            chunks.append(p[:cut])
            p = p[cut:].lstrip()
        if not p:
            continue
        # 并入当前块;放不下则收尾并开启新块(带重叠)
        if cur and len(cur) + 1 + len(p) > max_chars:
            chunks.append(cur)
            cur = (cur[-overlap:] + "\n" + p) if overlap else p
        else:
            cur = f"{cur}\n{p}" if cur else p
    if cur:
        chunks.append(cur)
    return chunks


def ocr_page(page: "fitz.Page", workdir: str) -> tuple[str, str]:
    """渲染无文本页为图片,调 OCR 服务识别。返回 (文本, 错误信息)。

    错误信息必须回传:历史上这里 except 后直接返回空串,调用方看到"OCR 无增益"
    就继续入库,于是整份图片型 PDF 带着每页十几字符的页眉进了索引,在库里等于
    不存在(实例:XBL1117-3.3 手册,14 页共 156 字符)。
    """
    try:
        pix = page.get_pixmap(dpi=config.get("ocr_dpi"))
        img = os.path.join(workdir, f"ocr_p{page.number}.png")
        pix.save(img)
        from . import ocr as ocr_mod
        text, err = ocr_mod.ocr_image(img)
        if err:
            return "", err
        return clean_text(text), ""
    except Exception as e:
        return "", f"{type(e).__name__}: {e}"


class _PageText:
    """单页文本抽取的累计结果:告警与 OCR 用量。

    抽成小对象是为了把原先三层判断(是否低文本 → OCR 是否成功 → 表格是否失败)
    收进一处,避免主流程嵌套过深。
    """

    def __init__(self):
        self.warnings: list[str] = []
        self.ocr_calls = 0
        self.ocr_failed = 0

    def harvest(self, page, number: int, ocr_dir: str) -> str:
        """返回该页最终文本(含表格 markdown)。"""
        text = page.get_text("text")
        if len(text.strip()) < config.get("ocr_min_chars"):
            text = self._rescue_by_ocr(page, number, text, ocr_dir)
        return self._append_tables(page, number, text)

    def _rescue_by_ocr(self, page, number: int, text: str, ocr_dir: str) -> str:
        """文本层缺失或极稀少(正文被转成矢量曲线等)时用 OCR 兜底。"""
        self.ocr_calls += 1
        ocr, err = ocr_page(page, ocr_dir)
        if err:
            self.ocr_failed += 1
            self.warnings.append(f"p{number} OCR 调用失败: {err}")
        elif len(ocr) > len(text):
            return ocr
        else:
            self.warnings.append(
                f"p{number} 低文本({len(text)} 字符)且 OCR 无增益({len(ocr)} 字符)")
        return text

    def _append_tables(self, page, number: int, text: str) -> str:
        from .doc_utils import table_to_md
        try:
            for t in page.find_tables().tables:
                md = table_to_md(t.extract())
                if md:
                    text += f"\n\n[表格]\n{md}"
        except Exception as e:
            self.warnings.append(f"p{number} 表格提取失败: {type(e).__name__}")
        return re.sub(r"\n{3,}", "\n\n", clean_text(text)).strip()

    def check_document(self, chunks: list, n_pages: int):
        """入库前体检:整份文本量异常偏低说明提取与 OCR 都没成功,需告警。

        实例:XBL1117-3.3 手册曾以每页 11 字符(只有页眉)入库,在库里等于不存在。
        """
        if not chunks:
            return
        total = sum(len(c[0]) for c in chunks)
        per_page = total / max(1, n_pages)
        threshold = config.get("min_chars_per_page")
        if per_page < threshold:
            self.warnings.append(
                f"整份文本量异常: {total} 字符 / {n_pages} 页 = {per_page:.0f} 字符/页"
                f"(低于阈值 {threshold}),该文档入库后基本不可检索")


def _extract_md(path: str, rel: str, category_dir: str) -> tuple:
    """Markdown 提取:按一级标题切伪页后分块,与 PDF 路径产出同构的元数据。"""
    meta = parse_meta(rel, category_dir)
    # 标题:优先取首个一级标题,否则用型号
    outline = doc_utils.md_outline(path)
    h1 = next((o["title"] for o in outline if o["level"] == 1), "")
    meta["title"] = h1 or meta.get("model_no", "")
    chunks: list[tuple[str, int]] = []
    for number, page in enumerate(doc_utils.md_pages(path)):
        # 去掉标题行本身(它只是分页标记),保留正文与表格
        body = "\n".join(ln for ln in page.split("\n")
                         if not re.match(r"^#{1,6}\s+", ln))
        chunks.extend((seg, number) for seg in split_into_chunks(body))
    return meta, chunks


def extract_chunks(path: str, rel: str, category_dir: str, ocr_dir: str):
    if doc_utils.is_markdown(path):
        return _extract_md(path, rel, category_dir)
    meta = parse_meta(rel, category_dir)
    tracker = _PageText()
    chunks: list[tuple[str, int]] = []
    doc = fitz.open(path)
    try:
        # 文档标题:优先 PDF 元数据标题,否则型号,否则留空(由调用方兜底)
        meta["title"] = (doc.metadata or {}).get("title", "").strip() or meta.get("model_no", "")
        n_pages = len(doc)                     # 必须在此取值:doc.close() 后不可再访问
        for number, page in enumerate(doc):
            text = tracker.harvest(page, number + 1, ocr_dir)
            chunks.extend((seg, number) for seg in split_into_chunks(text))
    finally:
        doc.close()

    tracker.check_document(chunks, n_pages)
    if tracker.ocr_calls:
        meta["ocr"] = {"calls": tracker.ocr_calls, "failed": tracker.ocr_failed}
    meta["warnings"] = tracker.warnings
    return meta, chunks


# ---------- embedding ----------

def _new_client() -> httpx.Client:
    return httpx.Client(timeout=180, headers={"Authorization": f"Bearer {config.EMBED_API_KEY}"})


def embed_batch(client: httpx.Client, texts: list[str]) -> list[list[float]]:
    url = f"{str(config.get('embed_base_url')).rstrip('/')}/embeddings"
    payload = {"model": config.get("embed_model"), "input": texts}
    input_type = config.get("embed_input_type_doc")
    if input_type:                 # Cohere 系需要;留空则不发送(OpenAI 兼容模型)
        payload["input_type"] = input_type
    dim = config.get("embed_dimensions")
    if dim:                        # 显式声明维度,与查询侧保持一致
        payload["dimensions"] = dim
    last_err = None
    attempts = config.get("embed_attempts")
    for attempt in range(attempts):
        try:
            r = client.post(url, json=payload)
            if r.status_code in _THROTTLE_STATUS:
                # 限流按分钟计,退避得比"偶发失败"长得多,否则整轮索引白跑
                # (实测一次全量重算在建到一半时被 429 打断)。
                # 服务商给了 Retry-After 就照办,没有则按 5s 起指数退避。
                wait = _retry_after(r) or 5 * (2 ** attempt)
                print(f"  [限流] embedding HTTP {r.status_code},"
                      f"等待 {wait:.0f}s 后重试 ({attempt + 1}/{attempts})",
                      file=sys.stderr, flush=True)
                last_err = f"HTTP {r.status_code} 限流"
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()["data"]
            return [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"embedding 失败({attempts}次重试): {last_err}")


_THROTTLE_STATUS = (403, 429)


def _retry_after(r) -> float | None:
    """服务商给的 Retry-After(秒);没有或不是数字则返回 None。"""
    try:
        return float(r.headers.get("Retry-After", ""))
    except ValueError:
        return None


def embed_file(rel: str, chunks: list[tuple[str, int]], n_batches: list[int]) -> list[dict]:
    texts = [c[0] for c in chunks]
    out = []
    client = _new_client()
    for start in range(0, len(texts), config.get("embed_batch")):
        batch = texts[start : start + config.get("embed_batch")]
        vecs = embed_batch(client, batch)
        for (text, page), v in zip(chunks[start : start + config.get("embed_batch")], vecs):
            out.append({"text": text, "page": page, "vector": v})
        n_batches[0] += 1
    return out


# ---------- LanceDB ----------

def schema(dim: int) -> pa.schema:
    return pa.schema([
        pa.field("text", pa.string()),
        pa.field("file", pa.string()),
        pa.field("page", pa.int32()),
        pa.field("category", pa.string()),
        pa.field("model_no", pa.string()),
        pa.field("c_id", pa.string()),
        pa.field("version", pa.string()),
        pa.field("title", pa.string()),
        pa.field("md5", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), dim)),
    ])


def esc_file(file: str) -> str:
    return file.replace("'", "''")


_PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(_PROJ_ROOT, "run_state.json")
LOCK_FILE = os.path.join(_PROJ_ROOT, "ingest.lock")
HISTORY_FILE = os.path.join(_PROJ_ROOT, "ingest_history.json")


def pid_exists(pid: int) -> bool:
    """进程是否存活(跨平台)。

    原实现只用 ctypes.windll(Windows 专有),Linux 上进容器跑增量索引会直接
    AttributeError —— 与 backend/main.py 的 _pid_alive 统一为同一口径。
    """
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    import ctypes
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return False
    ctypes.windll.kernel32.CloseHandle(h)
    return True


def acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            pid = int(open(LOCK_FILE, encoding="utf-8").read().strip())
        except (ValueError, OSError):
            pid = 0
        if pid and pid_exists(pid):
            sys.exit(f"错误: ingest 已在运行 (PID {pid}),请勿重复启动")
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


def release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception:
        pass


def dir_size_mb(path: str) -> float:
    total = 0
    if not os.path.isdir(path):
        return 0.0
    for dirpath, _, filenames in os.walk(path):
        for fn in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, fn))
            except OSError:
                pass
    return round(total / 1048576, 1)


def write_state(state: dict):
    state["db_size_mb"] = dir_size_mb(config.DB_PATH)
    try:
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)
    except Exception:
        pass


def extract_one(args):
    rel, full, md5, root = args
    ocr_dir = tempfile.mkdtemp(prefix="pdfrag_ocr_")
    try:
        category_dir = category_from_dir(full, root)
        meta, chunks = extract_chunks(full, rel, category_dir, ocr_dir)
        return rel, full, md5, meta, chunks
    finally:
        try:
            import shutil
            shutil.rmtree(ocr_dir, ignore_errors=True)
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true", help="清空索引全量重建")
    ap.add_argument("--force", nargs="*", default=None,
                    help="强制重处理:指定文件(相对路径),不带参数则全部文件")
    args = ap.parse_args()

    acquire_lock()
    try:
        _run(args)
    finally:
        release_lock()


def _plan_work(files: dict, known: dict, args) -> tuple[list, set]:
    """算出待处理的文件与已删除的文件。md5 未变且未显式 --force 的跳过。"""
    force_all = bool(args.force is not None and len(args.force) == 0)   # --force 无参 = 全部
    forced = {f.replace("\\", "/") for f in (args.force or [])}
    todo = []
    for rel, full in files.items():
        md5 = file_md5(full)
        if known.get(rel) == md5 and not (force_all or rel.replace("\\", "/") in forced):
            continue
        todo.append((rel, full, md5))
    return todo, set(known) - set(files)


def _extract_phase(to_index: list, root: str, state: dict, t0: float) -> list:
    """阶段一:多进程提取。find_tables 不释放 GIL,必须用进程绕开。"""
    total = len(to_index)
    state.update({"phase": "extracting", "extract": {"done": 0, "total": total}})
    write_state(state)
    extracted = []
    with ProcessPoolExecutor(config.get("extract_workers")) as ex:
        futures = {ex.submit(extract_one, (rel, full, md5, root)): (rel, full, md5)
                   for rel, full, md5 in to_index}
        for done, fut in enumerate(as_completed(futures), 1):
            rel, full, md5, meta, chunks = fut.result()
            state.update({"extract": {"done": done, "total": total},
                          "current": rel, "elapsed": round(time.time() - t0, 1)})
            write_state(state)
            if not chunks:
                print(f"  [跳过-无文本] {rel}")
                state["skipped"].append(rel)
                continue
            extracted.append((rel, full, md5, meta, chunks))
    return extracted


def _rows_from_embedding(emb: list, rel: str, md5: str, meta: dict) -> list[dict]:
    return [{**e, "file": rel, "category": meta["category"], "model_no": meta["model_no"],
             "c_id": meta["c_id"], "version": meta["version"],
             "title": meta.get("title", ""), "md5": md5} for e in emb]


def _index_phase(db, table, extracted: list, state: dict, t0: float, n_batches: list):
    """阶段二:并发 embedding,主线程按序写库。返回 (table, 写入块数)。"""
    total = len(extracted)
    state.update({"phase": "indexing", "done": 0, "embed": {"done": 0, "total": total}})
    n_chunks = 0
    with ThreadPoolExecutor(config.get("embed_workers")) as ex:
        futures = {ex.submit(embed_file, rel, chunks, n_batches): (rel, full, md5, meta, chunks)
                   for rel, full, md5, meta, chunks in extracted}
        for i, fut in enumerate(as_completed(futures), 1):
            rel, full, md5, meta, chunks = futures[fut]
            state.update({"embed": {"done": i - 1, "total": total},
                          "current": rel, "elapsed": round(time.time() - t0, 1)})
            write_state(state)
            try:
                emb = fut.result()
            except Exception as e:
                print(f"  [失败] {rel}: {e}")
                state["errors"].append(f"{rel}: {e}")
                write_state(state)
                continue
            if not emb:
                continue
            rows = _rows_from_embedding(emb, rel, md5, meta)
            try:
                if table is None:
                    db.create_table("chunks", data=rows, schema=schema(len(emb[0]["vector"])))
                    table = db.open_table("chunks")
                else:
                    table.delete(f"file = '{esc_file(rel)}'")
                    table.add(rows)
            except Exception as e:
                print(f"  [失败] {rel}: {e}")
                state["errors"].append(f"{rel}: {e}")
                write_state(state)
                continue
            n_chunks += len(rows)
            print(f"  [{i}/{total}] {rel} ({len(rows)} 块)")
            state.update({"embed": {"done": i, "total": total}, "chunks": n_chunks,
                          "elapsed": round(time.time() - t0, 1)})
            write_state(state)
    return table, n_chunks


def _append_history(added: int, removed: int, n_chunks: int, elapsed: float, skipped: list):
    history = {"time": datetime.now().isoformat(timespec="seconds"), "added": added,
               "removed": removed, "chunks": n_chunks, "elapsed": elapsed, "skipped": skipped}
    try:
        hist = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, encoding="utf-8") as f:
                hist = json.load(f)
        hist.append(history)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist[-100:], f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def _run(args):
    root = config.PDF_ROOT
    if not os.path.isdir(root):
        sys.exit(f"PDF_ROOT 不存在: {root}")

    db = lancedb.connect(config.DB_PATH)
    table, known = None, {}
    if db.list_tables() and not args.rebuild:
        table = db.open_table("chunks")
        pairs = table.to_arrow().select(["file", "md5"]).to_pylist()
        known = {r["file"]: r["md5"] for r in pairs}

    files = {rel: full for full, rel in iter_pdfs(root)}
    if args.rebuild:
        db.drop_table("chunks", ignore_missing=True)
    to_index, removed = _plan_work(files, known, args)

    total = len(to_index)
    state = {
        "phase": "extracting", "total_files": total,
        "extract": {"done": 0, "total": total}, "embed": {"done": 0, "total": 0},
        "chunks": 0, "elapsed": 0.0, "current": "", "errors": [], "skipped": [],
    }
    if not to_index and not removed:
        print(f"无需更新 ({len(files)} 个 PDF)")
        write_state({**state, "phase": "done", "current": "无需更新"})
        return

    t0, n_batches = time.time(), [0]
    extracted = _extract_phase(to_index, root, state, t0)
    table, n_chunks = _index_phase(db, table, extracted, state, t0, n_batches)

    if removed and table is not None:
        for rel in removed:
            table.delete(f"file = '{esc_file(rel)}'")
        print(f"  [移除] {len(removed)} 个已删除的文件")
    if table is not None:
        table.create_fts_index("text", replace=True)

    elapsed = round(time.time() - t0, 1)
    print(f"完成: 处理 {len(to_index)} 个文件 / {n_chunks} 块,移除 {len(removed)} 个,"
          f"耗时 {elapsed:.1f}s,embedding 请求 {n_batches[0]} 批")
    _append_history(len(to_index), len(removed), n_chunks, elapsed, state["skipped"])
    write_state({**state, "phase": "done", "done": total, "elapsed": elapsed,
                 "current": "", "finished_at": datetime.now().isoformat(timespec="seconds")})

if __name__ == "__main__":
    main()
