# -*- coding: utf-8 -*-
"""评测用例挖掘 v3:只收带单位的规格值(排除寄存器二进制、裸整数、同族共享值)"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent   # 仓库根目录
sys.path.insert(0, str(ROOT))
import lancedb
from backend import config

# 挖掘结果落在这里,再由 curate_eval.py 策展成 eval_queries.json
MINED = pathlib.Path(__file__).resolve().parent / "mined_cases.json"

# 必须带明确单位 —— 这才是可当作"规格值"检索的答案
UNIT_VAL = re.compile(
    r"^\s*[-±~]?\d+(?:\.\d+)?\s*"
    r"(mA|uA|µA|nA|mV|V|MHz|kHz|GHz|Hz|mΩ|kΩ|Ω|mH|uH|nH|pH|dBm|dB|%|pF|nF|uF|"
    r"ms|us|ns|s|°C|A|W|mW|kbit|Mbit|bit|Vdc)\s*(?:max|min|typ)?\.?\s*$", re.I)
DOCWORD = re.compile(r"(规格书|手册|指南|说明书|参考|用户|数据手册|datasheet|manual|guide)", re.I)

t = lancedb.connect(config.DB_PATH).open_table("chunks")
rows = t.to_arrow().select(["file", "page", "text", "category", "model_no"]).to_pylist()
texts = [r["text"] for r in rows]

def table_rows(text):
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("|") or set(line) <= set("|- :"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 2:
            yield cells

cands = []
for r in rows:
    model = (r["model_no"] or "").strip()
    if not model or DOCWORD.search(model) or len(model) < 4:
        continue
    for cells in table_rows(r["text"]):
        param = re.sub(r"[_\s]+", " ", cells[0]).strip(" _")
        if not re.search(r"[A-Za-z\u4e00-\u9fff]", param) or not (4 <= len(param) <= 22):
            continue
        if UNIT_VAL.match(param):
            continue
        if model.lower().replace("-", "")[:6] in param.lower().replace("-", ""):
            continue
        for c in cells[1:]:
            v = re.sub(r"\s+", " ", c).strip()
            if not UNIT_VAL.match(v):
                continue
            cands.append({"model": model, "param": param, "val": v, "file": r["file"],
                          "page": int(r["page"]) + 1, "category": r["category"]})

best: dict[tuple, dict] = {}
for c in cands:
    best.setdefault((c["file"], c["model"], c["param"], c["val"]), c)
print(f"带单位候选: {len(best)}")

picked = []
for c in best.values():
    d = sum(1 for x in texts if c["val"] in x)
    if d > 5:                     # 同族共享值(如 ±125 出现在 DSL/DSR/DS3)直接淘汰
        continue
    c["d"] = d
    c["query"] = f"{c['model']} {c['param']}"
    picked.append(c)

picked.sort(key=lambda x: (x["d"], x["category"]))
print(f"辨识度 <=5: {len(picked)}\n")
for c in picked[:70]:
    print(f"[{c['category'][:11]:<11}] d={c['d']} p{c['page']:<4} {c['query'][:50]:<52} -> {c['val']}")
json.dump(picked, open(MINED, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n-> {len(picked)} 条候选 -> {MINED}")
