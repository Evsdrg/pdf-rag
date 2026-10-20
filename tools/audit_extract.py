# -*- coding: utf-8 -*-
"""PDF 转文字质量审计。

分两部分:
 A. 全量扫索引里的提取异常模式(下标丢失、乱码、表格错列等)
 B. 抽样重开 PDF,逐页核对"页文本 vs 是否进了索引" —— 找整页丢失/低文本页
"""
import collections, json, os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent   # 仓库根目录
sys.path.insert(0, str(ROOT))
import fitz
import lancedb
from backend import config

t = lancedb.connect(config.DB_PATH).open_table("chunks")
rows = t.to_arrow().select(["file", "page", "text"]).to_pylist()
by_file = collections.defaultdict(list)
for r in rows:
    by_file[r["file"]].append(r)

print("=" * 100)
print("A. 索引文本里的提取异常模式(全 193 份)")
print("=" * 100)

PATTERNS = [
    ("下标丢失(字母/数字后跟孤立下划线)", re.compile(r"[A-Za-z0-9]_+(?=[\s,，、)）]|$)")),
    ("孤立下划线 token", re.compile(r"(?:^|\s)_(?:\s|$)")),
    ("替换字符 U+FFFD", re.compile("\ufffd")),
    ("表格错列(单行含 3+ 个制表分隔空单元)", re.compile(r"\|\s*\|\s*\|\s*\|")),
    ("连续空白异常(>=4 空格且非缩进)", re.compile(r"[^\s] {4,}[^\s]")),
]
tot_chunks = len(rows)
for label, rx in PATTERNS:
    n = sum(1 for r in rows if rx.search(r["text"]))
    print(f"  {label:<40} {n:>5} / {tot_chunks} 块 = {n/tot_chunks*100:5.1f}%")

# 二进制/十六进制串(寄存器表常出现, 属正常; 但占比过高说明表格被误读成数据)
HEX = re.compile(r"\b[01]{8,}\b")
n = sum(1 for r in rows if HEX.search(r["text"]))
print(f"  {'长二进制串(>=8 位)':<40} {n:>5} / {tot_chunks} 块 = {n/tot_chunks*100:5.1f}%")

# 每份文档的平均文本密度
print()
dens = []
for f, rs in by_file.items():
    pages = len({r["page"] for r in rs})
    chars = sum(len(r["text"]) for r in rs)
    dens.append((chars / max(1, pages), f, pages, chars))
dens.sort()
print(f"  文本密度最低的 8 份(字符/页):")
for d, f, p, c in dens[:8]:
    print(f"    {d:7.0f} 字符/页  {p:>4} 页  {c:>7} 字符  {f.split(chr(92))[-1][:52]}")

print()
print("=" * 100)
print("B. 抽样重开 PDF:页文本 vs 是否入索引(找整页丢失)")
print("=" * 100)

# 按类别分层抽样,每类最多 2 份,优先取密度最低的(最可能有问题)
picked, per_cat = [], collections.Counter()
for d, f, p, c in dens:
    cat = f.split(os.sep)[0] if os.sep in f else ""
    if per_cat[cat] >= 2:
        continue
    per_cat[cat] += 1
    picked.append(f)
# 再补几份密度最高的作对照
for d, f, p, c in dens[-6:]:
    if f not in picked:
        picked.append(f)
print(f"抽样 {len(picked)} 份\n")

print(f"{'文件':<40} {'总页':>5} {'入索引页':>8} {'丢失页':>7} {'低文本页':>9} {'均字符/页':>10}")
print("-" * 100)
tot_pages = tot_indexed = tot_missing = tot_thin = 0
worst = []
for f in picked:
    full = os.path.join(config.PDF_ROOT, f)
    if not os.path.isfile(full):
        continue
    try:
        doc = fitz.open(full)
    except Exception as e:
        print(f"  [打开失败] {f}: {e}")
        continue
    n = len(doc)
    lens = [len(doc[i].get_text("text").strip()) for i in range(n)]
    doc.close()
    indexed_pages = {r["page"] + 1 for r in by_file[f]}
    missing = [i + 1 for i in range(n) if (i + 1) not in indexed_pages]
    thin = [i for i in range(n) if lens[i] < 200]
    avg = sum(lens) / max(1, n)
    tot_pages += n; tot_indexed += len(indexed_pages)
    tot_missing += len(missing); tot_thin += len(thin)
    print(f"{f.split(chr(92))[-1][:38]:<40} {n:>5} {len(indexed_pages):>8} {len(missing):>7} "
          f"{len(thin):>9} {avg:>10.0f}")
    if missing or len(thin) > n * 0.3:
        worst.append((f, n, missing, thin, lens))

print("-" * 100)
print(f"{'合计':<40} {tot_pages:>5} {tot_indexed:>8} {tot_missing:>7} {tot_thin:>9}")
print(f"\n  页级覆盖: {tot_indexed}/{tot_pages} = {tot_indexed/tot_pages*100:.1f}%")
print(f"  整页丢失: {tot_missing} 页 ({tot_missing/tot_pages*100:.1f}%)")
print(f"  低文本页(<200字符, 走 OCR 兜底): {tot_thin} 页 ({tot_thin/tot_pages*100:.1f}%)")

print("\n=== 有问题的文档明细 ===")
for f, n, missing, thin, lens in worst[:10]:
    print(f"\n  {f}")
    print(f"    共 {n} 页; 丢失页 {missing[:12]}{'...' if len(missing)>12 else ''}")
    print(f"    低文本页 {[i+1 for i in thin][:12]}")
    print(f"    各页字符数(前20): {lens[:20]}")
