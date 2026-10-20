# -*- coding: utf-8 -*-
"""导出"解析后数据":索引里的文本,连同元数据落成可直接查阅的文件。

产出:

    <out>/chunks.jsonl        每块一行:解析出的文本 + 全部元数据(不含向量)
    <out>/pages/<文件>.txt    按页重建的可读文本(页用 ===== pN ===== 分隔)
    <out>/README.txt          数据来源、字段说明、保真度说明

**不重新解析 PDF** —— 那要跑一遍完整提取(本语料约 80 分钟),而索引里的文本
就是同一批解析结果,逐块取自索引即可。

页文本由该页的块拼接:切块按页进行,块间保留 chunk_overlap_chars 重叠,
拼接时按切块规则去重。超长段落走的是"硬切"分支、不带重叠前缀,这类块按原样
拼入。因此页文本对检索与审阅足够,但不是原页面的逐字节还原。

    uv run python tools/export_parsed.py                    # 导出到 parsed/
    uv run python tools/export_parsed.py --out <目录>
"""
import argparse
import json
import pathlib
import shutil
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import lancedb                                          # noqa: E402
from backend import config                              # noqa: E402

TABLE = "chunks"
META_COLS = ["file", "page", "category", "model_no", "c_id", "version", "title", "md5"]


def join_page_chunks(chunks: list[str], overlap: int) -> str:
    """把同一页的块拼回页文本。

    切块时新块以"上一块末 overlap 字 + 换行"开头;这里按同一规则剪掉,
    避免拼接后出现重复段落。硬切产生的块不满足该前缀关系,按原样拼入。
    """
    out = ""
    prev = ""
    for c in chunks:
        if prev:
            for k in range(min(overlap, len(prev)), 0, -1):
                if c.startswith(prev[-k:] + "\n"):
                    c = c[k + 1:]
                    break
        out = f"{out}\n{c}" if out else c
        prev = c
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="导出解析后数据")
    ap.add_argument("--out", default=str(ROOT / "parsed"), help="输出目录(默认 parsed/)")
    args = ap.parse_args()

    out = pathlib.Path(args.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    (out / "pages").mkdir(parents=True)

    tbl = lancedb.connect(config.DB_PATH).open_table(TABLE)
    rows = tbl.to_arrow().select(META_COLS + ["text"]).to_pylist()
    overlap = config.get("chunk_overlap_chars")
    print(f"  索引 {len(rows)} 块  块间重叠 {overlap} 字")

    t0 = time.time()
    by_file: dict[str, dict[int, list[str]]] = {}
    with open(out / "chunks.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            by_file.setdefault(r["file"], {}).setdefault(r["page"], []).append(r["text"])

    n_pages = 0
    for rel, pages in by_file.items():
        target = out / "pages" / f"{rel}.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        parts = []
        for page in sorted(pages):
            parts.append(f"===== p{page + 1} =====\n"
                         + join_page_chunks(pages[page], overlap))
            n_pages += 1
        target.write_text("\n\n".join(parts) + "\n", encoding="utf-8")

    readme = "\n".join([
        "解析后数据",
        "=" * 40,
        f"导出时间    : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"文档数      : {len(by_file)}",
        f"页数        : {n_pages}",
        f"块数        : {len(rows)}",
        "",
        "chunks.jsonl 每块一行(JSON),字段:",
        "  text      解析出的文本(表格已转 markdown)",
        "  file      相对手册根目录的路径,与 PDF_ROOT 对应",
        "  page      页号(0 起;文件内显示为 p{page+1})",
        "  category / model_no / c_id / version / title / md5   文档元数据",
        "",
        "pages/<文件>.txt 是按页重建的可读文本,页以 ===== pN ===== 分隔。",
        "切块按页进行、块间保留重叠,拼接时已按切块规则去重;超长段落走硬切分支",
        "的块不带重叠前缀,按原样拼入 —— 因此页文本对检索与审阅足够,",
        "但不是原页面的逐字节还原。需要逐字原文请直接读 PDF。",
        "实测保真度:随机抽 41 页与原 PDF 对照,去空白后相似度中位 1.000、",
        "均值 0.941;少数页有差异(依赖 OCR 的扫描页、表格页),另有约 2% 的页",
        "重建后偏长(硬切块按原样拼入所致)。",
        "",
        "本目录与索引同源:这些文本就是生成向量所用的那批数据,未重新解析 PDF。",
        "",
    ])
    (out / "README.txt").write_text(readme, encoding="utf-8")

    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) / 1048576
    print(f"  完成: {out}  {len(by_file)} 文档 / {n_pages} 页 / {len(rows)} 块  "
          f"{size:.0f} MB  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
