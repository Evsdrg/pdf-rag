# -*- coding: utf-8 -*-
"""策展最终评测集:过滤噪声 -> 按类别配平 -> 合并手写用例 -> 重校验 -> 写出。

组成三类,便于事后分类分析:
  mined   从表格挖出的(型号 + 参数 -> 带单位的规格值)
  topic   无型号、只有主题(考排序/跨文档区分能力)
  hand    人工手写(本轮真实踩坑的 case,含中文查询对英文手册)
"""
import collections, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent   # 仓库根目录
sys.path.insert(0, str(ROOT))
import lancedb
from backend import config

MINED = pathlib.Path(__file__).resolve().parent / "mined_cases.json"   # mine_eval3.py 的输出
OUT = ROOT / "eval_queries.json"

t = lancedb.connect(config.DB_PATH).open_table("chunks")
rows = t.to_arrow().select(["file", "page", "text", "model_no"]).to_pylist()
texts = [r["text"] for r in rows]
files = {r["file"] for r in rows}
head = [r["text"][:80] for r in rows]

def n_chunks(v):
    return sum(1 for x in texts if v in x)

mined = json.load(open(MINED, encoding="utf-8"))
# 路径分隔符规范化:mined_cases.json 出自早期 Windows 索引,存的是反斜杠路径;
# 现索引是正斜杠。不统一的话,后面的"期望文件存在"校验与写出的 expect 都会带错分隔符
# (eval_queries.json 里 43/55 条 expect 因此带反斜杠,曾把 recall 误判成 22%)。
for c in mined:
    c["file"] = c["file"].replace("\\", "/")

# --- 噪声过滤 ---
BAD_PARAM = re.compile(r"(第\s*\d+\s*步|step\s*\d|^GD\d|^GD5F|^GD9F|^\d+\s*K?$|寄存器|register\s*$)", re.I)
def param_ok(p: str) -> bool:
    if BAD_PARAM.search(p):
        return False
    # 参数名里不该有第二个"型号样"token(交叉参考表特征)
    toks = re.findall(r"[A-Z]{2,}\d+[A-Z0-9\-]*", p)
    return len(toks) <= 1

clean = [c for c in mined if param_ok(c["param"])]

# 去重:同 (型号,参数) 只留最独特的
seen, uniq = set(), []
for c in sorted(clean, key=lambda x: x["d"]):
    k = (c["model"].lower(), re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", c["param"].lower()))
    if k in seen:
        continue
    seen.add(k)
    uniq.append(c)

# 按类别配平, 每类最多 5 条
per_cat = collections.Counter()
balanced = []
for c in uniq:
    if per_cat[c["category"]] >= 5:
        continue
    per_cat[c["category"]] += 1
    balanced.append(c)
print("过滤后 mined:", len(clean), "-> 去重", len(uniq), "-> 配平", len(balanced))

# --- topic 类:无型号, 只有主题;要求该值在全库唯一归属一份文档 ---
topic = []
by_val = collections.defaultdict(set)
for c in clean:
    by_val[c["val"]].add(c["file"])
# 手工整理的主题词(取自文档领域),保证查询自然
TOPICS = [
    ("升降压转换器 输出电流限值", "TPS55289RYQR"),
    ("升降压转换器 输出电压纹波", "TPS55289RYQR"),
    ("高边栅极驱动 自举电容", "BDR2L00"),
    ("磁力计 供电电压范围", "QMC6309"),
    ("继电器 额定绝缘电压", "G5Q-14-DC12"),
    ("电流检测放大器 分流电阻", "ina226"),
    ("4G 模块 供电电压范围", "ML307R"),
    ("触摸按键 灵敏度调节", "CH592"),
]
for q, model in TOPICS:
    hit = [c for c in clean if model.lower() in c["file"].lower() or model.lower() in c["model"].lower()]
    if hit:
        c = hit[0]
        topic.append({"query": q, "expect": [model], "must_contain": [c["val"]],
                      "source": "topic", "_page": c["page"]})
print("topic 类:", len(topic))

# --- 手写类(保留),补齐 source 标记 ---
HAND = [
    ({"query": "W25Q32 供电电压", "must_contain": ["3.6"]}, "W25Q32JW"),
    ({"query": "DS18B20 温度传感器 精度", "must_contain": ["0.5"]}, "DS18B20"),
    ({"query": "CH592 蓝牙 SoC RISC-V", "must_contain": ["RISC-V"]}, "CH592"),
    ({"query": "TPS63020 升降压转换器 开关频率", "must_contain": ["2.4"]}, "TPS63020"),
    ({"query": "QMC6308 供电电压 VDD 范围", "must_contain": ["1.65", "1.95"]}, "QMC6308"),
    ({"query": "QMC6309 供电电压 VDD 范围", "must_contain": ["2.5", "3.6"]}, "QMC6309"),
    ({"query": "MSM8916 VDD_APC 绝对最大值", "must_contain": ["1.62"]}, "MSM8216"),
    ({"query": "LSM6DS3TR-C 陀螺仪加速度计电流消耗", "must_contain": ["0.45"]}, "LSM6DS3TR-C"),
    ({"query": "ML307R VBAT 供电范围", "must_contain": ["4.5"]}, "ML307R"),
    ({"query": "CH592 BLE 发送功率电流", "must_contain": ["17.2"]}, "CH592"),
]
hand = [{"query": q["query"], "expect": [e], "must_contain": q["must_contain"], "source": "hand"}
        for q, e in HAND]

# --- 汇总 + 逐条校验 ---
final = hand + topic + [
    {"query": c["query"], "expect": [c["file"]], "must_contain": [c["val"]],
     "source": "mined", "_page": c["page"], "_d": c["d"]} for c in balanced]

ok, dropped = [], []
for q in final:
    exp = q["expect"][0]
    hit_file = any(exp.lower() in f.lower() for f in files)
    if not hit_file:
        dropped.append((q["query"], f"期望文件不存在: {exp}")); continue
    # 答案必须确实存在于期望文件里
    exists = any(exp.lower() in r["file"].lower() and all(m in r["text"] for m in q["must_contain"])
                 for r in rows)
    if not exists:
        dropped.append((q["query"], "答案字面值不在期望文件中")); continue
    q["_n_chunks_with_val"] = max(n_chunks(m) for m in q["must_contain"])
    ok.append(q)

print(f"\n校验: 通过 {len(ok)} / 丢弃 {len(dropped)}")
for q, why in dropped[:10]:
    print(f"   丢弃 {q[:44]:<46} {why}")

for q in ok:
    q.pop("_d", None)
json.dump(ok, open(OUT, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
comp = collections.Counter(q["source"] for q in ok)
print(f"\n写出 {OUT.name}: {len(ok)} 条  {dict(comp)}")
