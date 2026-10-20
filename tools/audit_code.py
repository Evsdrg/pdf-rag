# -*- coding: utf-8 -*-
"""代码体检:用 AST 客观统计函数长度、嵌套深度、魔法数字、elif 链长度。

只看事实,不凭感觉 —— 先量出问题在哪,再决定改哪里。
"""
import ast
import pathlib
import sys

TARGETS = ["backend/retrieval.py", "backend/ingest.py", "backend/main.py",
           "backend/doc_utils.py", "server.py", "ocr_service.py", "run_backend.py",
           "backend/config.py", "eval_retrieval.py"]

# 允许出现的数字(0/1/2 这类结构性例外由阈值控制,不逐个人工豁免)
MAGIC_ALLOW = {0, 1, 2, 1.0, 0.0, 100, -1}


class FuncInfo(ast.NodeVisitor):
    def __init__(self, src_lines):
        self.src = src_lines
        self.funcs = []
        self.magic = []
        self.elif_chains = []

    def visit_FunctionDef(self, node):
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_func(node)

    def _visit_func(self, node):
        end = getattr(node, "end_lineno", node.lineno)
        depth = self._max_depth(node)
        # elif 链长度
        longest = 0
        for n in ast.walk(node):
            if isinstance(n, ast.If):
                cnt, cur = 1, n
                while len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If):
                    cnt += 1
                    cur = cur.orelse[0]
                longest = max(longest, cnt)
        self.funcs.append({
            "name": node.name, "line": node.lineno, "end": end,
            "len": end - node.lineno + 1, "depth": depth, "elif": longest,
        })
        for n in ast.walk(node):
            if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) \
                    and not isinstance(n.value, bool) and n.value not in MAGIC_ALLOW:
                self.magic.append((node.name, n.lineno, n.value,
                                   self.src[n.lineno - 1].strip()[:70]))
        self.generic_visit(node)

    def _max_depth(self, node, d=0):
        """统计控制流嵌套深度(不含函数定义本身)"""
        best = d
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With,
                                  ast.AsyncFor, ast.AsyncWith)):
                best = max(best, self._max_depth(child, d + 1))
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            else:
                best = max(best, self._max_depth(child, d))
        return best

    def visit_Module(self, node):
        self.generic_visit(node)


print(f"{'文件':<26} {'函数':<28} {'行数':>5} {'嵌套':>5} {'elif':>5}  {'魔数':>5}")
print("-" * 90)
allissues = []
for t in TARGETS:
    p = pathlib.Path(t)
    if not p.is_file():
        continue
    src = p.read_text(encoding="utf-8").splitlines()
    tree = ast.parse("\n".join(src))
    v = FuncInfo(src)
    v.visit(tree)
    for f in sorted(v.funcs, key=lambda x: -x["len"]):
        flags = []
        if f["len"] > 60:
            flags.append(f"长{f['len']}")
        if f["depth"] > 4:
            flags.append(f"嵌套{f['depth']}")
        if f["elif"] > 4:
            flags.append(f"elif{f['elif']}")
        if flags:
            allissues.append((t, f, flags))
    # 只打印有问题的 + 各文件最大的
    for f in sorted(v.funcs, key=lambda x: -x["len"])[:3]:
        m = sum(1 for x in v.magic if x[0] == f["name"])
        print(f"{t:<26} {f['name'][:26]:<28} {f['len']:>5} {f['depth']:>5} {f['elif']:>5}  {m:>5}")
    n_magic = len(v.magic)
    if n_magic:
        print(f"{'':<26} ↑ 全文件魔法数字 {n_magic} 处")

print()
print("=== 超出阈值的函数(长>60 / 嵌套>4 / elif>4)===")
for t, f, flags in allissues:
    print(f"  {t:<24} {f['name']:<28} L{f['line']}-{f['end']:<5} {', '.join(flags)}")
if not allissues:
    print("  (无)")

print()
print("=== 全部魔法数字(按文件)===")
total = 0
for t in TARGETS:
    p = pathlib.Path(t)
    if not p.is_file():
        continue
    src = p.read_text(encoding="utf-8").splitlines()
    v = FuncInfo(src)
    v.visit(ast.parse("\n".join(src)))
    if v.magic:
        print(f"\n--- {t} ({len(v.magic)} 处) ---")
        seen = set()
        for fn, ln, val, line in v.magic:
            key = (val, line)
            if key in seen:
                continue
            seen.add(key)
            print(f"    L{ln:<5} {str(val):<10} {line}")
        total += len(v.magic)
print(f"\n合计 {total} 处")
