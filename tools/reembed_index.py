# -*- coding: utf-8 -*-
"""用当前配置的嵌入模型重算已有索引的向量,写出一个新索引库。

用途:对比不同嵌入模型。**文本提取与切块跟嵌入模型无关**,所以不必重新解析
PDF —— 本语料的提取阶段约 80 分钟,这里直接复用现有索引里的文本,只重算向量,
切块与原库逐条一致,比较的就是纯粹的嵌入模型差异。

    # 用 embed-v5.0-pro 重算一份影子索引(不动现有索引)
    DB_PATH=dist/v5.lance EMBED_MODEL=embed-v5.0-pro \\
    EMBED_INPUT_TYPE_DOC=search_document \\
    uv run python tools/reembed_index.py --src index.lance

对比评测时,查询侧要用配套的 input_type:

    DB_PATH=dist/v5.lance EMBED_MODEL=embed-v5.0-pro \\
    EMBED_INPUT_TYPE_QUERY=search_query uv run python eval_retrieval.py
"""
import argparse
import os
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import lancedb                                            # noqa: E402
from backend import config, ingest                        # noqa: E402

TEXT_COLS = ["text", "file", "page", "category", "model_no", "c_id", "version",
             "title", "md5"]
TABLE = "chunks"


def read_source(src: pathlib.Path) -> tuple[list[dict], int]:
    t = lancedb.connect(str(src)).open_table(TABLE)
    rows = t.to_arrow().select(TEXT_COLS).to_pylist()
    old_dim = t.schema.field("vector").type.list_size
    print(f"  源索引: {src}  {len(rows)} 块  原维度 {old_dim}")
    return rows, old_dim


def embed_all(rows: list[dict], batch: int) -> list[list[float]]:
    """并发嵌入,按原顺序返回向量。"""
    texts = [r["text"] for r in rows]
    batches = [(i, texts[i:i + batch]) for i in range(0, len(texts), batch)]
    out: list[list[float] | None] = [None] * len(texts)
    client = ingest._new_client()
    done = 0
    t0 = time.time()

    def work(item):
        start, chunk = item
        return start, ingest.embed_batch(client, chunk)

    with ThreadPoolExecutor(config.get("embed_workers")) as ex:
        for start, vecs in ex.map(work, batches):
            for k, v in enumerate(vecs):
                out[start + k] = v
            done += len(vecs)
            print(f"\r  嵌入 {done}/{len(texts)}  {time.time() - t0:.0f}s",
                  end="", flush=True)
    client.close()
    print()
    if any(v is None for v in out):
        raise RuntimeError("有批次未返回向量")
    return out          # type: ignore[return-value]


def main() -> None:
    ap = argparse.ArgumentParser(description="重算索引向量(用于对比嵌入模型)")
    ap.add_argument("--src", default="index.lance", help="源索引(默认 index.lance)")
    ap.add_argument("--batch", type=int, default=None, help="每批条数(默认取配置)")
    args = ap.parse_args()

    src = (ROOT / args.src).resolve()
    dst = pathlib.Path(config.DB_PATH).resolve()
    if src == dst:
        raise SystemExit(f"源与目标相同({src}),会把原索引覆盖掉 —— 换 DB_PATH")
    model = config.get("embed_model")
    itype = config.get("embed_input_type_doc")
    print(f"  源: {src}")
    print(f"目标: {dst}")
    print(f"模型: {model}   input_type(doc): {itype or '(不发送)'}")

    rows, old_dim = read_source(src)
    vecs = embed_all(rows, args.batch or config.get("embed_batch"))
    dim = len(vecs[0])
    print(f"  向量维度: {old_dim} -> {dim}")

    if dst.exists():
        print(f"  目标已存在,先删除")
        import shutil
        shutil.rmtree(dst)
    db = lancedb.connect(str(dst))
    payload = [{**r, "vector": v} for r, v in zip(rows, vecs)]
    db.create_table(TABLE, data=payload, schema=ingest.schema(dim))
    tbl = db.open_table(TABLE)
    # 全文索引必须一并建:检索是三路(向量 + 全文 + 子串)融合,缺了全文通道
    # 对比就不是同一个系统了
    tbl.create_fts_index("text", replace=True)
    n = tbl.count_rows()
    size_mb = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file()) / 1048576
    print(f"\n完成: {dst}  {n} 块 (含 FTS 索引)  {size_mb:.0f} MB")


if __name__ == "__main__":
    main()
