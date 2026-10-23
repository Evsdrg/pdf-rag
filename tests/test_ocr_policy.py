"""OCR 内容筛选的零网络回归:原生稀疏页可免除,不确定与图像/矢量正文保留。"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fitz

from backend import doc_utils, ingest, ocr_policy
from tests.support import override_config


DENSE = ("Normal native document text with enough characters for extraction. " * 7)
SPARSE = "Device ABC123 application guide. Revision 1.2 issued 2026-10-23."


def document(texts):
    doc = fitz.open()
    for text in texts:
        page = doc.new_page(width=600, height=800)
        if text:
            page.insert_textbox(fitz.Rect(50, 160, 550, 700), text, fontsize=11)
    return doc


def image_bytes(color, alpha=255):
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 16, 16), True)
    for y in range(16):
        for x in range(16):
            pix.set_pixel(x, y, (*color, alpha))
    return pix.tobytes("png")


class DocumentPolicyTest(unittest.TestCase):
    def decide(self, doc, number=0):
        return ocr_policy.DocumentPolicy(doc, threshold=200, smart=True).decide(number)

    def test_native_sparse_cover(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            self.assertEqual(self.decide(doc).reason, "native_sparse_cover")

    def test_native_sparse_interior(self):
        with document([DENSE, SPARSE, DENSE, DENSE]) as doc:
            self.assertFalse(self.decide(doc, 1).needs_ocr)

    def test_zero_text_never_filtered(self):
        with document(["", DENSE, DENSE, DENSE]) as doc:
            self.assertEqual(self.decide(doc).reason, "no_text")

    def test_short_document_keeps_ocr(self):
        with document([SPARSE, DENSE, DENSE]) as doc:
            self.assertEqual(self.decide(doc).reason, "document_low_text")

    def test_high_ratio_keeps_ocr(self):
        with document([SPARSE] * 3 + [DENSE]) as doc:
            self.assertEqual(self.decide(doc).reason, "document_low_text")

    def test_consecutive_run_keeps_ocr(self):
        with document([SPARSE] * 4 + [DENSE] * 5) as doc:
            policy = ocr_policy.DocumentPolicy(doc, threshold=200, smart=True)
            self.assertEqual(policy.run_lengths[:4], [4] * 4)
            self.assertEqual(policy.decide(1).reason, "consecutive_low_text")

    def test_sufficient_text_and_exact_threshold(self):
        with document([DENSE] * 4) as doc:
            threshold = len(doc[0].get_text("text").strip())
            policy = ocr_policy.DocumentPolicy(doc, threshold=threshold, smart=True)
            self.assertEqual(policy.decide(0).reason, "sufficient_text")
            self.assertEqual(ocr_policy.DocumentPolicy(doc, threshold=0).decide(0).reason,
                             "sufficient_text")

    def test_legacy_switch(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            policy = ocr_policy.DocumentPolicy(doc, threshold=200, smart=False)
            self.assertEqual(policy.decide(0).reason, "legacy_threshold")

    def test_only_edge_text_keeps_ocr(self):
        with document(["", DENSE, DENSE, DENSE]) as doc:
            doc[0].insert_text((40, 40), SPARSE, fontsize=9)
            self.assertEqual(self.decide(doc).reason, "edge_text_only")

    def test_nonrepeated_image_keeps_ocr_even_when_small(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            doc[0].insert_image(fitz.Rect(50, 200, 80, 230), stream=image_bytes((0, 0, 0)))
            self.assertEqual(self.decide(doc).reason, "content_image")

    def test_repeated_dark_center_image_is_not_decoration(self):
        with document([SPARSE, DENSE, DENSE, DENSE, DENSE]) as doc:
            stream = image_bytes((0, 0, 0))
            for page in doc:
                page.insert_image(fitz.Rect(150, 250, 450, 550), stream=stream)
            self.assertEqual(self.decide(doc).reason, "content_image")

    def test_repeated_border_logo(self):
        with document([SPARSE, DENSE, DENSE, DENSE, DENSE]) as doc:
            stream = image_bytes((0, 0, 0))
            for page in doc:
                page.insert_image(fitz.Rect(50, 20, 100, 70), stream=stream)
            self.assertFalse(self.decide(doc).needs_ocr)

    def test_pale_masked_repeated_watermark(self):
        with document([DENSE, SPARSE, DENSE, DENSE, DENSE]) as doc:
            stream = image_bytes((238, 238, 238), 255)
            # PNG 的 alpha 通道需非恒定,才能生成独立软遮罩。
            pix = fitz.Pixmap(stream)
            pix.set_pixel(0, 0, (0, 0, 0, 0))
            for page in doc:
                page.insert_image(fitz.Rect(120, 200, 480, 560), stream=pix.tobytes("png"))
            policy = ocr_policy.DocumentPolicy(doc, threshold=200, smart=True)
            original = policy._images
            def rotated(number):
                return [dict(im, transform=(100, 100, -100, 100, 120, 200))
                        for im in original(number)]
            with patch.object(policy, "_images", side_effect=rotated):
                self.assertFalse(policy.decide(1).needs_ocr)

    def test_pale_but_unrotated_image_keeps_ocr(self):
        with document([SPARSE, DENSE, DENSE, DENSE, DENSE]) as doc:
            pix = fitz.Pixmap(image_bytes((238, 238, 238)))
            pix.set_pixel(0, 0, (0, 0, 0, 0))
            for page in doc:
                page.insert_image(fitz.Rect(120, 200, 480, 560), stream=pix.tobytes("png"))
            self.assertEqual(self.decide(doc).reason, "content_image")

    def test_watermark_histogram_does_not_drop_tiny_dark_text(self):
        with fitz.open() as doc:
            page = doc.new_page()
            pix = fitz.Pixmap(image_bytes((238, 238, 238)))
            pix.set_pixel(0, 0, (0, 0, 0, 0))
            pix.set_pixel(8, 8, (0, 0, 0, 255))
            page.insert_image(fitz.Rect(20, 20, 300, 300), stream=pix.tobytes("png"))
            self.assertFalse(ocr_policy._pale_masked_image(doc, page.get_images(full=True)[0]))

    def test_simple_table_lines_are_preserved(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            doc[0].draw_rect(fitz.Rect(50, 200, 400, 250), color=(0, 0, 0))
            self.assertFalse(self.decide(doc).needs_ocr)

    def test_filled_header_rule_is_decorative(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            doc[0].draw_rect(fitz.Rect(40, 90, 550, 90.6), fill=(0, 0, 0), color=None)
            self.assertFalse(self.decide(doc).needs_ocr)

    def test_filled_body_shape_keeps_ocr(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            doc[0].draw_rect(fitz.Rect(40, 250, 300, 350), fill=(0, 0, 0), color=None)
            self.assertEqual(self.decide(doc).reason, "complex_vectors")

    def test_curved_vectors_keep_ocr(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            doc[0].draw_circle((200, 300), 40)
            self.assertEqual(self.decide(doc).reason, "complex_vectors")

    def test_many_straight_vectors_keep_ocr(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            for i in range(21):
                doc[0].draw_line((50, 200+i*3), (400, 200+i*3))
            self.assertEqual(self.decide(doc).reason, "complex_vectors")

    def test_diagonal_vector_keeps_ocr(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            doc[0].draw_line((50, 200), (100, 250))
            self.assertEqual(self.decide(doc).reason, "complex_vectors")

    def test_inspection_failure_keeps_ocr(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            policy = ocr_policy.DocumentPolicy(doc, threshold=200, smart=True)
            with patch.object(policy, "_only_decorative_images", side_effect=RuntimeError("bad PDF")):
                self.assertEqual(policy.decide(0).reason, "inspection_failed")

    def test_annotations_keep_ocr(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            doc[0].add_text_annot((250, 250), "Additional content")
            self.assertEqual(self.decide(doc).reason, "annotation")

    def test_same_size_images_are_ambiguous(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            doc[0].insert_image(fitz.Rect(30, 20, 60, 50), stream=image_bytes((0, 0, 0)))
            doc[0].insert_image(fitz.Rect(80, 20, 110, 50), stream=image_bytes((200, 0, 0)))
            self.assertEqual(self.decide(doc).reason, "content_image")

    def test_local_image_inspection_failure_keeps_ocr(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            policy = ocr_policy.DocumentPolicy(doc, threshold=200, smart=True)
            policy._load_resources()
            policy._image_inspection_failed.add(0)
            self.assertTrue(policy.decide(0).needs_ocr)

    def test_empty_document_summary(self):
        with fitz.open() as doc:
            self.assertEqual(ocr_policy.DocumentPolicy(doc, 200, True).summary()["pages"], 0)

    def test_other_page_text_failure_does_not_break_target_page(self):
        class BrokenPage:
            def get_text(self, mode):
                raise RuntimeError("broken text layer")
        with document([SPARSE, DENSE, DENSE, DENSE, DENSE]) as doc:
            pages = [doc[i] for i in range(len(doc))]
            pages[-1] = BrokenPage()
            policy = ocr_policy.DocumentPolicy(pages, 200, True)
            self.assertFalse(policy.decide(0).needs_ocr)
            self.assertEqual(policy.decide(4).reason, "inspection_failed")

    def test_summary(self):
        with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
            s = ocr_policy.DocumentPolicy(doc, threshold=200, smart=True).summary()
            self.assertEqual((s["pages"], s["low_pages"], s["low_ratio"], s["max_low_run"]),
                             (4, 1, .25, 1))


class PolicyIntegrationTest(unittest.TestCase):
    def test_read_page_does_not_call_ocr_for_native_sparse(self):
        with override_config(ocr_smart_filter=True, ocr_min_chars=200):
            with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
                with patch("backend.ocr.ocr_image", side_effect=AssertionError("network forbidden")):
                    text, err = doc_utils.read_page_text(doc, 1)
                self.assertIn("ABC123", text)
                self.assertEqual(err, "")

    def test_read_page_legacy_and_temp_cleanup(self):
        with override_config(ocr_smart_filter=False, ocr_min_chars=200):
            paths = []
            def recognize(path):
                self.assertTrue(os.path.isfile(path))
                paths.append(Path(path))
                return "OCR output " * 30, ""
            with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
                with patch("backend.ocr.ocr_image", side_effect=recognize):
                    text, err = doc_utils.read_page_text(doc, 1)
            self.assertIn("OCR output", text)
            self.assertEqual(err, "")
            self.assertFalse(paths[0].parent.exists())

    def test_read_pages_reuses_document_policy(self):
        from backend import library
        with override_config(ocr_smart_filter=True, ocr_min_chars=200):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "manual.pdf"
                with document([SPARSE, SPARSE, DENSE, DENSE, DENSE]) as doc:
                    doc.save(path)
                with patch("backend.ocr_policy.DocumentPolicy", wraps=ocr_policy.DocumentPolicy) as build:
                    with patch("backend.ocr.ocr_image", side_effect=AssertionError("network forbidden")):
                        result = library.read_pages(tmp, "manual.pdf", "1,2,0,6")
                self.assertEqual(build.call_count, 1)
                self.assertIn("ABC123", result["pages"][0]["text"])
                self.assertIn("ABC123", result["pages"][1]["text"])
                self.assertIn("error", result["pages"][2])

    def test_read_failure_removes_temp_directory(self):
        with override_config(ocr_smart_filter=False, ocr_min_chars=200):
            paths = []
            def fail(path):
                paths.append(Path(path))
                raise RuntimeError("OCR failed")
            with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
                with patch("backend.ocr.ocr_image", side_effect=fail):
                    _, err = doc_utils.read_page_text(doc, 1)
            self.assertIn("OCR failed", err)
            self.assertFalse(paths[0].parent.exists())

    def test_extraction_state_keeps_ocr_counts_and_warnings(self):
        from concurrent.futures import Future
        import time
        result = Future()
        result.set_result(("manual.pdf", "unused", "hash",
                           {"ocr": {"calls": 2, "failed": 1,
                                    "decisions": {"content_image": 2, "native_sparse_page": 1}},
                            "warnings": ["p2 OCR failed"]}, [(SPARSE, 0)]))
        state = {"skipped": []}
        with patch("backend.ingest.ProcessPoolExecutor") as pool:
            pool.return_value.__enter__.return_value.submit.return_value = result
            with patch("backend.ingest.ocr_queue.OCRPool"), patch("backend.ingest.write_state"):
                rows = ingest._extract_phase([("manual.pdf", "unused", "hash")], "unused", state, time.time())
        self.assertEqual(len(rows), 1)
        self.assertEqual(state["ocr"]["calls"], 2)
        self.assertEqual(state["ocr"]["decisions"]["native_sparse_page"], 1)
        self.assertEqual(state["warnings"], ["manual.pdf: p2 OCR failed"])

    def test_ingest_and_read_use_same_decision(self):
        with override_config(ocr_smart_filter=True, ocr_min_chars=200):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "manual.pdf"
                with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
                    doc.save(path)
                with patch("backend.ingest.ocr_page", side_effect=AssertionError("network forbidden")):
                    meta, chunks = ingest.extract_chunks(str(path), "manual.pdf", "", tmp)
                self.assertEqual(meta["ocr"]["calls"], 0)
                self.assertEqual(meta["ocr"]["decisions"]["native_sparse_cover"], 1)
                self.assertTrue(any("ABC123" in text for text, _ in chunks))

    def test_ingest_keeps_image_page(self):
        with override_config(ocr_smart_filter=True, ocr_min_chars=200):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "manual.pdf"
                with document([SPARSE, DENSE, DENSE, DENSE]) as doc:
                    doc[0].insert_image(fitz.Rect(50, 200, 350, 500), stream=image_bytes((0, 0, 0)))
                    doc.save(path)
                with patch("backend.ingest.ocr_page", return_value=("Recovered image text " * 20, "")) as call:
                    meta, chunks = ingest.extract_chunks(str(path), "manual.pdf", "", tmp)
                self.assertEqual(call.call_count, 1)
                self.assertEqual(meta["ocr"]["calls"], 1)
                self.assertTrue(any("Recovered" in text for text, _ in chunks))


if __name__ == "__main__":
    unittest.main()
