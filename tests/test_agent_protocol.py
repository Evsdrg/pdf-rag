"""MCP/REST v2 协议和旧 REST 兼容测试;所有文档和表均为隔离夹具。"""
import asyncio
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastmcp import Client

from backend import agent_api, agent_routes, config, doc_utils, library
from tests.support import override_config
import server


class ProtocolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.root_patch = patch.object(config, "PDF_ROOT", str(self.root))
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.network = patch.object(socket.socket, "connect", side_effect=AssertionError("network forbidden"))
        self.network.start()
        self.addCleanup(self.network.stop)
        (self.root / "guide.md").write_text("# Introduction\nAlpha\n# Commands\nBeta", encoding="utf-8")
        app = FastAPI()
        app.include_router(agent_routes.router)
        self.client = TestClient(app)

    def test_page_has_reference_and_basis(self):
        data = self.client.get("/api/v2/page", params={"file": "guide.md", "page": 2}).json()
        self.assertEqual(data["schema_version"], 2)
        self.assertEqual((data["page"], data["page_basis"], data["total_pages"]), (2, "h1_section", 2))
        self.assertIn("Beta", data["text"])
        self.assertFalse(data["ocr"])

    def test_out_of_range_is_structured(self):
        result = self.client.get("/api/v2/page", params={"file": "guide.md", "page": 99})
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.json()["error"]["code"], "PAGE_OUT_OF_RANGE")
        self.assertEqual(result.json()["error"]["details"]["total_pages"], 2)

    def test_partial_pages_keeps_errors_separate_from_text(self):
        data = agent_api.read_pages("guide.md", "1,3,2")
        self.assertEqual([p["page"] for p in data["pages"]], [1, 3, 2])
        self.assertEqual(data["pages"][1]["error"]["code"], "PAGE_OUT_OF_RANGE")
        self.assertNotIn("text", data["pages"][1])

    def test_missing_file_and_traversal(self):
        for file in ("missing.pdf", "../outside.pdf"):
            data, status = agent_api.invoke(agent_api.read_page, file, 1)
            self.assertEqual(status, 404)
            self.assertEqual(data["error"]["code"], "FILE_NOT_FOUND")

    def test_unexpected_error_does_not_expose_secret(self):
        def fail():
            raise RuntimeError("private internal value")
        with self.assertLogs("pdfrag.agent_api", level="ERROR"):
            data, status = agent_api.invoke(fail)
        self.assertEqual(status, 500)
        self.assertNotIn("private internal value", json.dumps(data))

    def test_status_and_lists_do_not_call_upstream(self):
        with patch.object(library, "get_table", return_value=None):
            self.assertFalse(agent_api.status()["indexed"])
            data, _ = agent_api.invoke(agent_api.list_files)
            self.assertEqual(data["error"]["code"], "INDEX_NOT_FOUND")

    def test_ocr_failure_keeps_native_text_and_safe_warning(self):
        with fitz.open() as doc:
            page = doc.new_page()
            page.insert_text((70, 100), "Native text")
            with override_config(ocr_smart_filter=False, ocr_min_chars=200):
                with patch("backend.ocr.ocr_image", return_value=("", "secret request detail")):
                    result = doc_utils.read_page_content(doc, 1)
        self.assertIn("Native text", result["text"])
        self.assertEqual(result["warnings"][0]["code"], "OCR_FAILED")
        self.assertNotIn("secret request detail", json.dumps(result))

    def test_mcp_returns_one_json_text_block_and_error_flag(self):
        async def run():
            async with Client(server.mcp) as client:
                success = await client.call_tool("pdf_rag_read_page", {"file": "guide.md", "page": 1})
                error = await client.call_tool("pdf_rag_read_page", {"file": "missing.pdf", "page": 1}, raise_on_error=False)
                return success, error
        success, error = asyncio.run(run())
        self.assertEqual(len(success.content), 1)
        self.assertIsNone(success.structured_content)
        self.assertEqual(json.loads(success.content[0].text)["file"], "guide.md")
        self.assertTrue(error.is_error)
        self.assertEqual(json.loads(error.content[0].text)["error"]["code"], "FILE_NOT_FOUND")


class LegacyContractTest(unittest.TestCase):
    def test_old_api_shapes_unchanged(self):
        from backend.main import app
        client = TestClient(app)
        with patch("backend.main._table", return_value=None):
            for endpoint in ("/api/files", "/api/categories", "/api/search?q=voltage"):
                self.assertEqual(client.get(endpoint).json(), [])
        with patch.object(config, "PDF_ROOT", tempfile.gettempdir()):
            result = client.get("/api/page", params={"file": "missing-pdfrag.pdf", "page": 1})
        self.assertEqual(result.status_code, 200)
        self.assertIsInstance(result.json()["text"], str)
        self.assertIsInstance(result.json()["ocr"], bool)
        self.assertTrue(result.json()["error"])


if __name__ == "__main__":
    unittest.main()
