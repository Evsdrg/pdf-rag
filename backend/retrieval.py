"""共享检索核心。

流水线:多路召回(FTS / 型号子串 / 向量 / 可选实体桥)→ RRF 融合 → 内容去重 → 重排 → 片段。

实体桥是默认关闭的实验通道:它只从现有 chunk 文本构造确定性、有限的实体连接，
最终仍回到原始 chunk，不改变主表或向量分区契约。

以下设计点均经实测,勿凭直觉回退:

* **型号子串召回**:FTS 对型号前缀有盲区(W25Q32 找不到 W25Q32JW)。
* **页级累加计分**:同页多块累加是有效的相关性信号;改成块级独立计分会让正确页
  被邻近页顶掉(实测回归)。
* **代表块取"自身得分最高"者**,而非最先入队的页首块 —— 页首块几乎不含答案。
* **片段取查询感知窗口**,而非块首:块中位数约 1400 字符(p90 2821),
  页首数百字符恒为文档页眉 + 章节标题,表格参数值在更深处。
* **型号 token 不参与页内定位**:它每页页眉都出现,对"定位页内哪一段"无区分度,
  反而让含页眉的窗口压过含参数值的窗口。
* **中文按 2-gram 切分**:否则"发送功率电流"必须逐字命中,而文档写作"发送功率",
  中文查询对定位几乎不贡献。
* **内容去重只认非空 md5**:同型号、标题或块相似不足以证明厂商/文档族相同;
  当前索引没有可靠版本继承关系,不同字节的来源保留,不猜测合并版本。
"""
import collections
import logging
import os
import re
import time

import httpx
import pyarrow as pa

from . import config, query_lex
from .doc_utils import product_label as _product_label

log = logging.getLogger("pdfrag.retrieval")

# ---------- 算法常量(不对外暴露,改这里需重跑评测) ----------
# 供子串召回投影的列:不要把 768 维向量列一起物化。
# 必须含 md5 —— 去重依赖它识别"同料号族共用一份手册"(缺了会让去重静默失效)。
_PROJ_COLS = ["text", "file", "page", "category", "model_no", "c_id", "version",
              "title", "md5", "uid"]
# 目录/修订史页特征(这类页关键词密度高,天然占优,需降权)
_TOC_REV_RE = re.compile(
    r"(revision history|修订历史|修订记录|table of contents|contents\s*$|目录)", re.I)
# 可重试的 HTTP 状态码:服务商在密集请求下会返回 403/429
_RETRYABLE_STATUS = (403, 408, 429, 500, 502, 503, 504)
_SCORE_DECIMALS = 4


# ==================== HTTP 层 ====================

_CLIENT: httpx.Client | None = None


def _client() -> httpx.Client:
    """共享连接池。每处 httpx.post 都新建客户端会重付 TLS 握手 ——
    实测重排 8 块的固定开销 1972ms → 1236ms(-37%)。"""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = httpx.Client(
            timeout=httpx.Timeout(config.get("http_timeout"),
                                  connect=config.get("http_connect_timeout")),
            limits=httpx.Limits(max_keepalive_connections=config.get("http_keepalive"),
                                max_connections=config.get("http_max_conn")),
        )
    return _CLIENT


def reset_client():
    """配置变更后重建连接池(超时/连接数改动需要生效)。"""
    global _CLIENT
    if _CLIENT is not None:
        _CLIENT.close()
    _CLIENT = None


# 响应体里出现这些字符串时,失败是**确定性**的:服务商侧该模型没有可用渠道,
# 重试多少次都一样。实测单次失败的重排要烧 9.5s(4 次退避),而每次查询都要走
# 一遍,等于每次查询白等 8s 以上、且结果毫无区别。
_NO_RETRY_MARKERS = ("model_not_found", "no available channel",
                     "model name cannot be empty")


def _deterministic_failure(r) -> bool:
    """是否属"重试无意义"的失败。

    与限流(403/429)区分开 —— 那些是暂时的,指数退避确实能救回来。
    """
    if r.status_code not in _RETRYABLE_STATUS:
        return False
    body = r.text[:300].lower()
    return any(m in body for m in _NO_RETRY_MARKERS)


def _post_retry(url: str, payload: dict):
    """带指数退避的 POST。

    原先一次失败即降级,结果质量无声下滑而调用方毫无察觉 ——
    实测连续 55 条评测中有 19 条被服务商限流(403),分数因此被严重低估。
    """
    attempts = config.get("retry_attempts")
    base = config.get("retry_base_delay")
    last = ""
    for i in range(attempts):
        try:
            r = _client().post(url, headers={"Authorization": f"Bearer {config.EMBED_API_KEY}"},
                               json=payload)
            if r.status_code not in _RETRYABLE_STATUS:
                r.raise_for_status()
                return r
            if _deterministic_failure(r):
                raise RuntimeError(f"HTTP {r.status_code} 模型无可用渠道: {r.text[:160]}")
            last = f"HTTP {r.status_code}"
        except httpx.HTTPError as e:
            last = f"{type(e).__name__}: {e}"
        if i < attempts - 1:
            time.sleep(base * (2 ** i))
    raise RuntimeError(f"重试 {attempts} 次仍失败: {last}")


def _base_url() -> str:
    """嵌入服务根地址(去掉尾斜杠,避免拼接出 //embeddings)。"""
    return str(config.get("embed_base_url")).rstrip("/")


# 查询向量 LRU。键必须带模型、input_type 与维度:换模型后旧向量不可比,
# 复用会得到"看起来正常、实际跨空间"的结果。条目少,不需要持久化。
_EMBED_CACHE: "collections.OrderedDict[tuple, list[float]]" = collections.OrderedDict()


def embed_query(text: str, input_type_override: str | None = None,
                dim_override: int | None = None,
                model_override: str | None = None) -> list[float]:
    """取查询向量。命中本地缓存则不再访问上游。

    同一查询在结果缓存过期后会重新走到这里;没有这层缓存就要重付一次嵌入调用。

    `model_override` / `input_type_override` / `dim_override` 用于"按分区的契约
    生成查询向量":分区可能不是用当前全局配置建的(用户换过模型/维度/input_type),
    查询向量必须与分区**完全**匹配 —— 三者任缺一个都是跨契约检索。

    **model 也必须覆盖**:不同模型的向量空间不可比。只覆盖 dim/input_type 时,
    若两个模型维度恰好相同(如都截断到 768),维度检查通不出任何异常,就会拿
    A 模型的查询向量去搜 B 模型建的向量,相似度毫无意义却毫无声响。
    缓存键因此包含这三个值。
    """
    dim = dim_override if dim_override is not None else config.get("embed_dimensions")
    input_type = (input_type_override if input_type_override is not None
                  else config.get("embed_input_type_query"))
    model = model_override if model_override is not None else config.get("embed_model")
    key = (model, input_type, dim, text)
    cached = _EMBED_CACHE.get(key)
    if cached is not None:
        _EMBED_CACHE.move_to_end(key)
        return cached

    payload = {"model": model, "input": [text]}
    if input_type:                 # Cohere 系需要;留空则不发送(OpenAI 兼容模型)
        payload["input_type"] = input_type
    if dim:                        # 显式声明维度,不依赖服务商默认值
        payload["dimensions"] = dim
    r = _post_retry(f"{_base_url()}/embeddings", payload)
    vec = r.json()["data"][0]["embedding"]

    size = config.get("embed_cache_size")
    if size > 0:
        _EMBED_CACHE[key] = vec
        _EMBED_CACHE.move_to_end(key)
        while len(_EMBED_CACHE) > size:
            _EMBED_CACHE.popitem(last=False)
    return vec


def _call_reranker(query: str, docs: list[str]) -> list[float]:
    """调服务商 reranker 打分(按输入顺序返回分数)。

    **名字必须与 search() 的形参不同**:历史上函数名与形参同为 rerank,
    导致调用被形参遮蔽('bool' object is not callable),重排自始从未生效,
    且异常被吞掉无人察觉。
    """
    r = _post_retry(f"{_base_url()}/rerank",
                    {"model": config.get("reranker_model"), "query": query,
                     "documents": docs, "top_n": len(docs)})
    results = sorted(r.json()["results"], key=lambda x: x["index"])
    return [float(x["relevance_score"]) for x in results]


# ==================== 查询词解析 ====================

def _model_tokens(query: str) -> list[str]:
    return query_lex.model_tokens(query)


def _query_terms(query: str) -> tuple[list[str], set[str]]:
    """型号保持完整且不参与页内定位;中文按原有 2-gram 切分。"""
    return query_lex.query_terms(query)


# ==================== 片段窗口 ====================

def _score_window(seg: str, terms: list[str], models: set[str]) -> float:
    """窗口打分。

    型号 token **不参与**:它每页页眉都出现,对"定位页内哪一段"没有区分度,
    反而让含页眉的窗口压过含参数值的窗口(实测直接漏掉表格末尾的答案)。
    型号的职责是文档级筛选,不是页内定位。

    含「数字+单位」给固定加分。不要改成按数值个数加权 —— 实测会让密集表格
    (修订史、多列表)反超真正的取值处。
    """
    low = seg.lower()
    sc = sum(1.0 for t in terms if t.lower() not in models and t.lower() in low)
    if query_lex.VALUE_RE.search(seg):
        sc += config.get("num_unit_bonus")
    return sc


def _window_starts(length: int, width: int) -> list[int]:
    """窗口起点序列。

    刻意**不补末尾窗口**(start = length-width):实测会拉低答案命中率 ——
    末尾常是表格转储区,靠加分抢走本该属于正文取值处的窗口。
    """
    step = max(1, width // max(1, config.get("window_stride_div")))
    return list(range(0, max(1, length - width + 1), step))


def _best_window(text: str, query: str, width: int) -> tuple[int, float]:
    """返回 (最佳窗口起点, 得分)。全部窗口无命中时得分为 0。"""
    terms, models = _query_terms(query)
    if not terms:
        return 0, 0.0
    best_st, best_sc = 0, 0.0
    for st in _window_starts(len(text), width):
        sc = _score_window(text[st:st + width], terms, models)
        if sc > best_sc:
            best_st, best_sc = st, sc
    return best_st, best_sc


def _render_window(text: str, st: int, width: int) -> str:
    seg = text[st:st + width]
    return ("…" if st else "") + seg + ("…" if st + width < len(text) else "")


def make_snippet(text: str, query: str, width: int = 0) -> str:
    """在块内定位与查询最相关的窗口,而不是取块首。"""
    width = width or config.get("snippet_width")
    if len(text) <= width:
        return text
    st, sc = _best_window(text, query, width)
    return text[:width] if sc <= 0 else _render_window(text, st, width)


def page_snippet(chunks: list[dict], query: str, width: int = 0) -> str:
    """在一页的**所有命中块**上挑最佳窗口,而不是只看代表块。

    提取时表格 markdown 被追加在页文本之后,会被分块切到与正文不同的块里;
    只对代表块取窗口会恰好漏掉参数值所在的那一块。
    """
    width = width or config.get("snippet_width")
    best_text, best_sc = "", -1.0
    for row in chunks:
        text = row["text"]
        if len(text) <= width:
            terms, models = _query_terms(query)
            st, sc = 0, _score_window(text, terms, models)
        else:
            st, sc = _best_window(text, query, width)
        if sc > best_sc:
            best_sc, best_text = sc, _render_window(text, st, width)
    if best_sc <= 0 and chunks:
        return chunks[0]["text"][:width]
    return best_text


def snippet_reference(chunks: list[dict], query: str, width: int = 0) -> dict:
    """保留现有窗口选择,只给返回展示增加可核对的块引用。"""
    width = width or config.get("snippet_width")
    best_row, best_start, best_score = None, 0, -1.0
    terms, models = _query_terms(query)
    for row in chunks:
        text = row["text"]
        if len(text) <= width:
            start, score = 0, _score_window(text, terms, models)
        else:
            start, score = _best_window(text, query, width)
        if score > best_score:
            best_row, best_start, best_score = row, start, score
    if best_row is None:
        return {}
    if best_score <= 0:
        best_row, best_start = chunks[0], 0
    text = best_row["text"]
    end = min(len(text), best_start + width)
    # 仅有限扩展到邻近行边界,不挪动检索窗口、不改送重排的文本。
    before = text.rfind("\n", max(0, best_start - 120), best_start)
    if before >= 0:
        best_start = before + 1
    after = text.find("\n", end, min(len(text), end + 120))
    if after >= 0:
        end = after + 1
    segment = text[best_start:end]
    controls = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
    cleaned = controls.sub("", segment)
    header = ""
    if "|" in segment:
        for match in re.finditer(r"(?m)^\|[^\n]*\n\|\s*:?-", text[:best_start]):
            header_end = text.find("\n", match.end())
            candidate = text[match.start():header_end if header_end >= 0 else match.end()]
            if len(candidate) <= 500:
                header = candidate
    return {"chunk_id": best_row.get("uid"), "start_offset": best_start, "end_offset": end,
            "index_md5": best_row.get("md5"),
            "offset_basis": "indexed_chunk", "truncated_before": best_start > 0,
            "truncated_after": end < len(text), "text": cleaned,
            "table_header": header or None,
            "warnings": ([{"code": "TEXT_CONTROLS_REMOVED", "message": "展示已移除无意义控制字符,未推测修复字符"}]
                         if cleaned != segment else [])}


# ==================== 页面角色 ====================

def _role_penalty(row: dict, query: str = "", relevance: float | None = None,
                  evidence_text: str = "") -> float:
    """只惩罚有内容依据的封面/目录;技术证据与强模型相关性不因首页页号受罚。"""
    text = evidence_text or row["text"]
    keys = query_lex.extract_entities(text)
    technical = query_lex.VALUE_RE.search(text) and any(
        key.startswith(("parameter:", "symbol:")) for key in keys)
    if technical or (relevance is not None and relevance >= 0.9):
        return 1.0
    head = text[:config.get("toc_scan_chars")]
    if _TOC_REV_RE.search(head):
        return config.get("penalty_toc_rev")
    if int(row["page"]) == 0 and re.search(
            r"\b(?:data\s*sheet|user\s+manual|product\s+specification)\b|数据手册|规格书|用户手册", head, re.I):
        return config.get("penalty_cover")
    return 1.0


def _meta_line(row: dict) -> str:
    """送重排器时前置的文档身份行。

    重排器只读正文,而品牌/系列名常只出现在文件名里 —— EC800M 与 ML307R 这类
    同族手册正文高度相似,不给文件名信号时重排器无法区分(实测 5 条 Quectel
    查询全被 ML307R 抢占)。仅影响送入重排器的文本,不改索引、不改片段。
    """
    parts = [os.path.basename(row.get("file", ""))]
    if row.get("model_no"):
        parts.append(f"型号 {row['model_no']}")
    if row.get("category"):
        parts.append(f"类别 {row['category']}")
    return "[文档] " + " | ".join(p for p in parts if p)


# ==================== 投影表与子串召回 ====================

_PROJ_CACHE: tuple[object, int, pa.Table] | None = None


def _proj_table(table) -> pa.Table:
    """按表版本缓存投影表。

    _substring_recall 原先每次 table.to_arrow() 全量物化(含向量列,+78MB),
    而它对查询里每个型号 token 都要调一次,代价被放大数倍。
    """
    global _PROJ_CACHE
    ver = table.version
    if _PROJ_CACHE is None or _PROJ_CACHE[0] is not table or _PROJ_CACHE[1] != ver:
        full = table.to_arrow()
        try:
            _PROJ_CACHE = (table, ver, full.select(_PROJ_COLS))
        finally:
            del full
    return _PROJ_CACHE[2]


def _substring_recall(table, term: str, limit: int, *, query: str = "", category=None, file=None) -> list[dict]:
    """按完整型号字面前缀匹配 text 或既有 model_no;先过滤,再按参数相关性截断。"""
    import pyarrow.compute as pc
    df = _proj_table(table)
    mask = pc.or_(pc.match_substring(df["text"], term, ignore_case=True),
                  pc.match_substring(df["model_no"], term, ignore_case=True))
    if category:
        mask = pc.and_(mask, pc.equal(df["category"], category))
    if file:
        mask = pc.and_(mask, pc.match_substring(df["file"], file.replace("\\", "/")))
    rows = df.filter(mask).to_pylist()
    terms, models = _query_terms(query)
    return sorted(rows, key=lambda row: -_score_window(row["text"], terms, models))[:limit]


# ==================== 候选收集 ====================

class _Candidates:
    """候选收集器:页级累加计分,并记录该页的代表块与全部命中块。

    * 页级累加是刻意的(见模块文档):同页多块累加是有效相关性信号。
    * 代表块取"自身得分最高"者 —— 页首块几乎不含答案。
    * 全部命中块供片段跨块取窗口,因为表格常被切到与正文不同的块。
    """

    __slots__ = ("scores", "rows", "chunks", "traces", "_best", "_rrf_k", "_bonus_rank")

    def __init__(self, rrf_k: int, bonus_rank: int):
        self.scores: dict[tuple, float] = {}
        self.rows: dict[tuple, dict] = {}
        self.chunks: dict[tuple, list[dict]] = {}
        self.traces: dict[tuple, dict] = {}
        self._best: dict[tuple, tuple[float, dict]] = {}
        self._rrf_k = rrf_k
        self._bonus_rank = bonus_rank

    def add(self, row: dict, rank: int, bonus: bool = False):
        pk = (row["file"], int(row["page"]))
        s = 1.0 / (self._rrf_k + (self._bonus_rank if bonus else rank))
        self.scores[pk] = self.scores.get(pk, 0.0) + s
        self.chunks.setdefault(pk, []).append(row)
        cur = self._best.get(pk)
        if cur is None or s > cur[0]:
            self._best[pk] = (s, row)
            self.rows[pk] = row

    def __bool__(self) -> bool:
        return bool(self.scores)

    def top(self, limit: int) -> list[tuple[tuple, float]]:
        return sorted(self.scores.items(), key=lambda x: -x[1])[:limit]


def _sql_quote(value: str) -> str:
    return value.replace("'", "''")


def _like_literal(file: str) -> str:
    """把 file 过滤参数转成 LIKE 字面量。

    实测 DataFusion 的 LIKE 里 `_`/`%` 是通配符(BH1750FVI_TR 能命中
    BH1750FVI-TR),而本参数的语义与 Python 侧兜底判定 `_accepts` 都是
    **字面子串**——不转义的话,SQL 下推生效与否会给出不同结果。反斜杠分隔符
    归一为正斜杠:索引存的是正斜杠路径,Windows 风格的输入才能命中。
    """
    s = file.replace("\\", "/")
    return s.replace("%", "\\%").replace("_", "\\_")


def _apply_filter(query, category: str | None, file: str | None):
    """把过滤条件下推到 LanceDB,保证候选池规模不被过滤后截断。"""
    conds = []
    if category:
        conds.append(f"category = '{_sql_quote(category)}'")
    if file:
        conds.append(f"file LIKE '%{_sql_quote(_like_literal(file))}%'")
    return query.where(" AND ".join(conds)) if conds else query


def _accepts(row: dict, category: str | None, file: str | None) -> bool:
    """Python 侧兜底校验(下推条件在部分 LanceDB 版本上不保证生效)。

    三条通道传入的 row 来源不同:FTS/子串来自主表,向量通道来自**分区表**。
    分区表的 category/file 是冗余列(为把过滤下推而存),理论上可能与主表不一致
    (分区行滞后于主表)。这里只做粗筛以缩小回表范围,权威性由 _hydrate 保证:
    主表查不到的 uid 会被丢弃,所以冗余列陈旧不会放出错误结果。
    """
    if category and row.get("category") != category:
        return False
    if file and file.replace("\\", "/") not in row.get("file", ""):
        return False
    return True


def _channel_fts(table, query: str, limit: int, category, file, cands, degraded):
    try:
        found = _apply_filter(table.search(query, query_type="fts"),
                              category, file).limit(limit).to_list()
    except Exception as e:
        degraded.append("fts")
        log.warning("FTS 检索失败: %s", e)
        return
    for rank, row in enumerate(found):
        if _accepts(row, category, file):
            cands.add(row, rank)


def _channel_substring(table, query: str, limit: int, category, file, cands, degraded):
    for term in _model_tokens(query):
        try:
            found = _substring_recall(table, term, limit, query=query, category=category, file=file)
        except Exception as e:
            degraded.append("substring")
            log.warning("子串召回失败(%s): %s", term, e)
            continue
        for row in found:
            if _accepts(row, category, file):
                cands.add(row, 0, bonus=True)


def _entity_trace(result, uid: str, row: dict, seeds: dict[str, dict]) -> dict:
    """仅描述检索连接,不把共享实体称为事实关系。"""
    path = result.paths.get(uid)
    trace = {"kind": "entity_expansion" if path else "entity_direct", "chunk_id": uid,
             "index_md5": row.get("md5"), "scope": "retrieval_only"}
    if path and path.get("seed_chunk_id") in seeds:
        seed = seeds[path["seed_chunk_id"]]
        trace.update(seed_chunk_id=seed["uid"], seed_file=seed["file"], seed_page=int(seed["page"]) + 1,
                     seed_index_md5=seed.get("md5"),
                     shared_entities=[key[:100] for key in path.get("shared_entities", [])[:4]])
    return trace


def _channel_structured(table, query: str, limit: int, category, file, cands, degraded,
                        diag: dict | None = None):
    """实体桥按 uid 回主表,每页最多补一块,不改重排分数。"""
    from . import entity

    try:
        seeds = _balance_models(cands.top(len(cands.scores)), cands.rows, query)
        result = entity.search(table, query, category=category, file=file, limit=limit,
                               seed_rows=[cands.rows[key] for key, _ in seeds[:entity.MAX_SEED_INPUTS]])
        if diag is not None:
            diag["structured"] = entity.diagnostics(result)
        seed_ids = {path["seed_chunk_id"] for path in result.paths.values() if path.get("seed_chunk_id")}
        rows = _hydrate(table, list(dict.fromkeys((*result.ordered_uids, *sorted(seed_ids)))))
        seen: set[tuple[str, int]] = set()
        for rank, uid in enumerate(result.ordered_uids):
            row = rows.get(uid)
            if row is None or not _accepts(row, category, file):
                continue
            page_key = (row["file"], int(row["page"]))
            if page_key in seen:
                continue
            path = result.paths.get(uid)
            if path:
                seed = rows.get(path["seed_chunk_id"])
                if seed is None or not _accepts(seed, category, file):
                    continue
            seen.add(page_key)
            if page_key not in cands.scores:
                cands.add(row, limit + rank)
            elif not any(chunk.get("uid") == uid for chunk in cands.chunks[page_key]):
                # 已有页只补缺失块供证据定位,不重复奖励同一身份或改变代表块。
                cands.chunks[page_key].append(row)
            cands.traces[page_key] = _entity_trace(result, uid, row, rows)
        if diag is not None:
            diag["structured"]["added_pages"] = len(seen)
    except Exception as e:
        degraded.append("structured")
        log.warning("结构化实体检索失败: %s", e)
        if diag is not None:
            diag["structured"] = {**diag.get("structured", {}), "enabled": True, "status": "failed"}


def _hydrate(main_table, uids: list[str]) -> dict[str, dict]:
    """按 uid 从主表取回元数据与文本。

    分区表只有 uid + 过滤列 + 向量,答案文本在主表 —— 实测 300 个 uid 回表 6ms,
    相对嵌入调用可忽略。主表已无的 uid(孤儿)自然查不到,由调用方丢弃。
    """
    if not uids:
        return {}
    # uid 是 sha256 前 20 位十六进制,不含引号;仍按 SQL 字面量转义,防将来改生成规则
    quoted = ",".join("'" + u.replace("'", "''") + "'" for u in uids)
    rows = main_table.search().where(f"uid IN ({quoted})").limit(len(uids) + 10).to_list()
    return {r["uid"]: r for r in rows}


_COV_CACHE: dict[tuple, float] = {}


def _partition_coverage_ratio(db, table, slug: str) -> float | None:
    """分区对主表的块覆盖比例,按 (slug, 主表版本, 分区版本) 缓存。

    统计要扫全分区 uid,实测 12421 块 13ms;每个检索请求都算一遍太浪费,
    而它与 ingest 同步变化 —— 用两个 version 做失效信号即可。
    """
    from . import vecstore
    part = vecstore.open_partition(db, slug)
    if part is None:
        return None
    key = (slug, table.version, part.version)
    if key in _COV_CACHE:
        return _COV_CACHE[key]
    cov = vecstore.coverage(db, table, slug)
    ratio = cov["ratio"]
    _COV_CACHE[key] = ratio
    # 只保留最新一条,避免长期累积
    for k in [k for k in _COV_CACHE if k[0] == slug and k != key]:
        _COV_CACHE.pop(k, None)
    return ratio


def _channel_vector(table, query: str, limit: int, category, file, cands, degraded,
                    diag: dict | None = None):
    """向量通道:在分区表上检索,命中 uid 回主表取元数据。

    分区与查询向量必须成对:分区记录了建库时的 model/dim/input_type,查询侧用该
    分区的 **model + dim + input_type_query** 生成向量,而不是用当前全局配置 ——
    否则是"用 A 契约的查询向量检索 B 契约建的分区",相似度无意义。

    多分区按 `vector_models_priority` 的顺序依次检索。**一个块只用一个模型的向量**:
    某块若在靠前分区已命中,靠后分区的同名命中直接丢弃(按 uid 去重),否则它会被
    重复累加 RRF 分,让"被多个模型索引过的块"凭空获得权重优势。不同模型的向量
    也绝不混在一次距离计算里 —— 空间不可比。

    diag 传入时写入本次**实际参与检索**的分区列表,让"某个模型悄悄失败"
    能在响应的诊断信息里看见,而不是只躺在日志里。
    """
    from . import library, vecstore
    db = library.get_db()
    if db is None:
        degraded.append("vector:index_unavailable")
        return
    parts = vecstore.select_partitions(db)
    if not parts:
        degraded.append("vector:no_partition")
        log.warning("没有可用的向量分区;检查向量模型优先级/排除配置,或跑一次索引")
        return

    covered: set[str] = set()
    seen_uid: set[str] = set()
    # 实际检索成功的分区。逐个静默 continue 会让配置问题表现为"结果莫名变少",
    # 而用户以为所有分区都在生效 —— 用过的模型必须能一眼看到。
    used: list[str] = []
    for meta in parts:
        slug = meta["slug"]
        part = vecstore.open_partition(db, slug)
        if part is None:
            degraded.append("vector:partition_unavailable")
            continue
        stage = "embedding"
        try:
            vec = embed_query(query, input_type_override=meta.get("input_type_query"),
                              dim_override=meta.get("dim"),
                              model_override=meta.get("model"))
            stage = "dimension"
            want = part.schema.field("vector").type.list_size
            if len(vec) != want:
                raise ValueError(
                    f"查询向量维度 {len(vec)} 与分区 {slug} 的 {want} 不符;"
                    f"检查「向量维度」配置(EmbedDimensions)是否与建库时一致")
            stage = "search"
            q = part.search(vec, query_type="vector")
            # 有索引时补一道精确重算:IVF 只搜部分簇,不加 refine 会静默漏召回。
            # 没索引的分区(旧库/建索引失败)退化为暴力扫描,本身是精确的,不加。
            if vecstore.has_vector_index(part):
                q = q.refine_factor(vecstore.REFINE_FACTOR)
            found = _apply_filter(q, category, file).limit(limit).to_list()
        except Exception as e:
            degraded.append(f"vector:{stage}_failed")
            log.warning("向量检索失败(%s): %s", slug, e)
            continue
        used.append(slug)
        hits = [r for r in found if _accepts(r, category, file)]
        rows = _hydrate(table, [r["uid"] for r in hits])
        for rank, r in enumerate(hits):
            # 一个块在多个分区都命中时只计一次 —— 否则它会被重复累加 RRF 分,
            # 让"被多个模型索引过的块"凭空获得权重优势。按优先级先到的为准。
            if r["uid"] in seen_uid:
                continue
            row = rows.get(r["uid"])
            if row is None:          # 主表已无(孤儿),丢弃
                continue
            seen_uid.add(r["uid"])
            cands.add(row, rank)
            covered.add(r["uid"])

    if used and diag is not None:
        diag["vector_partitions"] = used
    if not used:
        return
    # 覆盖率是"分区覆盖了主表多少块"的静态属性,不是本次召回数 —— 一次检索只取
    # 几十块,用召回数除以总量必然接近 0,会把正常检索误判成降级。
    min_ratio = float(config.get("vector_coverage_min"))
    if min_ratio > 0:
        low = []
        for meta in parts:
            ratio = _partition_coverage_ratio(db, table, meta["slug"])
            if ratio is not None and ratio < min_ratio:
                low.append(f"{meta['slug']}={ratio:.0%}")
        if low:
            degraded.append("vector:low_coverage")
            log.warning("向量分区覆盖率低于下限 %.0f%%: %s;"
                        "对这些模型补跑一次索引可恢复",
                        min_ratio * 100, ", ".join(low))


# ==================== 内容副本去重 ====================

def _same_document(rows1: list[dict], rows2: list[dict]) -> bool:
    """同字节内容才可合并;标题/型号/文本相似不能证明来源或版本继承。"""
    md1, md2 = rows1[0].get("md5"), rows2[0].get("md5")
    return bool(md1 and md1 == md2)


_MAX_SOURCE_ALIASES = 4


def _pick_latest(cands, rows_by_key: dict, scores: dict, query: str = "", aliases: dict | None = None):
    """仅折叠同 MD5 副本,优先查询所指身份;保留有界别名,不推断新旧版本。"""
    groups: dict[tuple, list] = {}
    for key, _ in cands:
        row = rows_by_key[key]
        digest = row.get("md5")
        identity = ("md5", digest, row["page"]) if digest else ("file", row["file"], row["page"])
        groups.setdefault(identity, []).append(key)

    models = {token.lower() for token in _model_tokens(query)}
    keep: set = set()
    for group in groups.values():
        best = max(group, key=lambda key: (_model_identity_match(rows_by_key[key], models), scores[key]))
        keep.add(best)
        if aliases is not None and len(group) > 1:
            others = [{"file": rows_by_key[key]["file"], "model_no": rows_by_key[key].get("model_no", ""),
                       "index_md5": rows_by_key[key]["md5"], "scope": "same_bytes"}
                      for key in group if key != best]
            aliases[best] = {"items": others[:_MAX_SOURCE_ALIASES],
                             "omitted": max(0, len(others) - _MAX_SOURCE_ALIASES)}
    return [(k, s) for k, s in cands if k in keep]


# ==================== 重排 ====================

def _rerank_docs(cands, rows_by_key: dict, query: str, evidence_by_key: dict | None = None) -> list[str]:
    """结构化模式重用最终证据包;默认仍使用代表块窗口。"""
    docs = [rows_by_key[k]["text"] for k, _ in cands]
    if config.get("rerank_on_window"):
        docs = [evidence_by_key[k]["text"] if evidence_by_key is not None else make_snippet(d, query)
                for (k, _), d in zip(cands, docs)]
    if config.get("rerank_meta"):
        docs = [f"{_meta_line(rows_by_key[k])}\n{d}" for (k, _), d in zip(cands, docs)]
    return docs


def _model_identity_match(row: dict, models: set[str]) -> int:
    """完整查询型号与既有 model_no 的匹配,只作副本选择和平局裁决,不确认前缀变体。"""
    if not models:
        return 0
    return 2 if models.intersection(token.casefold() for token in _model_tokens(row.get("model_no", ""))) else 0


def _rerank_and_order(cands, rows_by_key: dict, query: str, evidence_by_key: dict | None = None):
    """重排并排序。返回 (排序后的候选, {key: 重排分})。

    模型相关性分经内容感知的角色惩罚后排序,外加一道**型号平局裁决**:同族手册两页的重排分差(实测
    0.006,如 EC800M vs EG800Z、74LVC1G04GV vs GW)低于重排自身抖动
    (0.004-0.008),先后本质随机;分差小于 rerank_tie_tolerance 时,查询里
    的型号 token 与文件身份匹配者在前。不要改成召回名次与重排名次的融合
    排序 —— 实测任何融合权重都会让概述页抢走参数值类查询的 top1
    (snippet@1 58%→38%)。
    """
    docs = _rerank_docs(cands, rows_by_key, query, evidence_by_key)
    rel = _call_reranker(query, docs)
    scores = {cands[i][0]: float(rel[i]) for i in range(len(cands))}
    adjusted = [rel[i] * _role_penalty(rows_by_key[key], query, rel[i],
                    evidence_by_key[key]["text"] if evidence_by_key is not None else "")
                for i, (key, _) in enumerate(cands)]
    order = sorted(range(len(cands)), key=lambda i: -adjusted[i])
    tol = float(config.get("rerank_tie_tolerance"))
    if tol > 0 and len(order) > 1:
        models = {tk.lower() for tk in _model_tokens(query)}
        if models:
            match = {cands[i][0]: _model_identity_match(rows_by_key[cands[i][0]], models)
                     for i in range(len(cands))}
            adj = adjusted
            for j in range(len(order) - 1):
                a, b = order[j], order[j + 1]
                if (abs(adj[a] - adj[b]) <= tol and match[cands[b][0]] > match[cands[a][0]]):
                    order[j], order[j + 1] = b, a
    return [cands[i] for i in order], scores


def _balance_models(picked, rows_by_key: dict, query: str):
    """仅结构化多型号查询使用轮转配额,组内保留当前排序。"""
    from . import entity
    models = [key for key in entity.extract_entities(query, query=True) if key.startswith("model:")]
    if len(models) < 2:
        return picked
    identities = {key: entity.extract_entities("", model_no=row.get("model_no", ""))
                  for key, row in rows_by_key.items()}
    groups = []
    for model in models:
        exact = [item for item in picked if model in identities[item[0]]]
        group = exact or [item for item in picked if len(model.removeprefix("model:")) >= 5
                         and any(key.startswith(model) for key in identities[item[0]] if key.startswith("model:"))]
        if group:
            groups.append(collections.deque(group))
    if len(groups) < 2:
        return picked
    out, seen = [], set()
    while any(groups):
        for group in groups:
            while group:
                item = group.popleft()
                if item[0] not in seen:
                    seen.add(item[0])
                    out.append(item)
                    break
    return out + [item for item in picked if item[0] not in seen]


class _EvidenceCoverage:
    """单次搜索内复用页/块词法,不跨请求保存正文或依赖过期实体索引。"""
    def __init__(self, query: str):
        self.slots = query_lex.evidence_slots(query)
        self.text_entities: dict[str, tuple[str, ...]] = {}
        self.model_entities: dict[str, set[str]] = {}
        self.pages: dict[tuple, tuple[set[str], str, set[str]]] = {}

    def page(self, key, cands: _Candidates):
        if key not in self.pages:
            chunks = cands.chunks.get(key, [cands.rows[key]])
            texts = tuple(dict.fromkeys(chunk["text"] for chunk in chunks))
            entities = set()
            for text in texts:
                if text not in self.text_entities:
                    self.text_entities[text] = query_lex.extract_entities(text)
                entities.update(self.text_entities[text])
            model = cands.rows[key].get("model_no", "")
            if model not in self.model_entities:
                self.model_entities[model] = set(query_lex.extract_entities("", model_no=model))
            self.pages[key] = entities, "\n".join(texts), self.model_entities[model]
        return self.pages[key]


def _cover_evidence(picked, cands: _Candidates, query: str, coverage: _EvidenceCoverage | None = None):
    """有界型号×参数/条件线索覆盖;只改 opt-in 名额,不修改重排分或推断条件满足。"""
    coverage = coverage if coverage is not None else _EvidenceCoverage(query)
    slots = coverage.slots
    if len(slots) < 2:
        return picked
    query_models = {slot.model for slot in slots if slot.model}
    page_keys, page_texts, identities = {}, {}, {}
    available = set()
    for key, _ in picked:
        page_keys[key], page_texts[key], identities[key] = coverage.page(key, cands)
        available.update(identities[key])

    def matches(key, model):
        if not model:
            return True
        actual = identities[key]
        if model in available:
            return model in actual
        return (len(model.removeprefix("model:")) >= 5
                and any(value.startswith(model) for value in actual if value.startswith("model:")))

    groups = []
    for slot in slots:
        eligible = [(item, query_lex.slot_score(slot, page_keys[item[0]], page_texts[item[0]]))
                    for item in picked if matches(item[0], slot.model)]
        eligible = [(item, score) for item, score in eligible if score > 0]
        eligible.sort(key=lambda pair: -pair[1])
        if eligible:
            strongest = eligible[0][1]
            groups.append(collections.deque(item for item, score in eligible if score == strongest))
    if len(groups) < 2:
        return _balance_models(picked, cands.rows, query) if len(query_models) > 1 else picked
    selected, seen = [], set()
    # 每槽只保一份当前排序中最靠前的证据,剩余名额恢复原相关性排序。
    for group in groups:
        if any(item[0] in seen for item in group):
            continue
        if group:
            item = group.popleft()
            selected.append(item)
            seen.add(item[0])
    remainder = [item for item in picked if item[0] not in seen]
    if len(query_models) > 1:
        remainder = _balance_models(remainder, cands.rows, query)
    return selected + remainder


# ==================== 结果缓存 ====================

_RESULT_CACHE: "collections.OrderedDict[tuple, tuple[float, list, dict]]" = collections.OrderedDict()

# 影响检索结果的可调项。这些值进入缓存键:否则在设置页调参后,最长 query_cache_ttl
# 秒内仍返回旧参数算出的结果(实测:改 snippet_width 后片段长度不变、改 rrf_k 后
# 分数不变),用户会以为设置没生效。改动配置时另需 reset_cache(),双保险。
_CACHE_PARAM_KEYS = (
    "rrf_k", "substring_bonus_rank", "cand_mult", "cand_mult_category", "cand_floor",
    "rerank_pool_mult", "rerank_pool_floor", "rerank_rank_weight", "rerank_tie_tolerance",
    "snippet_width", "window_stride_div",
    "num_unit_bonus", "toc_scan_chars", "penalty_cover", "penalty_toc_rev",
    "block_sim_threshold", "rerank_on_window", "rerank_meta",
    "reranker_model", "embed_model", "embed_input_type_query", "embed_dimensions",
    # 向量分区选择同样改变结果:换优先级/排除后必须重算,否则会返回旧分区的排序
    "vector_models_priority", "vector_models_exclude",
)

# `structured` is a request-scoped opt-in rather than a persisted setting, so
# it is included explicitly in the cache key below instead of this config list.


def _params_fingerprint() -> tuple:
    return tuple(config.get(k) for k in _CACHE_PARAM_KEYS)


def reset_cache() -> None:
    """清空全部进程内缓存:结果、查询向量、覆盖率、投影表和实体桥。

    配置变更、索引替换后必须调用。投影表也在这里清 —— 它虽按 table.version
    失效,但**导入数据包**时新索引的 version 可能恰好等于旧的(两个独立 lance
    目录各自从 0 起算),那样会继续用旧包的文本做子串召回。`library.reset_table()`
    解决的是表句柄,不涉及本模块的缓存,两者要成对。
    """
    global _PROJ_CACHE
    _RESULT_CACHE.clear()
    _EMBED_CACHE.clear()
    _COV_CACHE.clear()
    _PROJ_CACHE = None
    from . import entity
    entity.reset_cache()


def _cache_key(table, query, category, top_k, mode, rerank, file, max_per_doc, structured=False):
    return (table.version, query, category or "", top_k, mode, bool(rerank),
            file or "", max_per_doc or 0, bool(structured), _params_fingerprint())


def _cache_get(key):
    hit = _RESULT_CACHE.get(key)
    if hit is None:
        return None
    ts, out, diag = hit
    if time.time() - ts > config.get("query_cache_ttl"):
        _RESULT_CACHE.pop(key, None)
        return None
    _RESULT_CACHE.move_to_end(key)
    return out, diag


def _cache_put(key, out, diag):
    if config.get("query_cache_ttl") <= 0 or config.get("query_cache_size") <= 0:
        return
    _RESULT_CACHE[key] = (time.time(), out, diag)
    _RESULT_CACHE.move_to_end(key)
    while len(_RESULT_CACHE) > config.get("query_cache_size"):
        _RESULT_CACHE.popitem(last=False)


# ==================== 主流程 ====================

def _finish_diagnostics(diag: dict, candidates: int, returned: int):
    messages = {
        "fts": "全文检索失败,请检查本地全文索引",
        "substring": "型号子串检索失败,请检查本地文本索引",
        "vector:index_unavailable": "向量库不可用,请检查本地索引",
        "vector:no_partition": "没有选中的向量分区,请检查模型分区配置",
        "vector:partition_unavailable": "选中的向量分区无法打开",
        "vector:embedding_failed": "本次查询嵌入失败,请检查模型配置及真实调用日志",
        "vector:dimension_failed": "查询向量维度与分区契约不匹配",
        "vector:search_failed": "向量检索失败,请检查本地分区",
        "vector:low_coverage": "向量分区覆盖率低于配置下限",
        "structured": "结构化实体检索失败,已使用其他检索通道",
        "rerank": "本次重排失败,已使用融合排序",
    }
    degraded = list(dict.fromkeys(diag.get("degraded", [])))
    diag["degraded"] = degraded
    diag["counts"] = {"candidates": candidates, "returned": returned}
    diag["warnings"] = [{"code": code.upper().replace(":", "_"),
                         "message": messages.get(code, "检索通道降级")}
                        for code in degraded]
    diag["notice"] = "; ".join(item["message"] for item in diag["warnings"])


def search(table, query: str, category: str | None = None, top_k: int = 5,
           mode: str = "mixed", rerank: bool = True, file: str | None = None,
           max_per_doc: int = 0, diagnostics: dict | None = None,
           structured: bool = False) -> list[dict]:
    """混合检索,返回命中列表。

    file        按文件路径子串限定检索范围(如 "QMC6309")
    max_per_doc 同一文件最多返回几条(0 = 用配置值)
    diagnostics 可选 out 参数,写入降级路径与候选计数
    """
    diag = diagnostics if diagnostics is not None else {}
    degraded: list[str] = []
    diag["degraded"] = degraded
    max_per_doc = max_per_doc or config.get("max_per_doc")

    ckey = _cache_key(table, query, category, top_k, mode, rerank, file, max_per_doc, structured)
    cached = _cache_get(ckey)
    if cached is not None:
        out, cdiag = cached
        diag.update(cdiag)
        diag["cached"] = True
        return [dict(x) for x in out]
    diag["cached"] = False

    cands = _Candidates(config.get("rrf_k"), config.get("substring_bonus_rank"))
    limit = max(top_k * (config.get("cand_mult_category") if category
                         else config.get("cand_mult")), config.get("cand_floor"))
    if mode in ("mixed", "fts"):
        _channel_fts(table, query, limit, category, file, cands, degraded)
        _channel_substring(table, query, limit, category, file, cands, degraded)
    if mode in ("mixed", "vector"):
        _channel_vector(table, query, limit, category, file, cands, degraded, diag)
    if structured:
        _channel_structured(table, query, limit, category, file, cands, degraded, diag)

    if not cands:
        _finish_diagnostics(diag, 0, 0)
        return []

    pool = max(top_k * config.get("rerank_pool_mult"), config.get("rerank_pool_floor"))
    ranked = cands.top(len(cands.scores))
    coverage = _EvidenceCoverage(query) if structured else None
    if structured:
        ranked = _cover_evidence(ranked, cands, query, coverage)
    source_aliases: dict = {}
    # 先折叠内容副本,否则副本先占满 pool 再被删会白白丢掉其它证据页。
    picked = _pick_latest(ranked, cands.rows, cands.scores, query, source_aliases)[:pool]

    evidence_by_key = None
    if structured:
        from . import evidence
        evidence_by_key = evidence.Bundles(cands.chunks, query)
    rerank_scores: dict[tuple, float] = {}
    if rerank and picked:
        try:
            picked, rerank_scores = _rerank_and_order(picked, cands.rows, query, evidence_by_key)
        except Exception as e:
            degraded.append("rerank")
            log.warning("rerank 失败: %s", e)

    if structured:
        picked = _cover_evidence(picked, cands, query, coverage)
    out = _build_results(picked, cands, rerank_scores, query, top_k, max_per_doc, evidence_by_key, source_aliases)
    _finish_diagnostics(diag, len(picked), len(out))
    if not diag["degraded"]:
        _cache_put(ckey, [dict(x) for x in out],
                   {k: v for k, v in diag.items() if k != "cached"})
    return out


def _structured_facts(chunks: list[dict], query: str) -> list[dict]:
    from . import entity, table_facts
    signals = {key for key in entity.extract_entities(query, query=True) if not key.startswith("model:")}
    facts, seen = [], set()
    query_with_aliases = query + " " + " ".join(key.split(":", 1)[1].replace("_", " ") for key in signals)
    for chunk in chunks:
        if chunk.get("uid") in seen:
            continue
        seen.add(chunk.get("uid"))
        candidates = table_facts.extract(chunk, query=query_with_aliases if signals else "", max_facts=4)
        for fact in candidates:
            fact["source"].update(file=chunk["file"], page=int(chunk["page"]) + 1)
            if fact not in facts:
                facts.append(fact)
            if len(facts) >= 3:
                return facts
    return facts


def _build_results(picked, cands: _Candidates, rerank_scores: dict, query: str,
                   top_k: int, max_per_doc: int, evidence_by_key: dict | None = None,
                   source_aliases: dict | None = None) -> list[dict]:
    """按页去重、限制同文件条数,并组装返回结构。"""
    per_doc: dict[str, int] = {}
    out: list[dict] = []
    for k, _ in picked:
        if max_per_doc and per_doc.get(k[0], 0) >= max_per_doc:
            continue
        per_doc[k[0]] = per_doc.get(k[0], 0) + 1
        row = cands.rows[k]
        item = {
            "file": row["file"],
            "page": int(row["page"]) + 1,
            "category": row["category"],
            "model_no": row["model_no"],
            "product": _product_label(row["file"]),
            "kind": "md" if str(row["file"]).lower().endswith((".md", ".markdown")) else "pdf",
            "c_id": row["c_id"],
            "version": row.get("version", ""),
            "score": round(cands.scores[k], _SCORE_DECIMALS),
            "snippet": "" if evidence_by_key is not None else page_snippet(cands.chunks.get(k, [row]), query),
            "snippet_ref": {} if evidence_by_key is not None else snippet_reference(cands.chunks.get(k, [row]), query),
        }
        if evidence_by_key is not None:
            bundle = evidence_by_key[k]
            item["snippet"] = bundle["text"]
            item["evidence_refs"] = bundle["references"]
            item["structured_facts"] = _structured_facts(cands.chunks[k], query)
            if bundle["references"]:
                item["snippet_ref"] = dict(bundle["references"][0])
            else:
                item["snippet_ref"] = snippet_reference(cands.chunks.get(k, [row]), query)
        if source_aliases and k in source_aliases:
            item["source_aliases"] = source_aliases[k]["items"]
            item["source_aliases_omitted"] = source_aliases[k]["omitted"]
        if k in cands.traces:
            item["retrieval_trace"] = dict(cands.traces[k])
        if k in rerank_scores:
            item["rerank_score"] = round(rerank_scores[k], _SCORE_DECIMALS)
        out.append(item)
        if len(out) >= top_k:
            break
    return out
