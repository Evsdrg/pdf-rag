"""纯本地 OCR 判定:文档分布提供上下文,只有内容完整的稀疏页才免除 OCR。"""
import hashlib
import math
import statistics
import threading
from collections import Counter, OrderedDict
from dataclasses import dataclass

import fitz

from . import config


@dataclass(frozen=True)
class Decision:
    needs_ocr: bool
    reason: str


_PALE_CACHE: OrderedDict[str, bool] = OrderedDict()
_PALE_LOCK = threading.Lock()


def _image_key(image):
    return image[2], image[3], image[4], image[5]


def _info_key(image):
    return image["width"], image["height"], image["bpc"], image["cs-name"].split("(", 1)[0]


def _fraction(page, image):
    return (fitz.Rect(image["bbox"]) & page.rect).get_area() / page.rect.get_area()


def _at_edge(page, image):
    rect = fitz.Rect(image["bbox"])
    return (rect.y1 <= page.rect.y0 + .15 * page.rect.height
            or rect.y0 >= page.rect.y0 + .85 * page.rect.height)


def _placement(page, image):
    r = page.rect
    return tuple(round(v / scale, 2) for v, scale in
                 zip(image["transform"], (r.width, r.height, r.width,
                                          r.height, r.width, r.height)))


def _pale_masked_image(doc, resource):
    if not resource[1] or resource[5] not in ("DeviceRGB", "ICCBased"):
        return False
    if resource[2] * resource[3] > 25_000_000:
        return False
    key = hashlib.sha256((doc.xref_object(resource[0]) + doc.xref_object(resource[1])).encode()
                         + doc.xref_stream_raw(resource[0])
                         + doc.xref_stream_raw(resource[1])).hexdigest()
    with _PALE_LOCK:
        if key in _PALE_CACHE:
            _PALE_CACHE.move_to_end(key)
            return _PALE_CACHE[key]
    color = fitz.Pixmap(doc, resource[0])
    if color.colorspace is None or color.colorspace.n != 3:
        return False
    if color.alpha:
        color = fitz.Pixmap(color, 0)
    pix = fitz.Pixmap(color, fitz.Pixmap(doc, resource[1]))
    # 全分辨率颜色直方图保留小字号深色文字,不依赖会稀释笔画的缩略图。
    pale = all(min(color[:3]) + 255 - color[3] >= 200
               for color in pix.color_count(colors=True))
    with _PALE_LOCK:
        _PALE_CACHE[key] = pale
        _PALE_CACHE.move_to_end(key)
        while len(_PALE_CACHE) > 64:
            _PALE_CACHE.popitem(last=False)
    return pale


class DocumentPolicy:
    """仅在同一个已打开的 Document 内复用;不缓存 Document/Page 等原生对象。"""

    def __init__(self, doc, threshold=None, smart=None):
        self.doc = doc
        self.threshold = config.get("ocr_min_chars") if threshold is None else threshold
        self.smart = config.get("ocr_smart_filter") if smart is None else smart
        self._text_inspection_failed = set()
        texts = []
        for number, page in enumerate(doc):
            try:
                texts.append(page.get_text("text"))
            except Exception:
                texts.append("")
                self._text_inspection_failed.add(number)
        self.texts = tuple(texts)
        self.counts = tuple(len(text.strip()) for text in self.texts)
        self.low_ratio = sum(n < self.threshold for n in self.counts) / max(1, len(doc))
        self.run_lengths = [0] * len(doc)
        start = 0
        while start < len(doc):
            if self.counts[start] >= self.threshold:
                start += 1
                continue
            end = start + 1
            while end < len(doc) and self.counts[end] < self.threshold:
                end += 1
            self.run_lengths[start:end] = [end - start] * (end - start)
            start = end
        self._resources = None
        self._frequency = Counter()
        self._image_inspection_failed = set()
        self._decisions = {}
        self._decorations = {}
        self._decoration_placements = {}
        self._infos = {}

    def _images(self, number):
        if number not in self._infos:
            self._infos[number] = self.doc[number].get_image_info()
        return self._infos[number]

    def _load_resources(self):
        if self._resources is None:
            self._resources = []
            for number, page in enumerate(self.doc):
                try:
                    self._resources.append(page.get_images(full=True))
                except Exception:
                    self._resources.append([])
                    self._image_inspection_failed.add(number)
            self._frequency = Counter(xref for images in self._resources
                                      for xref in {im[0] for im in images})

    def _unique_resource(self, number, image):
        matches = {im[0]: im for im in self._resources[number]
                   if _image_key(im) == _info_key(image)}
        return next(iter(matches.values())) if len(matches) == 1 else None

    def _decoration(self, resource):
        xref = resource[0]
        if xref in self._decorations:
            return self._decorations[xref]
        self._decorations[xref] = ""
        if self._frequency[xref] < max(3, math.ceil(len(self.doc) * .6)):
            return ""
        pages = [i for i, images in enumerate(self._resources) if i > 0
                 and any(im[0] == xref for im in images)]
        if len(pages) < 3:
            return ""
        samples = [pages[0], pages[len(pages) // 2], pages[-1]]
        placements, border, diagonal = [], True, True
        for number in samples:
            matches = [im for im in self._images(number)
                       if self._unique_resource(number, im) is not None
                       and self._unique_resource(number, im)[0] == xref]
            if len(matches) != 1:
                return ""
            page, image = self.doc[number], matches[0]
            placements.append(_placement(page, image))
            border = border and _at_edge(page, image) and _fraction(page, image) <= .04
            a, b, c, d, _, _ = image["transform"]
            diagonal = diagonal and min(abs(a), abs(b), abs(c), abs(d)) > 1
        if len(set(placements)) != 1:
            return ""
        kind = ("border" if border else "pale" if diagonal
                and _pale_masked_image(self.doc, resource) else "")
        self._decorations[xref] = kind
        if kind:
            self._decoration_placements[xref] = placements[0]
        return kind

    def _only_decorative_images(self, number):
        self._load_resources()
        if number in self._image_inspection_failed:
            return False
        page = self.doc[number]
        for image in self._images(number):
            resource = self._unique_resource(number, image)
            if resource is None:
                return False
            kind = self._decoration(resource)
            if kind == "pale":
                if _placement(page, image) == self._decoration_placements[resource[0]]:
                    continue
                return False
            if kind == "border":
                if (_at_edge(page, image) and _fraction(page, image) <= .04
                        and _placement(page, image) == self._decoration_placements[resource[0]]):
                    continue
                if (number == 0 and _fraction(page, image) <= .3
                        and image["bbox"][3] <= page.rect.y0 + .5 * page.rect.height):
                    continue
            return False
        return True

    def _simple_rules(self, page):
        paths = page.get_drawings()
        if len(paths) > 20 or sum(len(p["items"]) for p in paths) > 32:
            return False
        for path in paths:
            if path.get("fill") is not None:
                if not all(item[0] == "re"
                           and min(item[1].width, item[1].height) <= 1
                           and max(item[1].width, item[1].height) >= 25
                           and (item[1].y1 <= page.rect.y0 + .17 * page.rect.height
                                or item[1].y0 >= page.rect.y0 + .83 * page.rect.height)
                           for item in path["items"]):
                    return False
                continue
            for item in path["items"]:
                if item[0] == "re":
                    continue
                if item[0] != "l":
                    return False
                a, b = item[1:3]
                if abs(a.x - b.x) > .5 and abs(a.y - b.y) > .5:
                    return False
        return True

    def decide(self, number):
        if number not in self._decisions:
            self._decisions[number] = self._decide(number)
        return self._decisions[number]

    def _decide(self, number):
        if number in self._text_inspection_failed:
            return Decision(True, "inspection_failed")
        text = self.texts[number].strip()
        if len(text) >= self.threshold:
            return Decision(False, "sufficient_text")
        if not self.smart:
            return Decision(True, "legacy_threshold")
        if not text:
            return Decision(True, "no_text")
        if len(self.doc) < 4 or self.low_ratio > .5:
            return Decision(True, "document_low_text")
        if self.run_lengths[number] >= 4:
            return Decision(True, "consecutive_low_text")
        visible = [c for c in text if not c.isspace()]
        if (len(visible) < 32 or "\ufffd" in text
                or sum(c.isalnum() for c in visible) < len(visible) / 2):
            return Decision(True, "sparse_or_invalid_text")
        try:
            page = self.doc[number]
            if page.first_annot is not None or page.first_widget is not None:
                return Decision(True, "annotation")
            if not self._only_decorative_images(number):
                return Decision(True, "content_image")
            if not self._simple_rules(page):
                return Decision(True, "complex_vectors")
            blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)
            center_chars = sum(len(span["text"].strip())
                               for block in blocks["blocks"] for line in block.get("lines", [])
                               for span in line.get("spans", [])
                               if page.rect.y0 + .15 * page.rect.height
                               <= (span["bbox"][1] + span["bbox"][3]) / 2
                               <= page.rect.y0 + .85 * page.rect.height)
            if center_chars < 12:
                return Decision(True, "edge_text_only")
        except Exception:
            return Decision(True, "inspection_failed")
        return Decision(False, "native_sparse_cover" if number == 0 else "native_sparse_page")

    def summary(self):
        return {"pages": len(self.counts), "low_pages": sum(n < self.threshold for n in self.counts),
                "low_ratio": round(self.low_ratio, 4),
                "median_chars": statistics.median(self.counts) if self.counts else 0,
                "max_low_run": max(self.run_lengths, default=0)}
