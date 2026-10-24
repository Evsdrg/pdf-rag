"""只在用户请求时本地渲染 PDF 页图;不调用 OCR 或视觉服务。"""
import json
import math

import fitz

from . import agent_documents, library

MAX_IMAGE_BYTES = 2_000_000


def render(file: str, page: int, clip: list[float] | None = None, max_size: int = 1600):
    if isinstance(page, bool) or not isinstance(page, int) or page < 1:
        raise library.LibraryError("page 需为正整数")
    if isinstance(max_size, bool) or not isinstance(max_size, int) or not 256 <= max_size <= 2400:
        raise library.LibraryError("max_size 需在256–2400之间")
    full = agent_documents.resolve(file)
    if not full.lower().endswith(".pdf"):
        raise library.LibraryError("页图仅支持PDF", code="UNSUPPORTED_FORMAT")
    with fitz.open(full) as doc:
        if page > len(doc):
            raise agent_documents.page_error(page, len(doc))
        target = doc[page - 1]
        bounds = target.rect
        normalized = [0.0, 0.0, 1.0, 1.0] if clip is None else clip
        if (not isinstance(normalized, list) or len(normalized) != 4 or
                any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in normalized)):
            raise library.LibraryError("clip需为归一化坐标[x0,y0,x1,y1]")
        x0, y0, x1, y1 = normalized
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            raise library.LibraryError("clip需满足0≤x0<x1≤1且0≤y0<y1≤1")
        area = fitz.Rect(bounds.x0 + x0 * bounds.width, bounds.y0 + y0 * bounds.height,
                         bounds.x0 + x1 * bounds.width, bounds.y0 + y1 * bounds.height)
        if area.is_empty or area.is_infinite:
            raise library.LibraryError("裁剪区域无效")
        scale = max_size / max(area.width, area.height)
        for _ in range(4):
            pix = target.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=area,
                                    colorspace=fitz.csRGB, alpha=False)
            data = pix.tobytes("jpeg", jpg_quality=85)
            if len(data) <= MAX_IMAGE_BYTES:
                metadata = {"schema_version": 2, "file": file, "page": page,
                            "page_basis": "physical", "kind": "pdf", "clip": normalized,
                            "width": pix.width, "height": pix.height, "mime_type": "image/jpeg"}
                return metadata, data
            scale *= .7
    raise library.LibraryError("页图超过返回上限,请缩小裁剪区域", code="IMAGE_TOO_LARGE")


def parse_clip(value: str):
    try:
        return json.loads(value) if value else None
    except ValueError:
        raise library.LibraryError("clip需为JSON坐标数组") from None
