"""共享查询词法:完整料号、接口/参数符号和值,不推断或回写文档身份。"""
import re
from itertools import islice

_MODEL_RE = re.compile(r"[A-Za-z0-9]+(?:[-_.+#][A-Za-z0-9]+)*(?:\([A-Za-z0-9]+\))?")
_NOT_MODEL_RE = re.compile(
    r"(?:v\d+(?:[._-]\d+)*|0x[0-9a-f]+|(?:i2c|i2s|qspi|spi|usart|uart|gpio|usb|can|sdio|pwm|adc|dac|tim|timer)\d*|"
    r"(?:sot|sop|soic|tssop|msop|qfn|dfn|dip|lga|bga)[-]?\d+)$", re.I,
)
_INTERFACE_RE = re.compile(
    r"(?<![a-z0-9_])(?P<name>i[2²]c|i[2²]s|qspi|spi|usart|uart|gpio|usb|can|sdio|pwm)"
    r"\d*(?![a-z0-9_])", re.I,
)
_SYMBOL_RE = re.compile(
    r"(?<![a-z0-9_])(?:vdd(?:[ _\t]*(?:apc|core|mem|ioq|io|rf))?|vin|vout|vbat|vled|vcc|vgs|vds|"
    r"idd(?:[ _\t]*(?:hp|lp|pd|standby))?|ibias|iout|sda|scl|sa0|cs|n?reset|en|cbst|"
    r"r[ _\t]*(?:in|out)|ftype)(?![a-z0-9_])", re.I,
)
# 型号内的 1G / 3.3V 不是参数值;SI 前缀仍区分大小写。
_UNIT = (r"(?:GHz|MHz|kHz|Hz|dBm|dB|dps|ppm|°C|℃|mm|cm|[µμu]m|nm|"
         r"[pnumkMµμ]?[AVWΩFHS]|[pnumµμ]?s|G|g|%)")
VALUE_RE = re.compile(r"(?<![A-Za-z0-9_.+#-])[±+-]?\d+(?:\.\d+)?\s*" + _UNIT + r"(?![A-Za-z0-9_])")
_QUANTITY_RE = re.compile(r"[±+-]?\d+(?:\.\d+)?\s*" + _UNIT, re.I)
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
        pattern = re.compile(r"(?<![a-z0-9])(?:" + "|".join(
            re.escape(alias).replace(r"\ ", r"\s+") for alias in english) + r")(?![a-z0-9])")
        patterns.append((name, tuple(alias.split()[0] for alias in english), pattern, chinese))
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
    for match in _INTERFACE_RE.finditer(text):
        name = match["name"].casefold().replace("²", "2")
        if name != "can" or match["name"].isupper():
            keys.add("interface:" + name)
    for match in _SYMBOL_RE.finditer(text):
        keys.add("symbol:" + re.sub(r"[ _\t]+", "", match.group()).casefold())
    for match in islice(VALUE_RE.finditer(text), 16):
        value = re.sub(r"\s+", "", match.group()).replace("µ", "u").replace("μ", "u").replace("℃", "°C")
        keys.add("value:" + value)
    folded = text.casefold()
    for name, starts, pattern, chinese in _PARAMETERS:
        if any(alias in folded for alias in chinese) or (
                any(start in folded for start in starts) and pattern.search(folded)):
            keys.add("parameter:" + name)
    return tuple(sorted(keys, key=lambda key: (_PRIORITY[key.split(":", 1)[0]], key))[:limit])
