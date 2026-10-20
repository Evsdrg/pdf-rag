# -*- coding: utf-8 -*-
"""细粒度画像:定位那 6 秒到底藏在哪 + 正确的 RSS 测量"""
import ctypes, gc, pathlib, statistics, sys, threading, time

ROOT = pathlib.Path(__file__).resolve().parent.parent   # 仓库根目录
sys.path.insert(0, str(ROOT))
import lancedb
from backend import config
import backend.retrieval as R
import backend.doc_utils as D

class PMC(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

_k32 = ctypes.windll.kernel32
_k32.GetCurrentProcess.restype = ctypes.c_void_p      # 关键:句柄是指针宽度
_k32.K32GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(PMC), ctypes.c_ulong]

def rss():
    p = PMC(); p.cb = ctypes.sizeof(PMC)
    _k32.K32GetProcessMemoryInfo(_k32.GetCurrentProcess(), ctypes.byref(p), p.cb)
    return p.WorkingSetSize / 1048576, p.PeakWorkingSetSize / 1048576

db = lancedb.connect(config.DB_PATH)
t = db.open_table("chunks")
b, pk = rss()
print(f"=== 基准 RSS {b:.0f} MB (进程峰值 {pk:.0f} MB) ===\n")

# ---------- 细粒度阶段计时 ----------
ACC = {}
def wrap(mod, name, label=None):
    f = getattr(mod, name)
    lbl = label or name
    def g(*a, **k):
        t0 = time.perf_counter(); r = f(*a, **k)
        ACC[lbl] = ACC.get(lbl, 0.0) + (time.perf_counter() - t0) * 1000
        return r
    setattr(mod, name, g)

for n in ("embed_query", "_call_reranker", "_substring_recall", "_pick_latest", "page_snippet"):
    wrap(R, n)
for n in ("title_key", "block_sim"):
    wrap(D, n)
# FTS / 向量 / 物化 通过包装 table.search 与 to_arrow 计时
_orig_search = t.search
def search_timed(*a, **k):
    qtype = k.get("query_type", "vector" if a and isinstance(a[0], list) else "fts")
    t0 = time.perf_counter(); r = _orig_search(*a, **k); dt = (time.perf_counter() - t0) * 1000
    ACC[f"lance.{qtype}"] = ACC.get(f"lance.{qtype}", 0.0) + dt
    return r

QUERIES = ["TPS55289RYQR Output current limit", "QMC6309 供电电压 VDD 范围",
           "MSM8916 VDD_APC 绝对最大值", "CH592 BLE 发送功率电流", "ina226 分流电阻"]

print("--- 单次 search() 阶段分解(5 条查询各一次,取均值) ---")
rows = []
for q in QUERIES:
    ACC.clear()
    gen = t.to_arrow
    def ta_timed(*a, **k):
        t0 = time.perf_counter(); r = gen(*a, **k)
        ACC["to_arrow"] = ACC.get("to_arrow", 0.0) + (time.perf_counter() - t0) * 1000
        return r
    t.to_arrow = ta_timed
    try:
        t0 = time.perf_counter()
        R.search(t, q, top_k=5)
        total = (time.perf_counter() - t0) * 1000
    finally:
        t.to_arrow = gen
    rows.append((q, total, dict(ACC)))

keys = ["embed_query", "_call_reranker", "_substring_recall", "_pick_latest",
        "page_snippet", "lance.fts", "lance.vector", "to_arrow", "block_sim", "title_key"]
print(f"{'查询':<32} {'total':>7} " + " ".join(f"{k.split('.')[-1][:9]:>10}" for k in keys))
for q, total, acc in rows:
    print(f"{q[:30]:<32} {total:>7.0f} " + " ".join(f"{acc.get(k, 0.0):>10.0f}" for k in keys))
avg = {k: statistics.mean(r[2].get(k, 0.0) for r in rows) for k in keys}
tot = statistics.mean(r[1] for r in rows)
covered = sum(avg.values())
print("-" * 130)
print(f"{'均值':<32} {tot:>7.0f} " + " ".join(f"{avg[k]:>10.0f}" for k in keys))
print(f"\n  已覆盖阶段合计 {covered:.0f} ms / 总 {tot:.0f} ms -> 未归因 {tot-covered:.0f} ms")
print()

# ---------- 内存: 各操作的增量 ----------
print("--- 内存增量(执行后 RSS 变化) ---")
def delta(label, fn):
    gc.collect(); m0 = rss()[0]
    r = fn()
    m1, pk1 = rss()
    print(f"  {label:<40} RSS {m0:>6.0f} -> {m1:>6.0f} MB  (+{m1-m0:>5.0f})  进程峰值 {pk1:>6.0f}")
    return r

full = delta("table.to_arrow() 全表(含 768 维向量)", lambda: t.to_arrow())
proj = delta("table.to_arrow().select(投影列)", lambda: t.to_arrow().select(R._PROJ_COLS))
del proj
txt  = delta("仅取 text 列(搜索用)", lambda: t.to_arrow().select(["text"]).to_pylist())
delta("完整一次 search()", lambda: R.search(t, QUERIES[0], top_k=5))
print()

# ---------- 并发 ----------
print("--- 并发压力 ---")
for nthread in (1, 4, 8):
    lat, errs = [], []
    def worker(qq, n=2):
        for _ in range(n):
            try:
                t0 = time.perf_counter(); R.search(t, qq, top_k=5)
                lat.append((time.perf_counter() - t0) * 1000)
            except Exception as e:
                errs.append(f"{type(e).__name__}: {e}")
    gc.collect(); m0 = rss()[0]
    ths = [threading.Thread(target=worker, args=(QUERIES[i % len(QUERIES)],)) for i in range(nthread)]
    t0 = time.perf_counter()
    for th in ths: th.start()
    for th in ths: th.join()
    wall = time.perf_counter() - t0
    m1, pk1 = rss()
    cnt = nthread * 2
    print(f"  {nthread} 线程 x2 次: 墙钟 {wall:>5.1f}s  {cnt/wall:>5.2f} q/s  "
          f"中位 {statistics.median(lat):>5.0f} ms  P95 {sorted(lat)[int(len(lat)*0.95)-1]:>5.0f} ms  "
          f"RSS {m0:.0f}->{m1:.0f}MB 峰值{pk1:.0f}MB  错误 {len(errs)}")
    if errs:
        print(f"      {errs[:2]}")
