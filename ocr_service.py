import gc
import html
import json
import logging
import os
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# 模型缓存重定向到项目内目录:用户主目录下的 .paddlex 曾出现目录损坏
os.environ.setdefault(
    "PADDLE_PDX_CACHE_HOME",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".paddlex_cache"),
)

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "ocr.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO, encoding="utf-8",
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("ocr")

PORT = 8900
# 空闲多久后卸载模型释放显存/内存(环境变量可调,默认 300s)
IDLE_TIMEOUT_SECONDS = int(os.getenv("OCR_IDLE_TIMEOUT_SECONDS", "300"))
# 卸载线程巡检间隔(不可调,固定 30s)
UNLOAD_CHECK_INTERVAL = 30

pipeline = None
lock = threading.Lock()
# PPStructureV3 管线非线程安全:并发 predict 会串批导致 shape 冲突,
# 所有推理调用统一串行化(单机单模型场景,吞吐不受影响)
PIPE_LOCK = threading.Lock()
last_used = 0.0       # 最近一次请求开始时间(time.monotonic)
active_requests = 0   # 正在处理中的请求数


def _touch():
    global last_used
    last_used = time.monotonic()


def ensure_pipeline():
    global pipeline
    if pipeline is None:
        with lock:
            if pipeline is None:
                log.info("初始化 PP-StructureV3 ...")
                from paddleocr import PPStructureV3
                pipeline = PPStructureV3(
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    engine="paddle",
                )
                log.info("PP-StructureV3 就绪")
    return pipeline


def _release_gpu_memory():
    """尽量释放 GPU/CPU 显存缓存(与 paddle 是否可用无关,安全跳过)。"""
    try:
        import paddle
        if paddle.is_compiled_with_cuda():
            paddle.device.cuda.empty_cache()
    except Exception:
        pass


def unload_model():
    """卸载模型:置空引用 + 回收 + 释放显存缓存。下次请求时重新初始化。"""
    global pipeline
    with lock:
        if pipeline is None or active_requests > 0:
            return False
        pipeline = None
    gc.collect()
    _release_gpu_memory()
    log.info("模型空闲超时(%ss),已卸载,显存/内存已释放", IDLE_TIMEOUT_SECONDS)
    return True


def _unload_loop():
    while True:
        time.sleep(UNLOAD_CHECK_INTERVAL)
        try:
            if pipeline is not None and active_requests == 0:
                idle = time.monotonic() - last_used
                if idle >= IDLE_TIMEOUT_SECONDS:
                    unload_model()
        except Exception:
            pass


def md_to_text(md: str) -> str:
    t = re.sub(r"<[^>]+>", " ", md)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def res_to_text(res) -> str:
    """从 PPStructureV3 结果提取可检索文本(全文 OCR + 表格 HTML 转文本)"""
    inner = (res.json or {}).get("res") or {}
    parts = []
    ocr = inner.get("overall_ocr_res") or {}
    recs = ocr.get("rec_texts") or []
    if recs:
        parts.append("\n".join(str(x) for x in recs))
    for t in inner.get("table_res_list") or []:
        pred = (t or {}).get("pred_html") or ""
        if pred:
            parts.append(md_to_text(pred))
    return "\n".join(parts).strip()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _reply(self, code: int, obj: dict):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            ok = pipeline is not None
            self._reply(200, {"ok": ok, "ready": ok, "loaded": ok,
                              "idle_timeout_s": IDLE_TIMEOUT_SECONDS})
        else:
            self._reply(404, {"error": "not found"})

    def do_POST(self):
        global active_requests
        if self.path != "/ocr":
            self._reply(404, {"error": "not found"})
            return
        with lock:
            active_requests += 1
        _touch()
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n).decode("utf-8"))
            img = req["image"]
            if not os.path.isfile(img):
                self._reply(400, {"error": f"image not found: {img}"})
                return
            with PIPE_LOCK:
                pipe = ensure_pipeline()
                res = pipe.predict(img)[0]
            text = res_to_text(res)
            self._reply(200, {"ok": True, "text": text})
        except Exception as e:
            log.error("OCR 处理失败: %s", e)
            self._reply(500, {"ok": False, "error": str(e)})
        finally:
            with lock:
                active_requests -= 1


if __name__ == "__main__":
    log.info("OCR 服务启动: http://127.0.0.1:%d (空闲卸载超时 %ss)",
             PORT, IDLE_TIMEOUT_SECONDS)
    threading.Thread(target=_unload_loop, daemon=True).start()
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
