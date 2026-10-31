"""默认关闭的确定性实体桥:查询时局部扩展,原始 chunk 始终是证据。"""
from __future__ import annotations

import re
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field

MAX_QUERY_ENTITIES = 16
MAX_ROW_ENTITIES = 48
MAX_DIRECT_CANDIDATES = 64
MAX_EXPANDED_CANDIDATES = 32
MAX_SEEDS = 8
MAX_POSTING = 256
MAX_NEIGHBORS = 64
MAX_INDEX_ROWS = 50_000
MAX_INDEX_BYTES = 128_000_000
MAX_INDEX_LINKS = 1_000_000

_MODEL_RE = re.compile(r"[A-Za-z0-9]+(?:[-_+#][A-Za-z0-9]+)*(?:\([A-Za-z0-9]+\))?")
_NOT_MODEL_RE = re.compile(
    r"(?:v\d+|0x[0-9a-f]+|(?:i2c|i2s|qspi|spi|usart|uart|gpio|usb|can|sdio|pwm|adc|dac|tim|timer)\d*)$",
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


@dataclass(frozen=True, slots=True)
class EntitySearch:
    query_entities: tuple[str, ...]
    direct_uids: tuple[str, ...]
    expanded_uids: tuple[str, ...]
    status: str
    index: EntityIndex | None = field(default=None, repr=False, compare=False)
    index_cached: bool = False

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
    return EntityIndex(version, {key: tuple(value) for key, value in postings.items()},
                       entities, metadata, (time.perf_counter() - start) * 1000)


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


def search(table, query: str, *, category: str | None = None, file: str | None = None,
           limit: int = 80) -> EntitySearch:
    keys = extract_entities(query, query=True, limit=MAX_QUERY_ENTITIES)
    models = {key for key in keys if _kind(key) == "model"}
    signals = {key for key in keys if _kind(key) not in {"model", "value"}}
    if not keys or (not models and not signals):
        return EntitySearch(keys, (), (), "skipped")
    index, cached = _cached_index(table)
    resolved = _resolve(index, keys)
    model_scope = {uid for key in models for actual in resolved.get(key, ()) for uid in index.by_entity[actual]}

    def accepts(uid):
        meta = index.metadata_by_uid[uid]
        return ((not models or uid in model_scope)
                and (not category or meta["category"] == category)
                and (not file or file.replace("\\", "/") in meta["file"]))

    def matched(uid):
        entities = index.entities_by_uid[uid]
        return {key for key, actual in resolved.items() if entities.intersection(actual)}

    def order(uid):
        hits = matched(uid)
        meta = index.metadata_by_uid[uid]
        return (-sum(_WEIGHTS[_kind(key)] for key in hits), -len(hits), meta["file"], meta["page"], uid)

    candidates = set()
    for actual_keys in resolved.values():
        for actual in actual_keys:
            eligible = (uid for uid in index.by_entity[actual] if accepts(uid))
            for n, uid in enumerate(eligible):
                if n >= MAX_POSTING:
                    break
                candidates.add(uid)
    # 有显式型号但缺少其它白名单词时可做型号召回;否则至少命中一个非型号查询词。
    direct = [uid for uid in candidates if not signals or matched(uid).intersection(signals)]
    direct.sort(key=order)
    direct_limit = min(MAX_DIRECT_CANDIDATES, max(1, limit // 2))
    expanded_limit = min(MAX_EXPANDED_CANDIDATES, max(1, limit // 4))

    def take_pages(uids, count, seen):
        picked = []
        for uid in uids:
            meta = index.metadata_by_uid[uid]
            page = (meta["file"], meta["page"])
            if page not in seen:
                seen.add(page)
                picked.append(uid)
                if len(picked) >= count:
                    break
        return tuple(picked)

    pages: set[tuple] = set()
    direct_uids = take_pages(direct, direct_limit, pages)
    neighbors = set()
    for seed in direct_uids[:MAX_SEEDS]:
        seed_entities = index.entities_by_uid[seed]
        edges = sorted(key for key in seed_entities if _kind(key) == "model" or (
            not models and _kind(key) in {"symbol", "interface"} and key not in _BROAD_SYMBOLS))
        for key in edges:
            n = 0
            for uid in index.by_entity[key]:
                if not accepts(uid):
                    continue
                n += 1
                if n > MAX_NEIGHBORS:
                    break
                shared = seed_entities.intersection(index.entities_by_uid[uid])
                if _kind(key) == "model" or len({e for e in shared if _kind(e) != "model"}) >= 2:
                    neighbors.add(uid)
    expanded = take_pages(sorted(neighbors, key=order), expanded_limit, pages)
    status = "used" if direct_uids or expanded else "empty"
    return EntitySearch(keys, direct_uids, expanded, status, index, cached)


def diagnostics(result: EntitySearch) -> dict:
    out = {"enabled": True, "status": result.status, "query_entities": len(result.query_entities),
           "direct_candidates": len(result.direct_uids), "expanded_candidates": len(result.expanded_uids)}
    if result.index is not None:
        out.update(index_rows=len(result.index.entities_by_uid), index_entities=len(result.index.by_entity),
                   index_build_ms=round(result.index.build_ms, 3), index_cached=result.index_cached)
    return out
