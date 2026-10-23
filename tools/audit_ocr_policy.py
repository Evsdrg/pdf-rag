"""离线比较 OCR 字数策略与内容筛选,不导入或调用任何模型客户端。"""
import argparse
import json
from collections import Counter
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import fitz

from backend.ocr_policy import DocumentPolicy


def audit_file(path, rel, threshold):
    t0 = time.perf_counter()
    with fitz.open(path) as doc:
        policy = DocumentPolicy(doc, threshold=threshold, smart=True)
        profile_s = time.perf_counter() - t0
        reasons = Counter()
        skipped = []
        candidates = 0
        for number, count in enumerate(policy.counts):
            if count >= threshold:
                continue
            candidates += 1
            decision = policy.decide(number)
            reasons[decision.reason] += 1
            if not decision.needs_ocr:
                skipped.append({"page": number + 1, "chars": count,
                                "reason": decision.reason,
                                "text": policy.texts[number].strip()})
        return {"file": rel, **policy.summary(), "legacy_ocr_pages": candidates,
                "filtered_pages": len(skipped), "ocr_pages": candidates - len(skipped),
                "reasons": dict(reasons), "skipped": skipped,
                "profile_s": round(profile_s, 4),
                "elapsed_s": round(time.perf_counter() - t0, 4)}


def audit(root, threshold=200):
    root = Path(root)
    if not root.is_dir():
        raise ValueError(f"PDF 根目录不存在: {root}")
    results, errors = [], []
    t0 = time.perf_counter()
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() != ".pdf" or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        try:
            results.append(audit_file(path, rel, threshold))
        except Exception as exc:
            errors.append({"file": rel, "error": f"{type(exc).__name__}: {exc}"})
    reasons = Counter()
    for result in results:
        reasons.update(result["reasons"])
    return {"threshold": threshold, "files": len(results),
            "pages": sum(r["pages"] for r in results),
            "legacy_ocr_pages": sum(r["legacy_ocr_pages"] for r in results),
            "filtered_pages": sum(r["filtered_pages"] for r in results),
            "ocr_pages": sum(r["ocr_pages"] for r in results),
            "profile_s": round(sum(r["profile_s"] for r in results), 3),
            "elapsed_s": round(time.perf_counter() - t0, 3),
            "reasons": dict(reasons), "errors": errors, "documents": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--threshold", type=int, default=200)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.threshold < 0:
        parser.error("threshold 不能小于 0")
    result = audit(args.root, args.threshold)
    if args.output:
        with args.output.open("x", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in result.items() if k != "documents"}, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
