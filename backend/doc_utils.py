"""PDF 页面文本提取、表格 markdown 化、共享读页逻辑。

除 PDF 外也处理 Markdown(.md):按一级标题切成"伪页",与 PDF 的页概念对齐,
使搜索/读页/书签三处接口对两种格式行为一致。
"""
import os
import re
from pathlib import Path

from . import config


def resolve_under(root: str, rel: str) -> str:
    """把客户端传入的相对路径解析到 root 之下,越界抛 FileNotFoundError。

    /api/pdf、/api/page 与 MCP 读页的 file 参数直接来自客户端。os.path.join
    遇到绝对路径会**丢弃前半段**("file=/etc/passwd" 直接读系统文件),带 ../
    则穿出语料库 —— 不设防时这些等价于任意文件读。反斜杠先归一为正斜杠:
    Linux 把 `..\\..\\x` 当普通文件名放行,而它在 Windows 语义下是穿越,
    归一后两种平台都按穿越拦截(fail-closed;本语料没有含反斜杠的文件名)。
    """
    rel = rel.replace("\\", "/")
    root_real = os.path.realpath(root)
    full = os.path.realpath(os.path.join(root_real, rel))
    if full != root_real and not full.startswith(root_real + os.sep):
        raise FileNotFoundError(f"路径越界: {rel}")
    return full

# ---------- Markdown ----------

MD_SUFFIXES = (".md", ".markdown")


def is_markdown(path: str) -> bool:
    return path.lower().endswith(MD_SUFFIXES)


_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_MD_COLOR_RE = re.compile(r"\$\\color\{#[0-9A-Fa-f]{3,8}\}\{([^}]*)\}\$")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def clean_md(text: str) -> str:
    """Markdown → 适合嵌入的纯文本。

    去掉图片引用(对文本检索是噪声)、还原 LaTeX 着色标记、把链接/加粗/行内代码
    降为纯文本;表格(markdown 语法)与标题原样保留 —— 表格结构对检索有价值。
    """
    text = _MD_IMG_RE.sub("", text)
    text = _MD_COLOR_RE.sub(r"\1", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_md_pages(text: str) -> list[str]:
    """按一级标题(`# `)把 Markdown 切成伪页,与 PDF 的页概念对齐。

    第一个一级标题之前的引言归入第 1 页;没有一级标题则整篇算一页。
    """
    pages: list[str] = []
    cur: list[str] = []
    for ln in text.split("\n"):
        if ln.startswith("# ") and any(s.strip() for s in cur):
            pages.append("\n".join(cur).strip())
            cur = [ln]
        else:
            cur.append(ln)
    if any(s.strip() for s in cur):
        pages.append("\n".join(cur).strip())
    return pages or [text.strip()]


def md_pages(path: str) -> list[str]:
    """读取 Markdown 并切分为伪页(每项为一页文本)。"""
    raw = Path(path).read_text(encoding="utf-8", errors="ignore")
    return split_md_pages(clean_md(raw))


def read_md_page(path: str, page: int) -> tuple[str, str]:
    """读 Markdown 伪页(1-based)。返回 (文本, 错误信息)。"""
    pages = md_pages(path)
    if page < 1 or page > len(pages):
        return "", f"页码越界: {page} (共 {len(pages)} 页)"
    return pages[page - 1], ""


def md_outline(path: str) -> list[dict]:
    """取 Markdown 标题结构(章节 + 页码),对齐 PDF 的 get_toc()。"""
    out = []
    for i, page in enumerate(md_pages(path), 1):
        for ln in page.split("\n"):
            m = re.match(r"^(#{1,6})\s+(.*)$", ln)
            if m:
                out.append({"level": len(m.group(1)), "title": m.group(2).strip(),
                            "page": i})
    return out


# "…系列" 之前的部分即产品/系列名: "Lierda LTE Standard(L) 系列 …" → "Lierda LTE Standard(L)"
# "FS8025B系列USB的PD…" → "FS8025B"。只用于展示,不写索引。
_SERIES_RE = re.compile(r"^(.*?)\s*系列")


def product_label(name_or_path: str) -> str:
    """从文件名派生产品/系列名,供展示用。

    为什么不在入库时填进 model_no:model_no 参与检索的跨版本文档去重
    (retrieval._same_document 要求型号完全一致才合并)。给同系列的多个不同
    主题文档填同一个系列名,会让它们因正文相似而被误判为同一文档、静默合并
    (实测 41 份 Lierda 文档会产生 296 对误合并)。故此处只在展示层派生。
    """
    stem = Path(name_or_path).stem
    m = _SERIES_RE.match(stem)
    label = m.group(1).strip() if m else ""
    # 兜底:文件以 "品牌_型号_…" 下划线命名且首段像型号时取首段
    if not label:
        head = stem.split("_")[0].strip()
        if head and head.isascii() and any(c.isdigit() for c in head):
            label = head
    return label


def version_key(v: str) -> tuple:
    """版本字符串 → 可比较的 tuple(数字优先,字母转序)。

    放在这里供 ingest(写索引)与 retrieval(多版本去重)共用 ——
    历史上两处各写了一份,容易出现行为漂移。
    """
    if not v:
        return (0,)
    if v[0].isdigit():
        return (1,) + tuple(int(x) for x in re.findall(r"\d+", v))
    return (2, ord(v[0]))


def title_key(title: str) -> str:
    """文档标题指纹:去掉版本号/页码等差异,用于识别同文档多版本"""
    t = re.sub(r"[Vv]\d+(\.\d+)*", "", title)
    t = re.sub(r"Rev\.?\s*[A-Za-z]+", "", t)
    t = re.sub(r"\s*\d+\s*$", "", t)
    t = re.sub(r"\s+", "", t)
    return t[:60]


def title_sim(a: str, b: str) -> float:
    """标题相似度(字符 bigram Jaccard),用于识别首页格式不同的同文档多版本"""
    def grams(s: str) -> set:
        s = re.sub(r"\s+", "", s).lower()
        return {s[i:i + 2] for i in range(len(s) - 1)}
    x, y = grams(a), grams(b)
    if not x or not y:
        return 0.0
    return len(x & y) / len(x | y)


def block_sim(a: str, b: str) -> float:
    """块文本相似度(截断 1500 字符的 bigram Jaccard),用于判断两个文件是否同一文档"""
    def grams(s: str) -> set:
        s = re.sub(r"\s+", "", s).lower()[:1500]
        return {s[i:i + 2] for i in range(len(s) - 1)}
    x, y = grams(a), grams(b)
    if not x or not y:
        return 0.0
    return len(x & y) / len(x | y)


def clean_cell(c) -> str:
    if c is None:
        return ""
    return " ".join(str(c).split())


def table_to_md(rows) -> str:
    """find_tables 的单元格矩阵 → markdown 表格文本。垃圾表(内容率过低)返回空串。

    合并单元格会在矩阵里展开成幽灵空列(某几行有值、其余行全空),不处理就会产生
    大量 "| a |  |  | b |" 的错列文本 —— 实测这类模式占索引块的 18.5%,既污染
    正文也浪费嵌入。这里按列的有效填充率丢弃稀疏列。
    """
    if not rows:
        return ""
    rows = [[clean_cell(c) for c in row] for row in rows]
    rows = [r for r in rows if any(c for c in r)]
    if not rows:
        return ""
    ncols = max(len(r) for r in rows)
    norm = [r + [""] * (ncols - len(r)) for r in rows]
    # 有效内容率过低 → 视为误检的垃圾表(基于原始矩阵,避免压缩后虚高)
    raw_total = len(norm) * ncols
    raw_filled = sum(1 for r in norm for c in r if c)
    ratio = raw_filled / raw_total
    min_ratio = config.get("table_min_ratio")
    if ratio < min_ratio or (len(norm) <= 4 and ratio < min_ratio * 3):
        return ""
    nrows = len(norm)
    # 只丢弃"全空列"(合并单元格展开产生的冗余列)。
    # 曾尝试进一步丢弃"稀疏列"(填充率<20%),实测错列数几乎不降(17→16、56→56),
    # 却把变体对比表的真实数据砍掉(IP2111A 那份 11033→7098 字符),故不做。
    keep_cols = [ci for ci in range(ncols) if any(norm[ri][ci] for ri in range(nrows))]
    if not keep_cols:
        return ""
    norm = [[r[ci] for ci in keep_cols] for r in norm]
    # 丢掉压缩后与前一列完全重复的列(合并单元格被拆成多列的另一种表现;
    # 仅当该列在所有非空处都与前一列相同时才算重复,不会误伤真实重复数据)
    dedup = [0]
    for ci in range(1, len(norm[0])):
        if any(norm[ri][ci] and norm[ri][ci] != norm[ri][dedup[-1]] for ri in range(nrows)):
            dedup.append(ci)
    norm = [[r[ci] for ci in dedup] for r in norm]
    if not norm[0] or not any(norm[0]):
        return ""

    def fmt(r):
        return "| " + " | ".join(r) + " |"

    out = [fmt(norm[0]), "|" + "---|" * len(norm[0])]
    out += [fmt(r) for r in norm[1:]]
    return "\n".join(out)


def page_text_with_tables(page, max_chars: int = 0) -> str:
    """页面文本 + 检测到的表格(markdown 格式)。无表格时只返回文本。"""
    text = page.get_text("text").strip()
    try:
        tables = page.find_tables().tables
        if tables:
            for i, t in enumerate(tables, 1):
                md = table_to_md(t.extract())
                if md:
                    text += f"\n\n[表格{i}]\n{md}"
    except Exception:
        pass
    if max_chars and len(text) > max_chars:
        text = text[:max_chars]
    return text

# 低文本页判定阈值:低于此值认为文本层不可用,尝试 OCR 兜底
THIN_PAGE_CHARS = 200


def read_page_text(doc, page_number: int) -> tuple[str, str]:
    """读取一页的完整文本(含表格 markdown),低文本页自动回退 OCR。

    返回 (文本, 错误信息);正常时错误为空。main.py 与 server.py 共用,
    避免两处阈值/DPI/超时参数各写一份导致行为漂移。
    """
    import os
    import tempfile

    page = doc[page_number - 1]
    text = page.get_text("text").strip()
    if len(text) >= THIN_PAGE_CHARS:
        return page_text_with_tables(page, max_chars=config.get("page_max_chars")), ""
    try:
        from . import ocr as ocr_mod
        workdir = tempfile.mkdtemp(prefix="pdfrag_page_")
        img = os.path.join(workdir, "page.png")
        page.get_pixmap(dpi=config.get("ocr_dpi")).save(img)
        ocr, err = ocr_mod.ocr_image(img)
        if err:
            raise RuntimeError(err)
        if len(ocr) < len(text):
            return page_text_with_tables(page, max_chars=config.get("page_max_chars")), ""
        return ocr or "OCR 无结果", ""
    except Exception as e:
        return "该页为低文本页且 OCR 服务不可用", f"{type(e).__name__}: {e}"
