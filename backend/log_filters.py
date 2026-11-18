"""TLS 探活导致的无效 HTTP 告警去噪。

飞牛 fnOS 的端口探活会先对每个已发布端口发一个 TLS ClientHello（`0x16 0x03 0x01`
开头），再发明文 `HEAD / HTTP/1.0` 判断存活。pdf-rag 的 8100 是明文 HTTP，TLS 记录
必然被 HTTP 解析器拒绝，uvicorn 对每个连接打一条
`Invalid HTTP request received.` 并返回 400；紧接着的明文 HEAD 仍然 200。实测生产
约每 2 秒一对，日增约 4 万行，日志被噪声淹没。

这里只过滤这一条固定消息：探活本身的 200/400 行为、其他协议告警与访问日志都保持不变。
不把 8100 改成 TLS，也不改任何请求处理路径。
"""
import logging

PROBE_WARNING = "Invalid HTTP request received."


class _DropProbeWarnings(logging.Filter):
    """丢弃 TLS 探活触发的固定告警；其余记录原样放行。"""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().strip() != PROBE_WARNING


_PROBE_FILTER = _DropProbeWarnings()


def install_probe_filter(logger: logging.Logger | None = None) -> logging.Logger:
    """给 uvicorn 协议 logger 挂上去噪过滤器（幂等）。

    只挂到 `uvicorn.error`：协议解析告警用它，应用日志不受影响。重复调用不会重复添加，
    避免热重载或多次导入时过滤器堆积。
    """
    target = logger if logger is not None else logging.getLogger("uvicorn.error")
    if not any(isinstance(item, _DropProbeWarnings) for item in target.filters):
        target.addFilter(_PROBE_FILTER)
    return target
