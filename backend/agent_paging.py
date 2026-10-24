"""有界输出与无状态游标。游标绑定进程、查询范围和数据版本。"""
import base64
import hashlib
import hmac
import json
import secrets

from .library import LibraryError

MAX_RESPONSE_BYTES = 32_000
_SECRET = secrets.token_bytes(32)


def fingerprint(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()[:24]


def encode_cursor(scope, revision, position) -> str:
    raw = json.dumps({"scope": fingerprint(scope), "revision": revision,
                      "position": position}, separators=(",", ":")).encode()
    signature = hmac.digest(_SECRET, raw, "sha256")
    return base64.urlsafe_b64encode(signature + raw).decode().rstrip("=")


def decode_cursor(cursor: str, scope, revision, default):
    if not cursor:
        return default
    try:
        if len(cursor) > 4096:
            raise ValueError
        decoded = base64.b64decode(cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True)
        signature, raw = decoded[:32], decoded[32:]
        if not hmac.compare_digest(signature, hmac.digest(_SECRET, raw, "sha256")):
            raise ValueError
        value = json.loads(raw)
        if value["scope"] != fingerprint(scope):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        raise LibraryError("游标无效或不属于本次请求,请从首批重新读取", code="INVALID_CURSOR") from None
    if value["revision"] != revision:
        raise LibraryError("数据或提取配置已变化,请从首批重新读取", code="STALE_CURSOR")
    return value["position"]


def json_size(value) -> int:
    return len(json.dumps(value, ensure_ascii=False).encode("utf-8"))


def bounded_items(items: list, key: str, base: dict, scope, revision, limit: int,
                  cursor: str = "") -> dict:
    offset = decode_cursor(cursor, scope, revision, 0)
    if not isinstance(offset, int) or not 0 <= offset <= len(items):
        raise LibraryError("游标位置无效", code="INVALID_CURSOR")
    selected = []
    end = offset
    while end < len(items) and len(selected) < limit:
        selected.append(items[end])
        candidate = {**base, key: selected, "count": len(selected), "total": len(items),
                     "truncated": True, "next_cursor": encode_cursor(scope, revision, end + 1)}
        if json_size(candidate) > MAX_RESPONSE_BYTES:
            selected.pop()
            break
        end += 1
    if end == offset and offset < len(items):
        raise LibraryError("单条记录超过返回大小上限,请缩小查询范围", code="ITEM_TOO_LARGE")
    more = end < len(items)
    return {**base, key: selected, "count": len(selected), "total": len(items),
            "truncated": more,
            "next_cursor": encode_cursor(scope, revision, end) if more else None}
