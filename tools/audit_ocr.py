# -*- coding: utf-8 -*-
"""量化 OCR 兜底失败:区分「图片型 PDF 被 OCR 救回」与「OCR 失败留下空壳」"""
import collections, os, pathlib, sys

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

results = []
for f, rs in by_file.items():
    full = os.path.join(config.PDF_ROOT, f)
    if not os.path.isfile(full):
        continue
    try:
        doc = fitz.open(full)
        pages = len(doc)
        raw = [len(doc[i].get_text("text").strip()) for i in range(pages)]
        doc.close()
    except Exception:
        continue
    pdf_chars = sum(raw)
    idx_chars = sum(len(r["text"]) for r in rs)
    thin_pages = sum(1 for x in raw if x < 200)
    results.append({
        "file": f, "pages": pages, "pdf_chars": pdf_chars, "idx_chars": idx_chars,
        "thin": thin_pages, "thin_ratio": thin_pages / max(1, pages),
        "pdf_per_page": pdf_chars / max(1, pages),
        "idx_per_page": idx_chars / max(1, pages),
    })

# 分类
image_pdf = [r for r in results if r["pdf_per_page"] < 200]          # 图片型, 必须靠 OCR
rescued   = [r for r in image_pdf if r["idx_per_page"] >= 200]       # OCR 救回
shell     = [r for r in image_pdf if r["idx_per_page"] < 200]        # OCR 没救回 → 空壳
print(f"文档总数(含索引): {len(results)}")
print(f"图片型 PDF(原始文本 <200 字符/页): {len(image_pdf)}")
print(f"  其中 OCR 成功救回(索引 >=200 字符/页): {len(rescued)}")
print(f"  其中 OCR 失败 → 空壳(索引仍 <200 字符/页): {len(shell)}")
print()

print("=== 空壳文档明细(这些在库里基本不可检索) ===")
print(f"{'页数':>5} {'PDF字符/页':>11} {'索引字符/页':>12}  文件")
for r in sorted(shell, key=lambda x: x["idx_per_page"]):
    print(f"{r['pages']:>5} {r['pdf_per_page']:>11.0f} {r['idx_per_page']:>12.0f}  "
          f"{r['file'].split(chr(92))[-1][:58]}")
print()

print("=== OCR 救回的样例(说明兜底机制确实在工作) ===")
for r in sorted(rescued, key=lambda x: -x["idx_per_page"])[:6]:
    print(f"  PDF {r['pdf_per_page']:>6.0f} -> 索引 {r['idx_per_page']:>6.0f} 字符/页  "
          f"{r['file'].split(chr(92))[-1][:54]}")
print()

print("=== 部分低文本页的文档(混合型, 这些页内容若丢失则不可检索) ===")
mixed = [r for r in results if 0.2 < r["thin_ratio"] < 1.0 and r["pdf_per_page"] >= 200]
print(f"共 {len(mixed)} 份; 列出低文本页占比最高的 10 份:")
for r in sorted(mixed, key=lambda x: -x["thin_ratio"])[:10]:
    print(f"  低文本页 {r['thin']:>3}/{r['pages']:<3} ({r['thin_ratio']*100:>3.0f}%)  "
          f"索引 {r['idx_per_page']:>6.0f} 字符/页  {r['file'].split(chr(92))[-1][:50]}")

# 全局: 索引文本量 vs PDF 原始文本量
tp = sum(r["pdf_chars"] for r in results)
ti = sum(r["idx_chars"] for r in results)
print(f"\n全库: PDF 原始文本 {tp/1e6:.2f} M 字符 -> 索引 {ti/1e6:.2f} M 字符 "
      f"(比值 {ti/max(1,tp):.2f}; >1 说明 OCR 补充了内容)")
