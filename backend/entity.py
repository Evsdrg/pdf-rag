"""默认关闭的确定性实体桥:查询时局部扩展,原始 chunk 始终是证据。"""
from __future__ import annotations

import math
import os
import pickle
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path

MAX_QUERY_ENTITIES = 16
MAX_ROW_ENTITIES = 48
MAX_DIRECT_CANDIDATES = 64
MAX_EXPANDED_CANDIDATES = 32
MAX_SEEDS = 8
MAX_SEED_INPUTS = 256
MAX_POSTING = 256
MAX_QUERY_CANDIDATES = 4096
MAX_NEIGHBORS = 64
# 索引本体实测约 1.3KB/块(8561 块 = 11MB,不含构建期 Arrow 临时量),20 万行约 260MB。
# 旧值 5 万行在 660 个同规模手册就会撞墙,与"1000+ 手册"的目标不符。
MAX_INDEX_ROWS = 200_000
MAX_INDEX_BYTES = 512_000_000
MAX_INDEX_LINKS = 4_000_000

from .query_lex import evidence_slots, extract_entities

_WEIGHTS = {"model": 6, "symbol": 3, "interface": 2, "parameter": 2, "value": 1}
_BROAD_SYMBOLS = {"symbol:" + value for value in ("vdd", "vin", "vout", "vbat", "vcc", "sda", "scl", "cs", "en")}


def _kind(key: str) -> str:
    return key.split(":", 1)[0]


class IndexLimitError(ValueError):
    """实体桥拒绝超过内存预算的主表;不会截断后伪称索引完整。"""


@dataclass(frozen=True, slots=True)
class EntityIndex:
    table_version: int
    by_entity: dict[str, tuple[str, ...]]
    entities_by_uid: dict[str, frozenset[str]]
    metadata_by_uid: dict[str, dict]
    build_ms: float
    page_entities: dict[tuple[str, int], frozenset[str]] = field(default_factory=dict)
    document_frequency: dict[str, int] = field(default_factory=dict)
    file_count: int = 0


@dataclass(frozen=True, slots=True)
class EntitySearch:
    query_entities: tuple[str, ...]
    direct_uids: tuple[str, ...]
    expanded_uids: tuple[str, ...]
    status: str
    index: EntityIndex | None = field(default=None, repr=False, compare=False)
    index_cached: bool = False
    seeds: int = 0
    pruned: int = 0
    by_model: dict[str, int] = field(default_factory=dict)
    paths: dict[str, dict] = field(default_factory=dict, repr=False, compare=False)

    @property
    def ordered_uids(self) -> tuple[str, ...]:
        return self.direct_uids + self.expanded_uids


_CACHE: tuple[object, int, EntityIndex] | None = None
_LIMIT_FAILURE: tuple[object, int, str] | None = None
_LOCK = threading.Lock()

# 持久化快照。构建一次实体索引在真实规模上要数秒到数十秒(8561 块约 2s,
# 25k 块约 7.7s,1000 手册量级约 23s),而同一份快照反序列化只要十几毫秒。
# 文件名绑定表版本:版本不符一律重建,绝不复用可能陈旧的数据。
_CACHE_VERSION = 1


def cache_path() -> Path:
    """快照路径:与 settings.json 同目录(容器内 /app/data,随备份)。"""
    from . import config

    return Path(config.SETTINGS_FILE).parent / "entity_index.pkl"


def _release_heap() -> None:
    """把已释放的堆归还操作系统。

    构建期 Arrow batches 会临时占用大量内存;Python 释放后 glibc 常保留在
    自己的 arena 里。实测 8561 块:归还前 RSS +80MB,归还后 +11MB。
    没有 malloc_trim 的平台静默跳过,不影响正确性。
    """
    try:
        import ctypes

        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


def _table_fingerprint(table) -> str | None:
    """快照归属标识:表版本 + 数据目录;拿不到可靠目录时返回 None(禁用快照)。

    只校验版本号是不够的——`table.version` 是**每张表各自的计数器**,不同数据库
    里的表可以同时处于 version=1。只比版本会让 A 库的快照被 B 库误用,检索结果
    与主表内容脱节。

    反过来,如果拿不到表的数据目录(例如测试里的替身对象),就无法证明快照属于
    这张表;此时宁可不使用快照,也不能冒险复用别人的索引。
    """
    import hashlib

    try:
        uri = getattr(table, "uri", None) or ""
    except Exception:
        uri = ""
    if not uri:
        return None
    raw = f"{uri}\x00{int(table.version)}".encode()
    return hashlib.sha256(raw).hexdigest()[:32]


def _load_snapshot(table) -> EntityIndex | None:
    """读取与当前表(路径+版本)匹配的快照;任何异常都返回 None 走重建。"""
    path = cache_path()
    version = int(table.version)
    fingerprint = _table_fingerprint(table)
    if fingerprint is None:
        return None
    try:
        with path.open("rb") as handle:
            payload = pickle.load(handle)
        if not isinstance(payload, dict) or payload.get("cache_version") != _CACHE_VERSION:
            return None
        if payload.get("table_version") != version:
            return None
        if payload.get("fingerprint") != fingerprint:
            return None
        index = payload.get("index")
        if not isinstance(index, EntityIndex) or index.table_version != version:
            return None
        return index
    except Exception:
        return None


def _save_snapshot(index: EntityIndex, table=None) -> None:
    """原子写入快照。失败只影响下次冷建速度,不影响正确性。"""
    fingerprint = _table_fingerprint(table) if table is not None else None
    if fingerprint is None:
        return                       # 无法证明归属时不写,避免污染其他表的快照
    path = cache_path()
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"cache_version": _CACHE_VERSION, "table_version": index.table_version,
                   "fingerprint": fingerprint, "index": index}
        with tmp.open("wb") as handle:
            pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        # 快照是纯加速手段:磁盘满、只读挂载、权限不足都不能影响检索本身。
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass


def _batches(table):
    return table.search().select(["uid", "file", "page", "category", "model_no", "text"]).limit(
        MAX_INDEX_ROWS + 1
    ).to_batches(batch_size=512)


def build(table) -> EntityIndex:
    start = time.perf_counter()
    version = int(table.version)
    if table.count_rows() > MAX_INDEX_ROWS:
        raise IndexLimitError("实体桥主表行数超过内存预算")
    postings: dict[str, list[str]] = defaultdict(list)
    entities, metadata, canonical = {}, {}, {}
    links, text_bytes = 0, 0
    for batch in _batches(table):
        text_bytes += batch.nbytes
        if text_bytes > MAX_INDEX_BYTES:
            raise IndexLimitError("实体桥主表文本超过内存预算")
        for row in batch.to_pylist():
            uid = row["uid"]
            if not uid or uid in entities:
                raise ValueError("实体桥需要非空且唯一的 chunk uid")
            keys = frozenset(canonical.setdefault(key, key) for key in extract_entities(
                row["text"] or "", model_no=row["model_no"] or ""))
            links += len(keys)
            if len(entities) >= MAX_INDEX_ROWS or links > MAX_INDEX_LINKS:
                raise IndexLimitError("实体桥关系数量超过内存预算")
            entities[uid] = keys
            metadata[uid] = {key: row[key] for key in ("file", "page", "category")}
            for key in keys:
                postings[key].append(uid)
    if int(table.version) != version:
        raise ValueError("实体桥构建期间主表版本变化")
    for uids in postings.values():
        uids.sort(key=lambda uid: (metadata[uid]["file"], metadata[uid]["page"], uid))
    page_sets: dict[tuple, set] = defaultdict(set)
    documents: dict[str, set] = defaultdict(set)
    for uid, keys in entities.items():
        meta = metadata[uid]
        page_sets[(meta["file"], meta["page"])].update(keys)
        for key in keys:
            documents[key].add(meta["file"])
    return EntityIndex(version, {key: tuple(value) for key, value in postings.items()},
                       entities, metadata, (time.perf_counter() - start) * 1000,
                       {page: frozenset(keys) for page, keys in page_sets.items()},
                       {key: len(files) for key, files in documents.items()},
                       len({meta["file"] for meta in metadata.values()}))


def _cached_index(table) -> tuple[EntityIndex, bool]:
    global _CACHE, _LIMIT_FAILURE
    # 一次只保留一份实体索引;同版本首批并发查询共享一次冷建。
    with _LOCK:
        version = int(table.version)
        if _CACHE and _CACHE[0] is table and _CACHE[1] == version:
            return _CACHE[2], True
        if _LIMIT_FAILURE and _LIMIT_FAILURE[0] is table and _LIMIT_FAILURE[1] == version:
            raise IndexLimitError(_LIMIT_FAILURE[2])
        _CACHE = None
        # 先尝试磁盘快照:表身份与版本都要匹配,不匹配就重建。
        snapshot = _load_snapshot(table)
        if snapshot is not None:
            _CACHE = (table, version, snapshot)
            _LIMIT_FAILURE = None
            _release_heap()
            return snapshot, True
        try:
            index = build(table)
        except IndexLimitError as error:
            _LIMIT_FAILURE = (table, version, str(error))
            raise
        _CACHE = (table, version, index)
        _LIMIT_FAILURE = None
        try:
            _save_snapshot(index, table)
        except Exception:
            pass                     # 快照失败只影响下次冷建速度
        _release_heap()
        return index, False


def get_index(table) -> EntityIndex:
    return _cached_index(table)[0]


def index_for(table) -> EntityIndex | None:
    with _LOCK:
        cached = _CACHE
    return cached[2] if cached and cached[0] is table and cached[1] == int(table.version) else None


def reset_cache(clear_snapshot: bool = False) -> None:
    """清内存缓存。`clear_snapshot=True` 同时删除磁盘快照(测试与排障用)。

    默认不删快照:版本校验已能保证不读到陈旧数据,保留快照可以让进程重启后
    仍然秒级可用。真正需要"从零重建"时显式传 True。
    """
    global _CACHE, _LIMIT_FAILURE
    with _LOCK:
        _CACHE = None
        _LIMIT_FAILURE = None
        if clear_snapshot:
            try:
                cache_path().unlink(missing_ok=True)
            except Exception:
                pass


def _resolve(index: EntityIndex, keys: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    resolved = {}
    for key in keys:
        if key in index.by_entity:
            resolved[key] = (key,)
        elif _kind(key) == "model" and len(key.removeprefix("model:")) >= 5:
            matches = tuple(k for k in index.by_entity if k.startswith(key) and _kind(k) == "model")
            if matches:
                resolved[key] = matches
    return resolved


def _balanced(uids, groups: dict[str, set[str]], count: int, metadata: dict,
              seen_pages: set[tuple] | None = None) -> tuple[str, ...]:
    """多型号独立队列轮流取页,不让一份长手册占满预算。"""
    pages = seen_pages if seen_pages is not None else set()
    queues = [deque(uid for uid in uids if uid in scope) for scope in groups.values()] if groups else [deque(uids)]
    picked = []
    while any(queues) and len(picked) < count:
        for queue in queues:
            while queue:
                uid = queue.popleft()
                meta = metadata[uid]
                page = (meta["file"], meta["page"])
                if page in pages:
                    continue
                pages.add(page)
                picked.append(uid)
                break
            if len(picked) >= count:
                break
    return tuple(picked)


def model_groups(index: EntityIndex, keys: tuple[str, ...]) -> dict[str, set[str]]:
    resolved = _resolve(index, keys)
    return {key: {uid for actual in resolved.get(key, ()) for uid in index.by_entity[actual]}
            for key in keys if _kind(key) == "model"}


def search(table, query: str, *, category: str | None = None, file: str | None = None,
           limit: int = 80, seed_rows: list[dict] | None = None) -> EntitySearch:
    keys = extract_entities(query, query=True, limit=MAX_QUERY_ENTITIES)
    models = {key for key in keys if _kind(key) == "model"}
    signals = {key for key in keys if _kind(key) not in {"model", "value"}}
    if not signals:
        return EntitySearch(keys, (), (), "skipped")
    index, cached = _cached_index(table)
    resolved = _resolve(index, keys)
    groups = model_groups(index, keys)
    model_scope = set().union(*groups.values()) if groups else set()
    slots = evidence_slots(query)

    def slot_groups(uids):
        result = {}
        for i, slot in enumerate(slots):
            scope = groups.get(slot.model, set()) if slot.model else None
            matched = {uid for uid in uids if (scope is None or uid in scope)
                       and slot.signal in index.entities_by_uid[uid]}
            if matched:
                result[str(i)] = matched
        return result or groups

    def accepts(uid):
        meta = index.metadata_by_uid[uid]
        return ((not models or uid in model_scope)
                and (not category or meta["category"] == category)
                and (not file or file.replace("\\", "/") in meta["file"]))

    def hits(entities):
        return {key for key, actual in resolved.items() if entities.intersection(actual)}

    def page_signals(uid):
        meta = index.metadata_by_uid[uid]
        page = (meta["file"], meta["page"])
        return hits(index.page_entities.get(page, index.entities_by_uid[uid])).intersection(signals)

    def rarity(key):
        return 1 + math.log((1 + index.file_count) / (1 + index.document_frequency.get(key, 0)))

    def order(uid):
        matched = hits(index.entities_by_uid[uid])
        score = sum(_WEIGHTS[_kind(key)] * rarity(key) for key in matched if _kind(key) != "model")
        meta = index.metadata_by_uid[uid]
        return (-score, -len(matched), meta["file"], meta["page"], uid)

    # 每个型号先取自己的合格 posting 预算,共享总线的先到块不能挤掉后面的型号。
    scopes = groups or {"": None}
    candidates = set()
    for scope in scopes.values():
        for query_key, actual_keys in resolved.items():
            matched_posting = set()
            for actual in actual_keys:
                for uid in index.by_entity[actual]:
                    if accepts(uid) and (scope is None or uid in scope):
                        matched_posting.add(uid)
            for uid in sorted(matched_posting, key=order)[:MAX_POSTING]:
                if len(candidates) >= MAX_QUERY_CANDIDATES:
                    break
                candidates.add(uid)
            if len(candidates) >= MAX_QUERY_CANDIDATES:
                break
        if len(candidates) >= MAX_QUERY_CANDIDATES:
            break
    direct = sorted((uid for uid in candidates if not signals or hits(index.entities_by_uid[uid]) & signals), key=order)
    direct_limit = min(MAX_DIRECT_CANDIDATES, max(1, limit // 2))
    expanded_limit = min(MAX_EXPANDED_CANDIDATES, max(1, limit // 4))
    pages: set[tuple] = set()
    direct_uids = _balanced(direct, slot_groups(direct), direct_limit, index.metadata_by_uid, pages)

    if seed_rows is None:
        seeds = direct_uids[:MAX_SEEDS]
    else:
        original = {row.get("uid") for row in seed_rows[:MAX_SEED_INPUTS]}
        eligible = sorted((uid for uid in original if uid in index.entities_by_uid and accepts(uid)
                           and (not signals or page_signals(uid))), key=order)
        seeds = _balanced(eligible, slot_groups(eligible), MAX_SEEDS, index.metadata_by_uid)
    neighbors, paths, pruned = set(), {}, 0
    for seed in seeds:
        seed_entities = index.entities_by_uid[seed]
        edges = sorted(key for key in seed_entities if _kind(key) == "model" or (
            not models and key in signals and _kind(key) in {"symbol", "interface"} and key not in _BROAD_SYMBOLS))
        for key in edges:
            eligible = [uid for uid in index.by_entity[key] if accepts(uid)]
            eligible.sort(key=order)
            for uid in eligible[:MAX_NEIGHBORS]:
                if uid == seed:
                    continue
                shared = seed_entities.intersection(index.entities_by_uid[uid])
                related = page_signals(uid)
                # 只有型号页眉/单一通用总线,而无当前问题信号的邻居不扩展。
                if (signals and not related) or (_kind(key) != "model" and len(shared - _BROAD_SYMBOLS) < 2):
                    pruned += 1
                    continue
                neighbors.add(uid)
                paths.setdefault(uid, {"seed_chunk_id": seed, "shared_entities": sorted(shared, key=lambda e: (
                    _kind(e) == "model", -rarity(e), e))[:4]})
    expanded = _balanced(sorted(neighbors, key=order), slot_groups(neighbors), expanded_limit, index.metadata_by_uid, pages)
    status = "used" if direct_uids or expanded else "empty"
    selected = direct_uids + expanded
    counts = {key.removeprefix("model:"): sum(uid in scope for uid in selected) for key, scope in groups.items()}
    return EntitySearch(keys, direct_uids, expanded, status, index, cached, len(seeds), pruned, counts,
                        {uid: paths[uid] for uid in expanded})


def diagnostics(result: EntitySearch) -> dict:
    out = {"enabled": True, "status": result.status, "query_entities": len(result.query_entities),
           "direct_candidates": len(result.direct_uids), "expanded_candidates": len(result.expanded_uids),
           "seeds": result.seeds, "pruned_neighbors": result.pruned, "by_model": result.by_model}
    if result.index is not None:
        out.update(index_rows=len(result.index.entities_by_uid), index_entities=len(result.index.by_entity),
                   index_build_ms=round(result.index.build_ms, 3), index_cached=result.index_cached)
    return out
