"""关键文档契约：端点清单与配置数量不能脱离实现。"""
import asyncio
import unittest
from pathlib import Path

from fastmcp import Client

from backend import config
from backend.main import app
import server


ROOT = Path(__file__).resolve().parents[1]


class DocumentationContractTest(unittest.TestCase):
    def test_http_reference_covers_every_registered_api_path(self):
        text = (ROOT / "docs" / "HTTP-API.md").read_text(encoding="utf-8")
        missing = [path for path in app.openapi()["paths"] if path not in text]
        self.assertEqual(missing, [])

    def test_configuration_count_matches_registry(self):
        text = (ROOT / "docs" / "CONFIGURATION.md").read_text(encoding="utf-8")
        self.assertIn(f"{len(config.SPECS)} 项可调参数 / {len(config.GROUPS)} 个后端分组", text)

    def test_mcp_documentation_covers_new_tools(self):
        text = (ROOT / "DEPLOY.md").read_text(encoding="utf-8")
        async def count_tools():
            async with Client(server.mcp) as client:
                return len(await client.list_tools())
        self.assertIn(f"系统提供 {asyncio.run(count_tools())} 个 `pdf_rag_*` 工具", text)
        for name in ("pdf_rag_read_section", "pdf_rag_render_page"):
            self.assertIn(name, (ROOT / "docs" / "HTTP-API.md").read_text(encoding="utf-8")
                          + (ROOT / "docs" / "MCP-PROTOCOL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
