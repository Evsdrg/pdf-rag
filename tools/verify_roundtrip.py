# -*- coding: utf-8 -*-
"""端到端往返验证:构建 → 预检(含服务配置差异)→ 导入 → 检索。"""
import json
import time
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8100"


def post(path, body=None, timeout=600):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(BASE + path, data=data, method="POST", headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


print("=== 1) 构建数据包(仅索引)===")
t0 = time.time()
r = post("/api/export/bundle?include_docs=false&level=3")
print(f"   {r['bytes'] / 1048576:.0f} MB, {r['documents']} 文档, {r['elapsed']}s")
name = r["path"].replace("\\", "/").rsplit("/", 1)[-1]
print(f"   包名 {name}")

print()
print("=== 2) 导入预检 ===")
i = post("/api/import/inspect", {"name": name})
p = i["provider"]
print(f"   服务配置差异项: {list(p['changed'].keys()) or '无(与本地一致)'}")
print(f"   包内 model = {p['bundle'].get('embed_model')}   base_url = {p['bundle'].get('embed_base_url')}")
print(f"   应用后阻断: {i['blocking_if_apply'] or '无 ✓'}")
print(f"   不应用阻断: {i['blocking_if_keep'] or '无 ✓'}")

print()
print("=== 3) 执行导入 ===")
r = post("/api/import/bundle", {"name": name, "restore_docs": True,
                                "replace_index": True, "apply_provider": True})
print(f"   ok={r['ok']}  PDF 新增 {r['documents_written']} / 跳过 {r['documents_skipped']}")
print(f"   索引替换={r['index_replaced']}  备份={r['index_backup']}")
print(f"   已应用服务配置: {r.get('provider_applied')}")

print()
print("=== 4) 导入后检索 ===")
q = "QMC6309 供电电压"
res = json.loads(urllib.request.urlopen(
    f"{BASE}/api/v2/search?query={urllib.parse.quote(q)}&top_k=2", timeout=120).read())
for h in res["results"]:
    print(f"   p{h['page']} {h['file'].split(chr(92))[-1][:40]}  含2.5={'2.5' in h['snippet']}")
