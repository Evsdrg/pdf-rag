"""结构化检索冷热逻辑基准:FTS/无网络,可选确定性重排替身,不改持久设置。"""
import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend import config, entity, library, retrieval
from tools.eval_relations import block_network, load_dataset, quarantined_questions


def signature(value):
    if isinstance(value, dict):
        return {key: signature(item) for key, item in value.items()
                if key not in ("index_build_ms", "index_cached", "cached")}
    if isinstance(value, (list, tuple)):
        return [signature(item) for item in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(signature(value), ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def distribution(values):
    ordered = sorted(values)
    return {"median_ms": statistics.median(ordered), "p95_ms": ordered[min(len(ordered)-1, int(.95*len(ordered)))],
            "n": len(ordered)}


def measure(table, queries, rounds, *, rerank_stub=False):
    times, snapshots, rerank_inputs = [], {}, {}
    original = retrieval._call_reranker
    current = ""

    def fake_rerank(query, documents):
        rerank_inputs[current] = digest(documents)
        return [1.0/(index+1) for index in range(len(documents))]

    if rerank_stub:
        retrieval._call_reranker = fake_rerank
    try:
        for repeat in range(rounds):
            for qid, query in queries if repeat % 2 == 0 else reversed(queries):
                for enabled in (False, True) if repeat % 2 == 0 else (True, False):
                    current = f"{qid}:{enabled}"
                    diagnostics = {}
                    start = time.perf_counter()
                    results = retrieval.search(table, query, mode="fts", rerank=rerank_stub,
                                               structured=enabled, diagnostics=diagnostics)
                    elapsed = (time.perf_counter()-start)*1000
                    if diagnostics.get("degraded"):
                        raise RuntimeError(f"基准出现降级: {qid} {diagnostics['degraded']}")
                    value = digest([results, diagnostics])
                    if current in snapshots and snapshots[current] != value:
                        raise RuntimeError(f"基准结果不确定: {current}")
                    snapshots[current] = value
                    times.append({"id": qid, "repeat": repeat, "structured": enabled, "ms": elapsed})
    finally:
        retrieval._call_reranker = original
    return times, snapshots, rerank_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--rerank-stub", action="store_true", help="用本地确定性分数走完整重排路径,不评价模型质量")
    parser.add_argument("--whole-chunk-rerank", action="store_true", help="只用于替身对照,关闭窗口重排")
    args = parser.parse_args()
    if args.rounds < 2:
        parser.error("至少两轮,不能用单轮波动证明性能收益")
    if args.whole_chunk_rerank and not args.rerank_stub:
        parser.error("整块重排对照必须显式启用本地替身")
    block_network()
    config.override_local({"query_cache_ttl": 0})
    if args.whole_chunk_rerank:
        config.override_local({"rerank_on_window": False})
    table = library.get_table()
    if table is None:
        parser.error("本地索引不存在;工具不会自动构建")
    data = load_dataset()
    skip = set(quarantined_questions(data))
    relations = [(q["id"], q["query"]) for q in data["questions"] if q["id"] not in skip]
    legacy = [(f"L{index:02}", q["query"]) for index, q in enumerate(json.loads((ROOT/"eval_queries.json").read_text()))]
    cold = []
    for _ in range(3):
        entity.reset_cache()
        start = time.perf_counter()
        index = entity.get_index(table)
        cold.append((time.perf_counter()-start)*1000)
    # 首次缓存构建不混进热态,但整个结果缓存保持关闭。
    for enabled in (False, True):
        retrieval.search(table, relations[0][1], mode="fts", rerank=False, structured=enabled)
    times, snapshots, inputs = measure(table, relations + legacy, args.rounds, rerank_stub=args.rerank_stub)
    summary = {"cold_index": distribution(cold), "rerank": "local_stub" if args.rerank_stub else "off",
               "rerank_on_window": config.get("rerank_on_window"),
               "index": {"version": int(table.version), "rows": len(index.entities_by_uid),
                         "entities": len(index.by_entity), "links": sum(len(keys) for keys in index.entities_by_uid.values())}}
    for group, ids in (("relations", {qid for qid, _ in relations}), ("legacy", {qid for qid, _ in legacy})):
        for enabled in (False, True):
            values = [row["ms"] for row in times if row["id"] in ids and row["structured"] == enabled]
            summary[f"{group}:{enabled}"] = distribution(values)
    paths = ("backend/retrieval.py", "backend/evidence.py", "backend/query_lex.py", "backend/entity.py")
    result = {"summary": summary, "times": times, "snapshots": snapshots, "rerank_inputs": inputs,
              "implementation_sha256": {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in paths},
              "datasets_sha256": {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                                  for path in ("eval_relations.json", "eval_queries.json")},
              "limitations": ["local FTS logic only, not production or network latency",
                              "stub reranking is deterministic input/cost validation, not real model quality",
                              "input and output hashes exclude only timing/cache diagnostics; no handbook text is exported"]}
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=1)+"\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
