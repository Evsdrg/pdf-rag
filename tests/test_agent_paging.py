"""有界列表、章节和跨页续读的离线回归。"""
import json
import socket
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import fitz

from backend import agent_api, agent_documents, agent_paging, config, library
from tests.support import override_config


class PagingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for target, value in (("PDF_ROOT", str(self.root)),):
            patcher = patch.object(config, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(socket.socket, "connect", side_effect=AssertionError("network forbidden"))
        patcher.start()
        self.addCleanup(patcher.stop)
        agent_documents.clear_cache()
        self.addCleanup(agent_documents.clear_cache)

    def write(self, text):
        (self.root / "guide.md").write_text(text, encoding="utf-8")

    def test_files_pagination_no_duplicates_and_filters(self):
        files = [{"file": f"category/{i:03d}.pdf", "category": "category", "model_no": "ABC123",
                  "kind": "pdf", "pages": 3, "chunks": 5} for i in range(328)]
        table = SimpleNamespace(version=7)
        with patch.object(library, "get_table", return_value=table), patch.object(library, "files_index", return_value=files):
            cursor, out = "", []
            while True:
                result = agent_api.list_files(model_no="abc", limit=30, cursor=cursor)
                self.assertLessEqual(agent_paging.json_size(result), agent_paging.MAX_RESPONSE_BYTES)
                out += result["files"]
                cursor = result["next_cursor"]
                if not cursor:
                    break
            self.assertEqual(out, [{**f, "pages_basis": "indexed_max_page"} for f in files])
            self.assertEqual(agent_api.list_files(kind="md")["files"], [])

    def test_cursor_binds_filter_and_version(self):
        values = [{"file": str(i), "category": "cat", "model_no": "A", "kind": "pdf"} for i in range(3)]
        table = SimpleNamespace(version=1)
        with patch.object(library, "get_table", return_value=table), patch.object(library, "files_index", return_value=values):
            cursor = agent_api.list_files(limit=1)["next_cursor"]
            self.assertEqual(agent_api.invoke(agent_api.list_files, kind="pdf", cursor=cursor)[0]["error"]["code"], "INVALID_CURSOR")
            table.version = 2
            self.assertEqual(agent_api.invoke(agent_api.list_files, cursor=cursor)[0]["error"]["code"], "STALE_CURSOR")

    def test_read_large_markdown_complete_across_cursors(self):
        text = "# MQTT\n" + ("电气参数和 AT+QMTCONN 说明\\\"\n" * 3000)
        self.write(text)
        out, cursor = "", ""
        while True:
            result = agent_api.read_page("guide.md", 1, max_chars=12000, cursor=cursor)
            self.assertLessEqual(agent_paging.json_size(result), agent_paging.MAX_RESPONSE_BYTES)
            out += result["text"]
            cursor = result["next_cursor"]
            if not cursor:
                break
        self.assertEqual(out, text.strip())

    def test_multi_page_budget_and_resume_exactly(self):
        self.write("# One\n" + "a" * 600 + "\n# Two\n" + "b" * 600)
        all_text = {1: "", 2: ""}
        cursor = ""
        while True:
            result = agent_api.read_pages("guide.md", "1,3,2", 256, cursor)
            self.assertLessEqual(sum(len(p.get("text", "")) for p in result["pages"]), 256)
            for page in result["pages"]:
                if "text" in page:
                    all_text[page["page"]] += page["text"]
            cursor = result["next_cursor"]
            if not cursor:
                break
        self.assertEqual(all_text[1], "# One\n" + "a" * 600)
        self.assertEqual(all_text[2], "# Two\n" + "b" * 600)

    def test_outline_depth_and_duplicate_titles(self):
        self.write("# Commands\n## Same\nAlpha\n### Details\nDetail\n## Same\nBeta\n")
        outline = agent_api.get_outline("guide.md")
        self.assertEqual(len(outline["outline"]), 3)
        first, second = [e for e in outline["outline"] if e["title"] == "Same"]
        self.assertNotEqual(first["section_id"], second["section_id"])
        section = agent_api.read_section("guide.md", first["section_id"])
        body = "".join(p["text"] for p in section["pages"])
        self.assertIn("Alpha", body)
        self.assertIn("Details", body)
        self.assertNotIn("Beta", body)

    def test_document_change_invalidates_cursor_and_section(self):
        self.write("# One\n" + "a" * 1000)
        cursor = agent_api.read_page("guide.md", 1, 256)["next_cursor"]
        section = agent_api.get_outline("guide.md")["outline"][0]["section_id"]
        self.write("# Changed\nNew")
        for func, args in ((agent_api.read_page, ("guide.md", 1, 256, cursor)),
                           (agent_api.read_section, ("guide.md", section))):
            result, _ = agent_api.invoke(func, *args)
            self.assertEqual(result["error"]["code"], "STALE_CURSOR")

    def test_ocr_continuation_reuses_cached_result(self):
        with fitz.open() as doc:
            doc.new_page()
            doc.save(self.root / "scan.pdf")
        with override_config(ocr_smart_filter=False):
            with patch("backend.ocr.ocr_image", return_value=("OCR content " * 500, "")) as recognize:
                cursor = ""
                while True:
                    result = agent_api.read_page("scan.pdf", 1, 256, cursor)
                    self.assertTrue(result["ocr"])
                    cursor = result["next_cursor"]
                    if not cursor:
                        break
        self.assertEqual(recognize.call_count, 1)

    def test_pdf_bookmark_range_and_missing_toc(self):
        with fitz.open() as doc:
            for _ in range(3):
                doc.new_page().insert_text((70, 100), "Native text " * 20)
            doc.set_toc([[1, "First", 1], [1, "Second", 2]])
            doc.save(self.root / "book.pdf")
        with override_config(ocr_min_chars=0):
            outline = agent_api.get_outline("book.pdf")
            data = agent_api.read_section("book.pdf", outline["outline"][0]["section_id"])
        self.assertEqual(data["section_basis"], "bookmark_pages")
        self.assertEqual([p["page"] for p in data["pages"]], [1, 2])

    def test_page_range_checked_before_expansion(self):
        result, _ = agent_api.invoke(agent_api.read_pages, "guide.md", "1-999999999")
        self.assertEqual(result["error"]["code"], "TOO_MANY_PAGES")

    def test_escaped_text_stays_within_wire_budget(self):
        self.write("# Escaped\n" + "\u0001\\\"" * 20000)
        data = agent_api.read_page("guide.md", 1, 12000)
        self.assertLessEqual(len(json.dumps(data, ensure_ascii=False).encode()), agent_paging.MAX_RESPONSE_BYTES)
        self.assertTrue(data["next_cursor"])


if __name__ == "__main__":
    unittest.main()
