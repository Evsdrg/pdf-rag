"""MCP/REST 的关键读取、错误和图片链路;使用隔离文档夹具。"""
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

from backend import agent_api, agent_routes, config, doc_utils
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

    def test_page_reference_and_safe_errors(self):
        data = self.client.get("/api/v2/page", params={"file": "guide.md", "page": 2}).json()
        self.assertEqual(data["schema_version"], 2)
        self.assertEqual((data["page"], data["page_basis"], data["total_pages"]), (2, "h1_section", 2))
        self.assertIn("Beta", data["text"])
        result = self.client.get("/api/v2/page", params={"file": "guide.md", "page": 99})
        self.assertEqual(result.json()["error"]["code"], "PAGE_OUT_OF_RANGE")
        for file in ("missing.pdf", "../outside.pdf"):
            result, status = agent_api.invoke(agent_api.read_page, file, 1)
            self.assertEqual(status, 404)
            self.assertEqual(result["error"]["code"], "FILE_NOT_FOUND")

    def test_mcp_single_payload_and_error_flag(self):
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

    def test_ocr_fallback_and_bad_documents(self):
        with fitz.open() as doc:
            doc.new_page().insert_text((70, 100), "Native text")
            with override_config(ocr_smart_filter=False, ocr_min_chars=200):
                with patch("backend.ocr.ocr_image", return_value=("", "secret request detail")):
                    result = doc_utils.read_page_content(doc, 1)
        self.assertIn("Native text", result["text"])
        self.assertEqual(result["warnings"][0]["code"], "OCR_FAILED")
        self.assertNotIn("secret request detail", json.dumps(result))
        (self.root / "bad.pdf").write_bytes(b"not a PDF")
        with fitz.open() as doc:
            doc.new_page()
            doc.save(self.root / "locked.pdf", encryption=fitz.PDF_ENCRYPT_AES_256,
                     owner_pw="test-owner", user_pw="test-reader")
        for file, code in (("bad.pdf", "DOCUMENT_UNREADABLE"), ("locked.pdf", "DOCUMENT_ENCRYPTED")):
            for path in ("/api/v2/page", "/api/v2/render"):
                result = self.client.get(path, params={"file": file, "page": 1})
                self.assertEqual(result.json()["error"]["code"], code)
                self.assertNotIn(str(self.root), result.text)

    def test_status_distinguishes_source_and_index(self):
        (self.root / "unindexed.PDF").write_bytes(b"source file only")
        (self.root / "notes.txt").write_text("not a manual")
        files = [{"file": "guide.md", "kind": "md", "chunks": 2, "category": "docs"},
                 {"file": "missing.pdf", "kind": "pdf", "chunks": 1, "category": "docs"}]
        with patch("backend.agent_api.library.get_table", return_value=object()), \
             patch("backend.agent_api.library.files_index", return_value=files), \
             patch.object(config, "DB_PATH", str(self.root / "index.lance")):
            data = agent_api.status()
        self.assertEqual((data["source_files"], data["indexed_files"], data["unindexed_files"]), (2, 2, 1))
        self.assertEqual(data["missing_source_files"], 1)
        self.assertEqual(data["source_by_kind"], {"pdf": 1, "md": 1})
        self.assertEqual(data["unindexed_examples"], ["unindexed.PDF"])
        self.assertEqual(data["last_ingest_status"], "unknown")
        self.assertEqual(data["source_status"], "ok")

    def test_page_image_native_transport_and_clip_validation(self):
        with fitz.open() as doc:
            page = doc.new_page(width=600, height=800)
            page.draw_rect(fitz.Rect(100, 100, 300, 400), color=(0, 0, 0))
            doc.save(self.root / "chart.pdf")
        result = self.client.get("/api/v2/render", params={"file": "chart.pdf", "page": 1,
                                                          "clip": "[0,0,0.5,0.5]", "max_size": 800})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.headers["content-type"], "image/jpeg")
        self.assertLessEqual(len(result.content), 2_000_000)
        async def run():
            async with Client(server.mcp) as client:
                return await client.call_tool("pdf_rag_render_page", {"file": "chart.pdf", "page": 1})
        result = asyncio.run(run())
        self.assertEqual([item.type for item in result.content], ["text", "image"])
        self.assertNotIn("base64", result.content[0].text)
        self.assertIsNone(result.structured_content)
        result = self.client.get("/api/v2/render", params={"file": "guide.md", "page": 1})
        self.assertEqual(result.json()["error"]["code"], "UNSUPPORTED_FORMAT")


if __name__ == "__main__":
    unittest.main()
