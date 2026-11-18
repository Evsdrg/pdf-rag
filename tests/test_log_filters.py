"""TLS 探活告警去噪:只丢固定消息,不影响其他日志与请求处理。"""
import logging
import unittest

from backend import log_filters


class ProbeFilterTest(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test.uvicorn.error")
        self.logger.handlers[:] = []
        self.logger.filters[:] = []
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)
        self.records = []

        class Collect(logging.Handler):
            def __init__(self, sink):
                super().__init__()
                self.sink = sink

            def emit(self, record):
                self.sink.append(record.getMessage())

        self.logger.addHandler(Collect(self.records))

    def test_only_probe_warning_is_dropped(self):
        log_filters.install_probe_filter(self.logger)
        self.logger.warning(log_filters.PROBE_WARNING)
        self.logger.warning("Invalid HTTP request received. retry=1")
        self.logger.warning("GET /mcp/ HTTP/1.1 405 Method Not Allowed")
        self.logger.error("ASGI application failed")
        self.assertEqual(self.records, [
            "Invalid HTTP request received. retry=1",
            "GET /mcp/ HTTP/1.1 405 Method Not Allowed",
            "ASGI application failed",
        ])

    def test_install_is_idempotent(self):
        log_filters.install_probe_filter(self.logger)
        log_filters.install_probe_filter(self.logger)
        filters = [item for item in self.logger.filters
                   if isinstance(item, log_filters._DropProbeWarnings)]
        self.assertEqual(len(filters), 1)

    def test_importing_app_installs_filter_on_uvicorn(self):
        # main 模块导入时应已挂到 uvicorn.error 上;这里只校验存在性,不重复导入。
        from backend import main  # noqa: F401
        target = logging.getLogger("uvicorn.error")
        self.assertTrue(any(isinstance(item, log_filters._DropProbeWarnings)
                            for item in target.filters))


if __name__ == "__main__":
    unittest.main()
