# -*- coding: utf-8 -*-
"""文档体检:Markdown 相对链接可解析 + 已跟踪文件不含敏感信息。仅用标准库。

CI 与本地均可运行:`python tools/check_docs.py`。
- 链接检查覆盖 git 跟踪的所有 .md;外链(http/https/mailto)不访问网络,只跳过。
- 敏感信息扫描同样只看 git 跟踪的文本文件;二进制(含 \0)跳过。
  规则偏保守(只匹配确定形态),命中即失败;新形态在 PATTERNS 里补充。
"""
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

# 确定形态的敏感内容:内网地址、本机路径、已知账号、密钥材料。
# 保守优先:宁可漏掉新形态,也不对正常文档误报。
PATTERNS = {
    "private_network": r"\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+"
                       r"|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b",
    "known_internal": r"Include946710|evsdrg@|sudo\s*密码|aosc-usb"
                      r"|/vol2/|/opt/helloworld|/home/cepvor",
    "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "provider_token": r"\b(?:sk|gh[pousr])-[A-Za-z0-9_-]{16,}",
    "literal_credential": r"(?i)(?:api[_-]?key|admin_token|password|passwd|secret)"
                          r"\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']",
}

_EXTERNAL = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def tracked(suffix: str = "") -> list[str]:
    cmd = ["git", "ls-files", "-z"]
    if suffix:
        cmd.append(f"*{suffix}")
    return [p for p in subprocess.check_output(cmd, text=True).split("\0") if p]


def is_text(path) -> bool:
    return b"\0" not in path.read_bytes()


def check_links() -> list[str]:
    problems = []
    for rel in tracked(".md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip().split("#", 1)[0].strip("<>")
            if not target or _EXTERNAL.match(target):
                continue
            dest = (ROOT / rel).parent / urllib.parse.unquote(target)
            if not dest.exists():
                problems.append(f"链接失效: {rel} -> {target}")
    return problems


def check_secrets() -> list[str]:
    problems = []
    for rel in tracked():
        path = ROOT / rel
        if not path.is_file() or not is_text(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for kind, pattern in PATTERNS.items():
            for match in re.finditer(pattern, text, re.I):
                line = text.count("\n", 0, match.start()) + 1
                problems.append(f"疑似敏感信息({kind}): {rel}:{line}")
    return problems


ROOT = None


def main() -> int:
    global ROOT
    ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                               text=True, check=True).stdout.strip())
    problems = check_links() + check_secrets()
    if problems:
        for p in problems:
            print(f"  - {p}")
        print(f"\n共 {len(problems)} 处问题")
        return 1
    print("PASS: 文档链接全部可解析;未在跟踪文件中发现敏感信息。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
