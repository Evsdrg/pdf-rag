"""共享查询词法:完整料号、接口/参数符号和值,不推断或回写文档身份。"""
import re
from dataclasses import dataclass
from itertools import islice

_MODEL_RE = re.compile(r"[A-Za-z0-9]+(?:[-_.+#][A-Za-z0-9]+)*(?:\([A-Za-z0-9]+\))?")
_NOT_MODEL_RE = re.compile(
    r"(?:v\d+(?:[._-]\d+)*|0x[0-9a-f]+|(?:i2c|i2s|qspi|spi|usart|uart|gpio|usb|can|sdio|pwm|adc|dac|tim|timer)\d*|"
    r"(?:sot|sop|soic|tssop|msop|qfn|dfn|dip|lga|bga)[-]?\d+[A-Za-z]*(?:-[A-Za-z0-9]+)*)$", re.I,
)
# 按共同前缀分组,避免每个字符位置重复尝试十几个同首字母分支。
_INTERFACE_BODY = r"i[2²][cs]|qspi|s(?:pi|dio)|u(?:sart|art|sb)|gpio|can|pwm"
_SYMBOL_BODY = (
    r"v(?:dif[12]|dd(?:[ _\t]*(?:apc|core|mem|ioq|io|rf))?|in|out|bat|led|cc|gs|ds)|"
    r"i(?:dd(?:[ _\t]*(?:hp|lp|pd|standby))?|bias|out)|s(?:da|cl|a0)|c(?:s|bst)|"
    r"n?reset|en|r[ _\t]*(?:in|out)|ftype"
)
_INTERFACE_RE = re.compile(r"(?<![a-z0-9_])(?P<name>" + _INTERFACE_BODY + r")\d*(?![a-z0-9_])", re.I)
_SYMBOL_RE = re.compile(r"(?<![a-z0-9_])(?:" + _SYMBOL_BODY + r")(?![a-z0-9_])", re.I)
# 两类完整词在当前白名单和边界下互不重叠,故可合并扫描;新增词需保持该约束。
_SIGNAL_RE = re.compile(
    r"(?<![a-z0-9_])(?:(?P<interface>(?P<name>" + _INTERFACE_BODY + r")\d*)|"
    r"(?P<symbol>" + _SYMBOL_BODY + r"))(?![a-z0-9_])", re.I,
)
# 型号内的 1G / 3.3V 不是参数值;SI 前缀仍区分大小写。
_UNIT = (r"(?:GHz|MHz|kHz|Hz|dBm|dB|dps|ppm|°C|℃|mm|cm|[µμu]m|nm|"
         r"[pnumkMµμ]?[AVWΩFHS]|[pnumµμ]?s|G|g|%)")
# 数字/空白与后续单位首字符不相交,无需回溯尝试更短数字或空白(Python>=3.13)。
VALUE_RE = re.compile(r"(?<![A-Za-z0-9_.+#-])[±+-]?\d++(?:\.\d++)?\s*+" + _UNIT + r"(?![A-Za-z0-9_])")
_QUANTITY_RE = re.compile(r"[±+-]?\d+(?:\.\d+)?\s*" + _UNIT, re.I)
_PARAMETER_ALIASES = (
    ("supply_voltage", ("supply voltage", "operating voltage", "供电电压", "工作电压", "电源电压")),
    ("input_voltage", ("input voltage", "输入电压")),
    ("output_voltage", ("output voltage", "fixed output", "输出电压", "固定输出")),
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
    ("dropout", ("dropout", "dropout voltage", "vdif1", "vdif2", "vdrop", "压差")),
    ("load_regulation", ("load regulation", "load reg", "负载调整率")),
    ("measurement_range", ("gyroscope range", "gyro range", "full scale range", "陀螺仪量程", "量程")),
    ("gyroscope", ("gyroscope", "gyro", "陀螺仪")),
    ("absolute_maximum", ("absolute maximum", "maximum ratings", "limit parameter", "绝对最大", "最大额定", "极限参数")),
    ("ordering", ("ordering", "marking", "marking rule", "订货", "订购", "打标")),
    ("dimensions", ("dimension", "dimensions", "封装尺寸", "封装形式")),
    ("static_characteristics", ("static characteristics", "dc characteristics", "静态特性", "dc 特性", "电气特性")),
    ("timing", ("dynamic characteristics", "switching characteristics", "timing", "tpd", "tplz", "传输延迟", "动态特性", "时序")),
    ("features", ("features", "特性列表", "主要特点")),
    ("turn_on", ("turn on time", "turn-on time", "启动时间")),
    ("temperature_coefficient", ("temperature coefficient", "tco", "零偏温漂", "零偏温度系数")),
    ("dummy_cycle", ("dummy cycle", "dummy cycles")),
    ("application", ("application circuit", "applied circuit", "应用电路")),
    ("output_high", ("voh", "高电平输出电压")),
    ("output_low", ("vol", "低电平输出电压")),
    ("on_resistance", ("rds(on)", "rds (on)", "导通电阻")),
    ("continuous_current", ("continuous drain current", "连续漏极电流")),
    ("quiescent_current", ("quiescent current", "static bias", "静态偏置电流", "静态电流")),
)


_ASCII_WORD_RE = re.compile(r"[a-z0-9]+")


def _compile_aliases():
    patterns = []
    for name, aliases in _PARAMETER_ALIASES:
        english = tuple(alias for alias in aliases if alias.isascii())
        chinese = tuple(alias for alias in aliases if not alias.isascii())
        pattern = re.compile(r"(?<![a-z0-9])(?:" + "|".join(
            re.escape(alias).replace(r"\ ", r"\s+") for alias in english) + r")(?![a-z0-9])")
        starts = frozenset(_ASCII_WORD_RE.match(alias).group() for alias in english)
        patterns.append((name, starts, pattern, chinese))
    return tuple(patterns)


_PARAMETERS = _compile_aliases()
_PRIORITY = {"model": 0, "symbol": 1, "interface": 2, "parameter": 3, "value": 4}
_TERM_RE = re.compile(r"[\u4e00-\u9fff]+|[A-Za-z0-9][A-Za-z0-9\-._+#]*(?:\([A-Za-z0-9]+\))?")


def _is_model(value: str) -> bool:
    return (len(value) >= 3 and bool(re.search(r"[a-z]", value, re.I)) and bool(re.search(r"\d", value))
            and not _NOT_MODEL_RE.fullmatch(value) and not _SYMBOL_RE.fullmatch(value)
            and not _QUANTITY_RE.fullmatch(value))


def model_tokens(text: str) -> list[str]:
    tokens = []
    for match in _MODEL_RE.finditer(VALUE_RE.sub(" ", text)):
        value = match.group()
        if not _is_model(value):
            continue
        parts = value.split("-")
        # 只拆每段本身都为完整料号的列表,不能把 3.3V/3.3S 当第二个型号。
        if len(parts) > 1 and all(len(part) >= 4 and _is_model(part) for part in parts):
            tokens.extend(parts)
        else:
            tokens.append(value)
    return list(dict.fromkeys(tokens))


def query_terms(query: str) -> tuple[list[str], set[str]]:
    models = {token.casefold() for token in model_tokens(query)}
    terms = []
    for match in _TERM_RE.finditer(query):
        run = match.group()
        if run.casefold() in models or any(part.casefold() in models for part in run.split("-")):
            continue
        if "\u4e00" <= run[0] <= "\u9fff":
            terms.extend([run] if len(run) <= 3 else (run[i:i + 2] for i in range(len(run) - 1)))
        elif len(run) >= 3 or _SYMBOL_RE.fullmatch(run):
            terms.append(run)
    return list(dict.fromkeys(terms)), models


def extract_entities(text: str, *, model_no: str = "", query: bool = False, limit: int = 48) -> tuple[str, ...]:
    keys = {"model:" + token.casefold() for token in model_tokens(text if query else model_no)}
    for match in _SIGNAL_RE.finditer(text):
        if match["interface"] is not None:
            name = match["name"].casefold().replace("²", "2")
            if name != "can" or match["name"].isupper():
                keys.add("interface:" + name)
        else:
            keys.add("symbol:" + re.sub(r"[ _\t]+", "", match.group()).casefold())
    for match in islice(VALUE_RE.finditer(text), 16):
        value = re.sub(r"\s+", "", match.group()).replace("µ", "u").replace("μ", "u").replace("℃", "°C")
        keys.add("value:" + value)
    folded = text.casefold()
    words = set(_ASCII_WORD_RE.findall(folded))
    for name, starts, pattern, chinese in _PARAMETERS:
        if any(alias in folded for alias in chinese) or (
                not starts.isdisjoint(words) and pattern.search(folded)):
            keys.add("parameter:" + name)
    return tuple(sorted(keys, key=lambda key: (_PRIORITY[key.split(":", 1)[0]], key))[:limit])


@dataclass(frozen=True, slots=True)
class EvidenceSlot:
    model: str
    signal: str
    conditions: tuple[str, ...] = ()


MAX_EVIDENCE_SLOTS = 24
_CONDITION_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:VCC|VDD|VGS|VDS|VIN|VOUT(?:\(T\))?|IOUT|IO|IL|RL|CL|TA)"
    r"\s*=\s*[+-]?\d+(?:\.\d+)?\s*" + _UNIT +
    r"(?:\s*[~～–]\s*[+-]?\d+(?:\.\d+)?\s*" + _UNIT + r")?(?![A-Za-z0-9_])", re.I,
)


def _condition_key(value: str) -> str:
    name, literal = re.sub(r"\s+", "", value).split("=", 1)
    return name.casefold() + "=" + literal.replace("µ", "u").replace("μ", "u")


def evidence_slots(query: str) -> tuple[EvidenceSlot, ...]:
    keys = extract_entities(query, query=True)
    models = [key for key in keys if key.startswith("model:")] or [""]
    parameters = [key for key in keys if key.startswith("parameter:")]
    # 只去已被更具体参数覆盖的父词;温度/频率等独立子问题不能被一概删去。
    parents = {
        "current": {"quiescent_current", "continuous_current"},
        "temperature": {"temperature_coefficient"},
        "resistance": {"on_resistance"},
        "package": {"dimensions", "ordering"},
        "gyroscope": {"measurement_range", "temperature_coefficient"},
        "output_voltage": {"output_high", "output_low"},
    }
    names = {key.split(":", 1)[1] for key in parameters}
    signals = [key for key in parameters if not names.intersection(parents.get(key.split(":", 1)[1], set()))]
    signals = signals or [key for key in keys if key.startswith(("symbol:", "interface:"))]
    if not signals:
        return ()
    conditions = tuple(dict.fromkeys(_condition_key(match.group())
                                    for match in _CONDITION_RE.finditer(query)))[:4]
    slots = []
    for model in models:
        for signal in signals:
            if len(conditions) > 1 and len(models) == 1 and len(signals) == 1:
                slots.extend(EvidenceSlot(model, signal, (condition,)) for condition in conditions)
            else:
                slots.append(EvidenceSlot(model, signal, conditions))
    return tuple(slots[:MAX_EVIDENCE_SLOTS])


def slot_score(slot: EvidenceSlot, keys, text: str = "") -> float:
    if slot.signal not in keys:
        return 0.0
    actual = {_condition_key(match.group()) for match in _CONDITION_RE.finditer(text)}
    return 1.0 + sum(condition in actual for condition in slot.conditions)
