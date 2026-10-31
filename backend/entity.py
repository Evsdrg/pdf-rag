"""默认关闭的确定性实体桥:查询时局部扩展,原始 chunk 始终是证据。"""
from __future__ import annotations

import math
import re
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

MAX_QUERY_ENTITIES = 16
MAX_ROW_ENTITIES = 48
MAX_DIRECT_CANDIDATES = 64
MAX_EXPANDED_CANDIDATES = 32
MAX_SEEDS = 8
MAX_SEED_INPUTS = 256
MAX_POSTING = 256
MAX_QUERY_CANDIDATES = 4096
MAX_NEIGHBORS = 64
MAX_INDEX_ROWS = 50_000
MAX_INDEX_BYTES = 128_000_000
MAX_INDEX_LINKS = 1_000_000

_MODEL_RE = re.compile(r"[A-Za-z0-9]+(?:[-_.+#][A-Za-z0-9]+)*(?:\([A-Za-z0-9]+\))?")
_NOT_MODEL_RE = re.compile(
    r"(?:v\d+(?:[._-]\d+)*|0x[0-9a-f]+|(?:i2c|i2s|qspi|spi|usart|uart|gpio|usb|can|sdio|pwm|adc|dac|tim|timer)\d*)$",
    re.I,
)
_INTERFACE_RE = re.compile(
    r"(?<![a-z0-9_])(?P<name>i[2²]c|i[2²]s|qspi|spi|usart|uart|gpio|usb|can|sdio|pwm)"
    r"\d*(?![a-z0-9_])", re.I,
)
_SYMBOL_RE = re.compile(
    r"(?<![a-z0-9_])(?:vdd(?:[ _\t]*(?:apc|core|mem|ioq|io|rf))?|vin|vout|vbat|vled|vcc|"
    r"idd(?:[ _\t]*(?:hp|lp|pd|standby))?|ibias|iout|sda|scl|sa0|cs|n?reset|en|cbst|"
    r"r[ _\t]*(?:in|out)|ftype)(?![a-z0-9_])", re.I,
)
# SI 前缀区分大小写:mA 与 MA、mΩ 与 MΩ 不能成为同一个实体。
_VALUE_RE = re.compile(
    r"(?<![A-Za-z0-9.+-])[+-]?\d+(?:\.\d+)?\s*"
    r"(?:GHz|MHz|kHz|Hz|dBm|dB|ppm|°C|℃|mm|cm|[µμu]m|nm|"
    r"[pnumkMµμ]?[AVWΩFH]|[pnumµμ]?s|%)(?![A-Za-z0-9])"
)
_PARAMETER_ALIASES = (
    ("supply_voltage", ("supply voltage", "operating voltage", "供电电压", "工作电压", "电源电压")),
    ("input_voltage", ("input voltage", "输入电压")),
    ("output_voltage", ("output voltage", "输出电压")),
    ("current", ("current", "电流")),
    ("frequency", ("frequency", "频率")),
    ("temperature", ("temperature", "温度")),
    ("address", ("address", "地址")),
    ("package", ("package", "封装")),
    ("pin", ("pinout", "pin", "引脚", "管脚")),
    ("power", ("power consumption", "standby power", "功耗")),
    ("accuracy", ("accuracy", "精度", "准确度")),
    ("impedance", ("impedance", "阻抗")),
    ("resistance", ("resistance", "电阻")),
    ("capacitance", ("capacitance", "电容")),
    ("inductance", ("inductance", "电感")),
    ("bandwidth", ("bandwidth", "带宽")),
    ("odr", ("odr", "output data rate", "输出数据率")),
    ("gain", ("gain", "增益")),
    ("pullup", ("pull-up", "pull up", "上拉")),
)


def _compile_aliases():
    patterns = []
    for name, aliases in _PARAMETER_ALIASES:
        english = tuple(alias for alias in aliases if alias.isascii())
        chinese = tuple(alias for alias in aliases if not alias.isascii())
        pattern = re.compile(
            r"(?<![a-z0-9])(?:" + "|".join(
                re.escape(alias).replace(r"\ ", r"\s+") for alias in english
            ) + r")(?![a-z0-9])"
        )
        patterns.append((name, tuple(alias.split()[0] for alias in english), pattern, chinese))
    return tuple(patterns)


_PARAMETERS = _compile_aliases()
_WEIGHTS = {"model": 6, "symbol": 3, "interface": 2, "parameter": 2, "value": 1}
_PRIORITY = {"model": 0, "symbol": 1, "interface": 2, "parameter": 3, "value": 4}
_BROAD_SYMBOLS = {"symbol:" + value for value in ("vdd", "vin", "vout", "vbat", "vcc", "sda", "scl", "cs", "en")}


def _kind(key: str) -> str:
    return key.split(":", 1)[0]


def _model_tokens(text: str) -> set[str]:
    tokens = set()
    for match in _MODEL_RE.finditer(text):
        value = match.group().casefold()
        if (len(value) >= 3 and re.search(r"[a-z]", value) and re.search(r"\d", value)
                and not _NOT_MODEL_RE.fullmatch(value) and not _SYMBOL_RE.fullmatch(value)):
            tokens.add(value)
            # 多型号文档可列 MSM8216-MSM8616-MSM8916;普通料号的 -C/-TR 后缀不拆。
            parts = value.split("-")
            if len(parts) > 1 and all(len(p) >= 4 and re.search(r"[a-z]", p) and re.search(r"\d", p)
                                      for p in parts):
                tokens.update(parts)
    return tokens


def extract_entities(text: str, *, model_no: str = "", query: bool = False,
                     limit: int = MAX_ROW_ENTITIES) -> tuple[str, ...]:
    keys: set[str] = set()
    values = tuple(_VALUE_RE.finditer(text))
    if query:
        # 数字+单位不作为料号解析,例如 100MHz 和 3.3V。
        identity = _VALUE_RE.sub(" ", text)
    else:
        identity = model_no
    keys.update("model:" + token for token in _model_tokens(identity))
    for match in _INTERFACE_RE.finditer(text):
        name = match["name"].casefold().replace("²", "2")
        if name != "can" or match["name"].isupper():
            keys.add("interface:" + name)
    for match in _SYMBOL_RE.finditer(text):
        value = re.sub(r"[ _\t]+", "", match.group()).casefold()
        keys.add("symbol:" + value)
    for match in values[:16]:
        value = re.sub(r"\s+", "", match.group()).replace("µ", "u").replace("μ", "u").replace("℃", "°C")
        keys.add("value:" + value)
    folded = text.casefold()
    for name, starts, pattern, chinese in _PARAMETERS:
        if any(alias in folded for alias in chinese) or (
                any(start in folded for start in starts) and pattern.search(folded)):
            keys.add("parameter:" + name)
    return tuple(sorted(keys, key=lambda key: (_PRIORITY[_kind(key)], key))[:limit])


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
        try:
            index = build(table)
        except IndexLimitError as error:
            _LIMIT_FAILURE = (table, version, str(error))
            raise
        _CACHE = (table, version, index)
        _LIMIT_FAILURE = None
        return index, False


def get_index(table) -> EntityIndex:
    return _cached_index(table)[0]


def index_for(table) -> EntityIndex | None:
    with _LOCK:
        cached = _CACHE
    return cached[2] if cached and cached[0] is table and cached[1] == int(table.version) else None


def reset_cache() -> None:
    global _CACHE, _LIMIT_FAILURE
    with _LOCK:
        _CACHE = None
        _LIMIT_FAILURE = None


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
    if not keys or (not models and not signals):
        return EntitySearch(keys, (), (), "skipped")
    index, cached = _cached_index(table)
    resolved = _resolve(index, keys)
    groups = model_groups(index, keys)
    model_scope = set().union(*groups.values()) if groups else set()

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
                candidates.add(uid)
            if len(candidates) >= MAX_QUERY_CANDIDATES:
                break
        if len(candidates) >= MAX_QUERY_CANDIDATES:
            break
    direct = sorted((uid for uid in candidates if not signals or hits(index.entities_by_uid[uid]) & signals), key=order)
    direct_limit = min(MAX_DIRECT_CANDIDATES, max(1, limit // 2))
    expanded_limit = min(MAX_EXPANDED_CANDIDATES, max(1, limit // 4))
    pages: set[tuple] = set()
    direct_uids = _balanced(direct, groups, direct_limit, index.metadata_by_uid, pages)

    if seed_rows is None:
        seeds = direct_uids[:MAX_SEEDS]
    else:
        original = {row.get("uid") for row in seed_rows[:MAX_SEED_INPUTS]}
        eligible = sorted((uid for uid in original if uid in index.entities_by_uid and accepts(uid)
                           and (not signals or page_signals(uid))), key=order)
        seeds = _balanced(eligible, groups, MAX_SEEDS, index.metadata_by_uid)
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
    expanded = _balanced(sorted(neighbors, key=order), groups, expanded_limit, index.metadata_by_uid, pages)
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
