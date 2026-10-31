"""从单个 chunk 内的 Markdown pipe 表格保守提取条件事实。

只做确定性的表头/单元格解析：不调用模型、不跨 chunk 拼接表格、
不做数值换算、Min/Typ/Max 推断或条件继承。所有输出字段都能回到原 chunk 原文。

边界：
- 只认 Markdown pipe 表格（表头行 + 分隔行 + 数据行都在本 chunk 内）。
- 表头必须能定位参数(或符号)列与显式单位列；数值列角色(min/typ/max/value)必须唯一。
- 形状问题（缺表头、列数不一致、重复/歧义表头、表中途重复分隔行、代码 fence、
  HTML 表格、rowspan/colspan）整表丢弃；单元格问题（数值损坏、单位破损/缺失、
  数值格为空）只丢该行。
- 条件只来自显式 Condition/Test conditions/条件列，绝不从正文推断，也绝不向下继承。
- source.header_start_offset/header_end_offset 覆盖表头行到分隔行末尾；
  start_offset/end_offset 覆盖该数据行的完整原文范围。
"""
from __future__ import annotations

import re
from typing import Any

MAX_FACTS_CAP = 4
MAX_CELL_CHARS = 200
MAX_TEXT_CHARS = 100_000

# 单位白名单：大小写敏感，mA 与 MA、mΩ 与 MΩ 是不同单位。
UNIT_WHITELIST = frozenset({
    "V", "mV", "µV", "uV", "kV", "Vdc", "Vac", "Vrms", "Vpp",
    "A", "mA", "MA", "µA", "uA", "nA", "pA",
    "W", "mW", "µW", "uW", "dBm", "dBW", "W/mK", "W/m",
    "Hz", "kHz", "MHz", "GHz", "THz",
    "s", "ms", "µs", "us", "ns", "ps",
    "Ω", "mΩ", "MΩ", "kΩ", "GΩ",
    "F", "mF", "µF", "uF", "nF", "pF", "F/m",
    "H", "mH", "µH", "uH", "nH",
    "°C", "℃", "C", "K", "°F",
    "m", "cm", "mm", "µm", "um", "nm", "km",
    "%", "ppm", "ppb", "dB", "dBc", "rpm",
    "N", "kg", "g", "J", "Wh", "mJ",
    "bps", "kbps", "Mbps", "Gbps", "bit/s", "B", "KB", "MB",
    "V/m", "A/m", "lux", "cd/m2",
})

_NAME_HEADERS = ("parameter", "参数", "symbol", "符号", "item", "项目",
                 "characteristic", "特性", "参数名称", "parameter name")
_UNIT_HEADERS = ("unit", "单位", "units")
_CONDITION_HEADERS = ("condition", "conditions", "test condition", "test conditions",
                      "条件", "测试条件", "工作条件", "operating condition",
                      "operating conditions")

_ROLE_WORDS = {
    "min": "min", "minimum": "min",
    "typ": "typ", "typical": "typ",
    "max": "max", "maximum": "max",
    "value": "value", "nominal": "value", "default": "value", "rating": "value",
}

_NUMBER_RE = re.compile(r"^[+-]?\d+(?:\.\d+)?$")
_RANGE_RE = re.compile(r"^[+-]?\d+(?:\.\d+)?\s*(?:-|~|–|—|to)\s*[+-]?\d+(?:\.\d+)?$", re.I)
_SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")
_PLACEHOLDERS = frozenset({"", "-", "--", "—", "–", "n/a", "na"})
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_HTML_RE = re.compile(r"<\s*(table|tr|td|th|tbody|thead)\b", re.I)
_SPAN_RE = re.compile(r"<\s*(td|th)[^>]*\b(?:rowspan|colspan)\s*=", re.I)


class _AbortTable(Exception):
    """表级形状不可信，整表丢弃。"""


class _SkipRow(Exception):
    """单行单元格不可信，只丢这一行。"""


def _clip(text: str) -> str:
    if len(text) > MAX_CELL_CHARS:
        raise _SkipRow("单元格超出事实预算")
    return text


def _normalize(cell: str) -> str:
    value = cell.strip().strip("*").strip()
    value = value.rstrip(".").strip()
    value = re.sub(r"\s+", " ", value)
    return value.casefold()


def _split_cells(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [cell.strip() for cell in inner.split("|")]


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.count("|") >= 2


def _is_separator_line(line: str) -> bool:
    cells = _split_cells(line)
    if len(cells) < 2:
        return False
    return all(_SEPARATOR_CELL_RE.match(cell.replace(" ", "")) for cell in cells)


def _line_records(text: str) -> list[dict[str, Any]]:
    records = []
    start = 0
    for raw in text.split("\n"):
        records.append({"raw": raw, "start": start, "end": start + len(raw)})
        start += len(raw) + 1
    return records


def _table_runs(text: str) -> list[list[dict[str, Any]]]:
    """把 chunk 切成连续 pipe 行段；代码 fence 内的段不算表。"""
    records = _line_records(text)
    runs: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    in_fence = False
    for record in records:
        raw = record["raw"]
        if _FENCE_RE.match(raw):
            if current:
                runs.append(current)
                current = []
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _is_table_line(raw):
            current.append(record)
        else:
            if current:
                runs.append(current)
                current = []
    if current:
        runs.append(current)
    return runs


def _classify_header(cells: list[str]) -> dict[str, Any]:
    """把表头分类成名称列/单位列/条件列/数值角色列；形状不明确时抛 _AbortTable。"""
    plan: dict[str, Any] = {"name": None, "symbol": None, "unit": None, "condition": None,
                             "roles": {}, "role_columns": [], "header_units": {}}
    seen_labels: set[str] = set()
    for index, cell in enumerate(cells):
        raw = cell.strip()
        if not raw:
            raise _AbortTable("空表头")
        label = _normalize(raw)
        if label in seen_labels:
            raise _AbortTable("重复表头")
        seen_labels.add(label)
        paren = None
        match = re.match(r"^(?P<body>[^()]*)\((?P<inner>[^()]*)\)\s*$", raw)
        if match:
            body = match.group("body")
            inner = match.group("inner").strip()
            if inner in UNIT_WHITELIST:
                paren = inner
            elif inner.casefold() in _ROLE_WORDS:
                paren = inner
            else:
                body = raw  # 括号内容不是单位也不是角色，只当普通表头文本
        else:
            body = raw
        label = _normalize(body)
        role = _ROLE_WORDS.get(label)
        if role is None and paren is not None:
            role = _ROLE_WORDS.get(_normalize(paren))
        is_name = label in _NAME_HEADERS
        is_unit = label in _UNIT_HEADERS
        is_condition = label in _CONDITION_HEADERS
        if paren is not None and paren in UNIT_WHITELIST:
            plan["header_units"][index] = paren
        if role is not None:
            if role in plan["roles"].values():
                raise _AbortTable("数值列角色重复")
            plan["roles"][index] = role
            plan["role_columns"].append(index)
            continue
        if is_unit:
            if plan["unit"] is not None:
                raise _AbortTable("单位列重复")
            plan["unit"] = index
            continue
        if is_condition:
            if plan["condition"] is not None:
                raise _AbortTable("条件列重复")
            plan["condition"] = index
            continue
        if is_name:
            key = "symbol" if ("symbol" in label or "符号" in label) else "name"
            if plan[key] is not None:
                raise _AbortTable("名称列重复")
            plan[key] = index
            continue
        # 其它列（例如备注）不参与事实提取。
    if plan["name"] is None and plan["symbol"] is None:
        raise _AbortTable("没有参数/符号列")
    if not plan["role_columns"]:
        raise _AbortTable("没有可识别的数值列")
    if "value" in plan["roles"].values() and len(plan["roles"]) > 1:
        raise _AbortTable("value 与 min/typ/max 混合歧义")
    header_units = {column: unit for column, unit in plan["header_units"].items()
                    if column in plan["role_columns"]}
    if plan["unit"] is None:
        # 没有独立单位列时，只接受每个数值列表头都写明且完全一致的显式单位。
        if len(header_units) != len(plan["role_columns"]):
            raise _AbortTable("没有显式单位列")
        if len(set(header_units.values())) != 1:
            raise _AbortTable("表头单位不一致")
    return plan


def _cell_value(text: str) -> tuple[str, str]:
    """返回 (kind, value)：kind 为 number / range / missing / invalid。"""
    stripped = text.strip()
    if stripped.casefold() in _PLACEHOLDERS:
        return ("missing", stripped)
    if _NUMBER_RE.match(stripped):
        return ("number", stripped)
    if _RANGE_RE.match(stripped):
        return ("range", stripped)
    return ("invalid", stripped)


def _extract_from_table(run: list[dict[str, Any]], row: dict[str, Any]) -> list[dict[str, Any]]:
    if len(run) < 3:
        raise _AbortTable("表太短")
    header_record, sep_record = run[0], run[1]
    if not _is_separator_line(sep_record["raw"]):
        raise _AbortTable("缺少分隔行")
    header_cells = _split_cells(header_record["raw"])
    sep_cells = _split_cells(sep_record["raw"])
    if len(header_cells) != len(sep_cells):
        raise _AbortTable("表头与分隔行列数不一致")
    plan = _classify_header(header_cells)

    facts: list[dict[str, Any]] = []
    for record in run[2:]:
        try:
            fact = _row_fact(record, header_cells, plan, row,
                             header_record["start"], sep_record["end"])
        except _SkipRow:
            continue
        if fact is not None:
            facts.append(fact)
    return facts


def _row_fact(record: dict[str, Any], header_cells: list[str], plan: dict[str, Any],
              row: dict[str, Any], header_start: int, header_end: int) -> dict[str, Any] | None:
    unit_index = plan["unit"]
    condition_index = plan["condition"]
    name_index = plan["name"] if plan["name"] is not None else plan["symbol"]
    symbol_index = plan["symbol"]
    if _is_separator_line(record["raw"]):
        raise _AbortTable("表中途重复分隔行")
    cells = _split_cells(record["raw"])
    if len(cells) != len(header_cells):
        raise _AbortTable("数据行列数不一致")
    name = cells[name_index].strip()
    if not name:
        raise _SkipRow("参数名缺失（合并单元格）")
    if unit_index is not None:
        unit = cells[unit_index].strip()
        if not unit:
            raise _SkipRow("单位缺失")
        if unit not in UNIT_WHITELIST:
            raise _SkipRow("单位不在白名单")
        for column, header_unit in plan["header_units"].items():
            if column in plan["role_columns"] and header_unit != unit:
                raise _SkipRow("表头单位与单位列冲突")
    else:
        header_units = set(plan["header_units"][column] for column in plan["role_columns"])
        unit = header_units.pop() if header_units else ""
        if unit not in UNIT_WHITELIST:
            raise _SkipRow("单位不在白名单")
    values: dict[str, str] = {}
    usable = False
    for column in plan["role_columns"]:
        role = plan["roles"][column]
        kind, value = _cell_value(cells[column])
        if kind == "missing":
            if value == "":
                raise _SkipRow("数值格为空（合并单元格）")
            continue
        if kind == "invalid":
            raise _SkipRow("数值损坏")
        if kind == "range" and role != "value":
            raise _SkipRow("min/typ/max 列不写 range")
        values[role] = value
        usable = True
    if not usable:
        return None
    symbol = cells[symbol_index].strip() if symbol_index is not None else ""
    conditions = cells[condition_index].strip() if condition_index is not None else ""
    source = {
        "chunk_id": row.get("uid"),
        "index_md5": row.get("md5"),
        "start_offset": record["start"],
        "end_offset": record["end"],
        "offset_basis": "indexed_chunk",
        "header_start_offset": header_start,
        "header_end_offset": header_end,
    }
    return {
        "parameter": _clip(name),
        "symbol": _clip(symbol) or None,
        "subject": row.get("model_no") or "",
        "values": {key: _clip(value) for key, value in values.items()},
        "unit": unit,
        "conditions": _clip(conditions),
        "source": source,
    }


def relevance(fact: dict[str, Any], query: str) -> int:
    haystack = " ".join(part for part in (fact["parameter"], fact["symbol"] or "",
                                           fact["conditions"]) if part).casefold()
    score = 0
    folded = query.casefold()
    if folded and folded in haystack:
        score += 3
    for token in re.split(r"[^\w一-鿿]+", query):
        if token and token.casefold() in haystack:
            score += 1
    return score


def extract(row: dict, *, query: str = "", max_facts: int = 3) -> list[dict]:
    """从一个 chunk 中提取保守的条件事实列表。"""
    if not isinstance(row, dict):
        return []
    text = row.get("text")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_CHARS or not row.get("uid"):
        return []
    try:
        budget = int(max_facts)
    except (TypeError, ValueError):
        budget = 3
    budget = max(0, min(budget, MAX_FACTS_CAP))
    if budget == 0:
        return []
    facts: list[dict[str, Any]] = []
    seen: set[tuple] = set()
    for run in _table_runs(text):
        if not run[-1]["raw"].rstrip().endswith("|"):
            # 末行不完整：表格可能被硬切到下一个 chunk，整表丢弃。
            continue
        segment = text[run[0]["start"]:run[-1]["end"]]
        if _HTML_RE.search(segment) or _SPAN_RE.search(segment):
            continue  # HTML 表格、rowspan/colspan 合并单元格
        try:
            table_facts = _extract_from_table(run, row)
        except _AbortTable:
            continue
        for fact in table_facts:
            key = (fact["parameter"], fact["symbol"], fact["conditions"],
                   tuple(sorted(fact["values"].items())), fact["unit"])
            if key in seen:
                continue
            seen.add(key)
            facts.append(fact)
    if not query.strip():
        return facts[:budget]
    scored = [(relevance(fact, query), index, fact) for index, fact in enumerate(facts)]
    scored = [item for item in scored if item[0] > 0]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in scored[:budget]]
