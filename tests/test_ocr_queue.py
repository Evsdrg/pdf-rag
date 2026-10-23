"""OCR 队列与跨进程提取回归。所有识别均为进程内替身,不会调用上游。"""
import multiprocessing
import os
from pathlib import Path
import queue
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import fitz

from backend import config, ingest, ocr, ocr_queue
from tests.support import override_config


NATIVE = "Native paragraph for deterministic page ordering and fallback. "


def make_pdf(path, pages=8):
    with fitz.open() as doc:
        for number in range(pages):
            page = doc.new_page(width=300, height=400)
            page.insert_textbox(fitz.Rect(25, 80, 275, 250), f"Page {number + 1}. {NATIVE}", fontsize=10)
            page.draw_rect(fitz.Rect(25, 200, 260, 230), color=(0, 0, 0))
        doc.save(path)


class QueueTest(unittest.TestCase):
    def test_capacity_is_acquired_before_render_and_results_can_arrive_out_of_order(self):
        capacity = threading.BoundedSemaphore(2)
        stopped = threading.Event()
        requests, responses = queue.Queue(), queue.Queue()
        producer = ocr_queue.Producer(requests, responses, capacity, stopped, 0)
        with tempfile.TemporaryDirectory() as tmp:
            def render(name):
                path = Path(tmp) / name
                path.write_text("image")
                return str(path)
            first = producer.submit(lambda: render("first"))
            second = producer.submit(lambda: render("second"))
            started = threading.Event()
            def third():
                producer.submit(lambda: (started.set(), render("third"))[1])
            thread = threading.Thread(target=third)
            thread.start()
            self.assertFalse(started.wait(.1))
            capacity.release()
            self.assertTrue(started.wait(2))
            thread.join()
            responses.put((second, "second", ""))
            responses.put((first, "first", ""))
            self.assertEqual(producer.receive(first), ("first", ""))
            self.assertEqual(producer.receive(second), ("second", ""))

    def test_render_failure_releases_capacity(self):
        capacity = threading.BoundedSemaphore(1)
        producer = ocr_queue.Producer(queue.Queue(), queue.Queue(), capacity, threading.Event(), 0)
        with self.assertRaisesRegex(RuntimeError, "render failed"):
            producer.submit(lambda: (_ for _ in ()).throw(RuntimeError("render failed")))
        self.assertTrue(capacity.acquire(blocking=False))

    def test_stopped_queue_does_not_start_render(self):
        stopped = threading.Event(); stopped.set()
        producer = ocr_queue.Producer(queue.Queue(), queue.Queue(), threading.BoundedSemaphore(1), stopped, 0)
        with self.assertRaisesRegex(RuntimeError, "已停止"):
            producer.submit(lambda: self.fail("render should not start"))

    def test_client_is_reused_and_closed_and_images_deleted(self):
        context = multiprocessing.get_context("spawn")
        paths = []
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(3):
                path = Path(tmp) / f"page{i}.png"; path.write_bytes(b"image"); paths.append(path)
            with patch("backend.ocr_queue.httpx.Client") as client:
                with patch("backend.ocr_queue.ocr.ocr_image", return_value=("recognized", "")) as recognize:
                    with ocr_queue.OCRPool(context, 1, 1) as pool:
                        producer = ocr_queue.Producer(pool.requests, pool.responses[0],
                                                      pool.capacity, pool.stopped, 0)
                        tasks = [producer.submit(lambda p=p: str(p)) for p in paths]
                        self.assertEqual([producer.receive(t) for t in tasks], [("recognized", "")] * 3)
                self.assertEqual(client.call_count, 1)
                self.assertEqual(client.return_value.close.call_count, 1)
                self.assertTrue(all(call.kwargs["client"] is client.return_value for call in recognize.call_args_list))
            self.assertTrue(all(not p.exists() for p in paths))

    def test_http_ocr_can_use_supplied_client_without_network(self):
        with override_config(ocr_backend="local"):
            with patch("backend.ocr.httpx.post", side_effect=AssertionError("network forbidden")):
                from unittest.mock import Mock
                client = Mock()
                client.post.return_value.json.return_value = {"text": "recognized"}
                self.assertEqual(ocr.ocr_image("unused.png", client=client), ("recognized", ""))
                self.assertEqual(client.post.call_count, 1)


class ExtractionParallelTest(unittest.TestCase):
    def test_one_document_uses_multiple_ocr_lanes_and_matches_serial_output(self):
        with override_config(extract_workers=1, ocr_workers=4, ocr_smart_filter=False, ocr_dpi=72):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "manual.pdf"; make_pdf(path)
                long_text = "Recognized image paragraph with deterministic contents. " * 8
                def serial_ocr(page, _):
                    return f"Physical page {page.number + 1}. {long_text}", ""
                with patch("backend.ingest.ocr_page", side_effect=serial_ocr):
                    serial = ingest.extract_chunks(str(path), "manual.pdf", "", tmp)[1]
                lock = threading.Lock()
                active = peak = 0
                def recognize(path, **_):
                    nonlocal active, peak
                    self.assertTrue(os.path.isfile(path))
                    with lock:
                        active += 1; peak = max(peak, active)
                    time.sleep(.04 * (4 - int(Path(path).stem.split('p')[-1]) % 4))
                    with lock: active -= 1
                    number = int(Path(path).stem.split('p')[-1])
                    return f"Physical page {number + 1}. {long_text}", ""
                state = {"errors": [], "skipped": []}
                with patch("backend.ocr_queue.ocr.ocr_image", side_effect=recognize):
                    with patch("backend.ingest.write_state"):
                        result = ingest._extract_phase([("manual.pdf", str(path), "hash")], tmp, state, time.time())
                self.assertGreater(peak, 1)
                self.assertLessEqual(peak, 4)
                self.assertEqual(result[0][4], serial)
                self.assertEqual(state["ocr"]["calls"], 8)
                self.assertEqual(state["ocr"]["failed"], 0)
                self.assertEqual(state["concurrency"], {"extract_workers": 1, "ocr_workers": 4})

    def test_multiple_documents_share_global_limit_and_page_failures_do_not_abort(self):
        with override_config(extract_workers=2, ocr_workers=2, ocr_smart_filter=False, ocr_dpi=72):
            with tempfile.TemporaryDirectory() as tmp:
                paths = [Path(tmp) / name for name in ["a.pdf", "b.pdf"]]
                for path in paths: make_pdf(path, 4)
                lock = threading.Lock(); active = peak = 0
                def recognize(path, **_):
                    nonlocal active, peak
                    with lock:
                        active += 1; peak = max(peak, active)
                    time.sleep(.06)
                    with lock: active -= 1
                    if Path(path).stem == "ocr_p1":
                        raise RuntimeError("page failure")
                    return "Recovered image text. " * 15, ""
                state = {"errors": [], "skipped": []}
                with patch("backend.ocr_queue.ocr.ocr_image", side_effect=recognize):
                    with patch("backend.ingest.write_state"):
                        result = ingest._extract_phase([(p.name, str(p), "hash") for p in paths], tmp, state, time.time())
                self.assertEqual(len(result), 2)
                self.assertEqual(peak, 2)
                self.assertEqual(state["ocr"]["calls"], 8)
                self.assertEqual(state["ocr"]["failed"], 2)
                for item in result:
                    chunks = item[4]
                    self.assertTrue(any("Native paragraph" in text for text, number in chunks if number == 1))
                    self.assertEqual([p for _, p in chunks], sorted(p for _, p in chunks))

    def test_invalid_file_isolated_and_no_ocr_for_markdown(self):
        with override_config(extract_workers=2, ocr_workers=1):
            with tempfile.TemporaryDirectory() as tmp:
                md = Path(tmp) / "manual.md"; md.write_text("# Heading\n\nNative markdown body")
                bad = Path(tmp) / "broken.pdf"; bad.write_bytes(b"not a PDF")
                state = {"errors": [], "skipped": []}
                with patch("backend.ocr_queue.ocr.ocr_image", side_effect=AssertionError("network forbidden")):
                    with patch("backend.ingest.write_state"):
                        result = ingest._extract_phase([(p.name, str(p), "hash") for p in [md, bad]], tmp, state, time.time())
                self.assertEqual(len(result), 1)
                self.assertIn("broken.pdf", state["errors"][0])
                self.assertEqual(state["extract"]["done"], 2)

    def test_concurrency_config_is_exposed_and_validated(self):
        specs = config.snapshot()
        self.assertEqual(specs["ocr_workers"]["default"], 4)
        self.assertEqual(specs["ocr_workers"]["group"], "索引吞吐")
        self.assertEqual(specs["extract_workers"]["hi"], 32)
        for name in ["ocr_workers", "extract_workers"]:
            self.assertEqual(config.SPECS[name].coerce(32), 32)
            for value in [0, 33]:
                with self.assertRaises(ValueError): config.SPECS[name].coerce(value)


if __name__ == "__main__":
    unittest.main()
