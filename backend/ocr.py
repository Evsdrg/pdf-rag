"""OCR 后端抽象:本机 Paddle 服务 或 远程视觉模型 API。

两种后端对上层暴露同一个入口 `ocr_image(img_path) -> (text, err)`:
* local  —— 调本机 ocr_service.py 的 `POST /ocr`(PaddleOCR PP-StructureV3),
             入参是图片路径,服务在本机读文件。
* remote —— 调 OpenAI 兼容的 `/chat/completions`,把整页图 base64 塞进消息。
             适用于 PaddleOCR-VL 这类视觉语言模型(如 paddleocr-vl-1.6)。
             图片必须内联(base64),因为远端读不到本地路径。

选哪条由 config.get("ocr_backend") 决定。上层(ingest 的 ocr_page、doc_utils 的
read_page_text)只调本模块,不关心后端差异。
"""
import base64
import time

import httpx

from . import config


def _local_ocr(img_path: str, timeout: float) -> str:
    r = httpx.post(f"{config.get("ocr_url").rstrip("/")}/ocr", json={"image": img_path}, timeout=timeout)
    r.raise_for_status()
    return r.json().get("text", "")


def _remote_ocr(img_path: str, timeout: float) -> str:
    """视觉模型 OCR:整页图 base64 内联到 chat 消息。

    提示词由 config.get("ocr_prompt") 给出(默认 "OCR")。实测要点:
    * paddleocr-vl:提示词是白名单任务词(ocr/formula/table/chart/seal/spotting),
      自由文本会触发幻觉;markdown 由其 PaddleX 服务端后处理生成,裸模型拿不到。
    * hunyuan-ocr:"OCR" 即输出 markdown("##" 标题 + "|" 表格),稳定;
      官方任务词 "doc_parse" 是"理解+总结",会改写原文(关键词漂移),检索勿用。

    返回内容即页文本;不再做 markdown 剥离——表格的 markdown 结构对检索有价值,
    且纯文本模型(paddle)给的本就是纯文本。
    """
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = img_path.rsplit(".", 1)[-1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    payload = {
        "model": config.get("ocr_model"),
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": config.get("ocr_prompt")},
            ],
        }],
    }
    r = httpx.post(f"{config.get("ocr_api_base").rstrip("/")}/chat/completions",
                   headers={"Authorization": f"Bearer {config.OCR_API_KEY}"},
                   json=payload, timeout=timeout)
    r.raise_for_status()
    return (r.json()["choices"][0]["message"].get("content") or "").strip()


def ocr_image(img_path: str, timeout: float | None = None) -> tuple[str, str]:
    """识别一张图片,返回 (文本, 错误信息);成功时错误为空。

    顺带把本次真实调用的结果记进进程内状态(见 status),供前端展示——
    **不额外发任何探测请求**:状态完全由真实使用推导。
    """
    timeout = timeout or config.get("ocr_timeout")
    backend = str(config.get("ocr_backend")).strip().lower()
    t0 = time.time()
    try:
        if backend == "remote":
            text = _remote_ocr(img_path, timeout)
        else:
            text = _local_ocr(img_path, timeout)
        _record(backend, ok=True, elapsed=time.time() - t0)
        return text, ""
    except Exception as e:
        _record(backend, ok=False, elapsed=time.time() - t0,
                error=f"{type(e).__name__}: {e}")
        return "", f"{type(e).__name__}: {e}"


# 最近一次真实调用结果。进程内、不持久化:重启后回到"尚无调用记录"。
_last: dict = {}


def _record(backend: str, ok: bool, elapsed: float, error: str = "") -> None:
    _last.update({
        "ok": ok,
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(elapsed, 2),
        "error": error,
    })


def status() -> dict:
    """当前 OCR 配置 + 最近一次真实调用的结果。

    **刻意不做任何网络探测**:定时/主动探活会给上游服务带来无意义负载,
    且 OCR 后端可用性并不会在几秒内变化。需要验证后端是否可用时,
    让真实业务跑一次(读一个扫描页/重跑索引)即可。
    """
    backend = str(config.get("ocr_backend")).strip().lower()
    info: dict = {"backend": backend}
    if backend == "remote":
        info.update({"url": config.get("ocr_api_base"), "model": config.get("ocr_model")})
    else:
        info.update({"url": config.get("ocr_url")})
    info["last_call"] = dict(_last) if _last else None
    return info
