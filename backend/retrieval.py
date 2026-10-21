"""共享检索核心。

流水线:多路召回(FTS / 型号子串 / 向量)→ RRF 融合 → 跨版本去重 → 重排 → 片段。

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
* **多版本合并以型号一致为硬前提**:仅凭标题指纹会误并不同型号 ——
  不少中文 PDF 的元数据标题就是章节名(实测三份不同型号手册标题同为"主要特点")。
"""
import collections
import logging
import os
import re
import time

import httpx
import pyarrow as pa

from . import config
from .doc_utils import product_label as _product_label

log = logging.getLogger("pdfrag.retrieval")

# ---------- 算法常量(不对外暴露,改这里需重跑评测) ----------
# 供子串召回投影的列:不要把 768 维向量列一起物化。
# 必须含 md5 —— 去重依赖它识别"同料号族共用一份手册"(缺了会让去重静默失效)。
_PROJ_COLS = ["text", "file", "page", "category", "model_no", "c_id", "version",
              "title", "md5"]
# 型号 token 的最小长度:太短会把版本号、单位当型号
_MODEL_TOKEN_MIN_LEN = 3
# 中文 2-gram 切分阈值:不超过该长度整体保留,超过则切分
_CJK_WHOLE_MAX = 3
_CJK_GRAM = 2
# 允许中文串切分/英文词提取的查询词形态
_TERM_RE = re.compile(r"[\u4e00-\u9fff]+|[A-Za-z0-9][A-Za-z0-9\-\._]{2,}")
_MODEL_RE = re.compile(r"[A-Za-z0-9]+")
# 参数值几乎总以"数字 + 单位"形式出现,作为窗口定位的正向信号
_NUM_UNIT_RE = re.compile(
    r"\d+(?:\.\d+)?\s*(?:mA|uA|µA|nA|mV|V|MHz|kHz|GHz|Hz|mΩ|kΩ|Ω|mH|uH|nH|pH|dBm|dB|%|G|"
    r"pF|nF|uF|ms|us|ns|s|°C)", re.I)
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
    """查询里可能是元器件型号的 token:含字母与数字、长度达标。"""
    return [tk for tk in _MODEL_RE.findall(query)
            if len(tk) >= _MODEL_TOKEN_MIN_LEN
            and any(c.isdigit() for c in tk) and any(c.isalpha() for c in tk)]


def _query_terms(query: str) -> tuple[list[str], set[str]]:
    """切分查询词。返回 (全部词, 型号类词)。

    中文连续串切 2-gram:不做分词也能对部分匹配给分。否则"发送功率电流"会被当成
    一个整词、必须逐字命中,而文档往往写作"发送功率" —— 中文查询对窗口打分
    几乎不贡献(实测显著拉低片段命中率)。
    """
    models = {t.lower() for t in _model_tokens(query)}
    terms: list[str] = []
    for run in _TERM_RE.findall(query):
        if "\u4e00" <= run[0] <= "\u9fff":
            if len(run) <= _CJK_WHOLE_MAX:
                terms.append(run)
            else:
                terms.extend(run[i:i + _CJK_GRAM] for i in range(len(run) - 1))
        else:
            terms.append(run)
    return terms, models


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
    if _NUM_UNIT_RE.search(seg):
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


# ==================== 页面角色 ====================

def _role_penalty(row: dict) -> float:
    """封面/目录/修订史页的排序惩罚。这类页关键词密度高,天然占优。"""
    if int(row["page"]) == 0:
        return config.get("penalty_cover")
    if _TOC_REV_RE.search(row["text"][:config.get("toc_scan_chars")]):
        return config.get("penalty_toc_rev")
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

_PROJ_CACHE: tuple[int, pa.Table] | None = None


def _proj_table(table) -> pa.Table:
    """按表版本缓存投影表。

    _substring_recall 原先每次 table.to_arrow() 全量物化(含向量列,+78MB),
    而它对查询里每个型号 token 都要调一次,代价被放大数倍。
    """
    global _PROJ_CACHE
    ver = table.version
    if _PROJ_CACHE is None or _PROJ_CACHE[0] != ver:
        full = table.to_arrow()
        try:
            _PROJ_CACHE = (ver, full.select(_PROJ_COLS))
        finally:
            del full
    return _PROJ_CACHE[1]


def _substring_recall(table, term: str, limit: int) -> list[dict]:
    """对 text 列做精确子串召回,补 FTS 的型号前缀匹配盲区。"""
    import pyarrow.compute as pc
    df = _proj_table(table)
    return df.filter(pc.match_substring(df["text"], term)).to_pylist()[:limit]


# ==================== 候选收集 ====================

class _Candidates:
    """候选收集器:页级累加计分,并记录该页的代表块与全部命中块。

    * 页级累加是刻意的(见模块文档):同页多块累加是有效相关性信号。
    * 代表块取"自身得分最高"者 —— 页首块几乎不含答案。
    * 全部命中块供片段跨块取窗口,因为表格常被切到与正文不同的块。
    """

    __slots__ = ("scores", "rows", "chunks", "_best", "_rrf_k", "_bonus_rank")

    def __init__(self, rrf_k: int, bonus_rank: int):
        self.scores: dict[tuple, float] = {}
        self.rows: dict[tuple, dict] = {}
        self.chunks: dict[tuple, list[dict]] = {}
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
            found = _substring_recall(table, term, limit)
        except Exception as e:
            degraded.append("substring")
            log.warning("子串召回失败(%s): %s", term, e)
            continue
        for row in found:
            if _accepts(row, category, file):
                cands.add(row, 0, bonus=True)


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
        degraded.append("vector")
        return
    parts = vecstore.select_partitions(db)
    if not parts:
        degraded.append("vector")
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
            continue
        try:
            vec = embed_query(query, input_type_override=meta.get("input_type_query"),
                              dim_override=meta.get("dim"),
                              model_override=meta.get("model"))
            want = part.schema.field("vector").type.list_size
            if len(vec) != want:
                raise ValueError(
                    f"查询向量维度 {len(vec)} 与分区 {slug} 的 {want} 不符;"
                    f"检查「向量维度」配置(EmbedDimensions)是否与建库时一致")
            found = _apply_filter(part.search(vec, query_type="vector"),
                                  category, file).limit(limit).to_list()
        except Exception as e:
            degraded.append(f"vector:{meta.get('model') or slug}")
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
    if not covered:
        degraded.append("vector")
        log.warning("所有向量分区均未召回;检查分区覆盖率与嵌入服务")
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
            degraded.append("vector")
            log.warning("向量分区覆盖率低于下限 %.0f%%: %s;"
                        "对这些模型补跑一次索引可恢复",
                        min_ratio * 100, ", ".join(low))


# ==================== 跨版本去重 ====================

def _same_document(rows1: list[dict], rows2: list[dict]) -> bool:
    """两份文件是否为"同一文档"。

    判据按强度排列:

    1. **内容 md5 相同 → 同一文档**。厂商常用一份手册覆盖整个料号族
       (实测 MX25R3235F 的 4 个订购料号共用同一 PDF),此时 model_no 各异,
       仅比型号会放行 4 份逐字节相同的候选,结果里全是同一份手册。
    2. **型号一致**是版本合并的硬前提。不能只凭标题指纹:不少中文 PDF 的元数据
       标题是章节名,实测三份不同型号的 LED 手册标题都是"主要特点",仅凭标题
       会把它们并成一组、只留版本号最高者,其余型号被静默删除、永不出现。
    """
    from .doc_utils import title_key, block_sim
    r1, r2 = rows1[0], rows2[0]
    md1, md2 = r1.get("md5") or "", r2.get("md5") or ""
    if md1 and md1 == md2:
        return True
    m1, m2 = r1.get("model_no") or "", r2.get("model_no") or ""
    if not m1 or m1 != m2:
        return False
    t1k, t2k = title_key(r1.get("title", "")), title_key(r2.get("title", ""))
    if t1k and t1k == t2k:
        return True
    threshold = config.get("block_sim_threshold")
    return any(block_sim(a["text"], b["text"]) > threshold for a in rows1 for b in rows2)


def _pick_latest(cands, rows_by_key: dict, scores: dict):
    """同文档多版本合并:每组只保留版本号最高的一份。"""
    from .doc_utils import version_key
    by_file: dict[str, list] = {}
    for k, _ in cands:
        by_file.setdefault(rows_by_key[k]["file"], []).append(k)

    groups: list[list[str]] = []
    for f in by_file:
        for g in groups:
            if _same_document([rows_by_key[k] for k in by_file[g[0]]],
                              [rows_by_key[k] for k in by_file[f]]):
                g.append(f)
                break
        else:
            groups.append([f])

    keep: set = set()
    for g in groups:
        best = max(g, key=lambda f: (version_key(rows_by_key[by_file[f][0]].get("version", "")),
                                     max(scores[k] for k in by_file[f])))
        keep.update(by_file[best])
    return [(k, s) for k, s in cands if k in keep]


# ==================== 重排 ====================

def _rerank_docs(cands, rows_by_key: dict, query: str) -> list[str]:
    """构造送重排器的文本。窗口化可显著降低载荷,前置身份行用于区分同族文档。"""
    docs = [rows_by_key[k]["text"] for k, _ in cands]
    if config.get("rerank_on_window"):
        docs = [make_snippet(d, query) for d in docs]
    if config.get("rerank_meta"):
        docs = [f"{_meta_line(rows_by_key[k])}\n{d}" for (k, _), d in zip(cands, docs)]
    return docs


def _model_identity_match(row: dict, models: set[str]) -> int:
    """查询型号 token 与文档身份(文件名+型号字段)的匹配级别。

    只做**平局裁决**,不做主排序键 —— 文件名/页眉里型号无处不在,当主键会让
    "含型号但内容无关"的页全面胜出(与 _score_window 排除型号 token 同理)。
    返回 2 = 身份里含完整型号 token,0 = 不含。
    """
    if not models:
        return 0
    ident = re.sub(r"[\s_-]+", "",
                   os.path.basename(row.get("file", "")) + " " + row.get("model_no", "")).lower()
    return 2 if any(m in ident for m in models) else 0


def _rerank_and_order(cands, rows_by_key: dict, query: str):
    """重排并排序。返回 (排序后的候选, {key: 重排分})。

    纯重排分排序,外加一道**型号平局裁决**:同族手册两页的重排分差(实测
    0.006,如 EC800M vs EG800Z、74LVC1G04GV vs GW)低于重排自身抖动
    (0.004-0.008),先后本质随机;分差小于 rerank_tie_tolerance 时,查询里
    的型号 token 与文件身份匹配者在前。不要改成召回名次与重排名次的融合
    排序 —— 实测任何融合权重都会让概述页抢走参数值类查询的 top1
    (snippet@1 58%→38%)。
    """
    docs = _rerank_docs(cands, rows_by_key, query)
    rel = _call_reranker(query, docs)
    scores = {cands[i][0]: float(rel[i]) for i in range(len(cands))}
    order = sorted(range(len(cands)),
                   key=lambda i: -(rel[i] * _role_penalty(rows_by_key[cands[i][0]])))
    tol = float(config.get("rerank_tie_tolerance"))
    if tol > 0 and len(order) > 1:
        models = {tk.lower() for tk in _model_tokens(query)}
        if models:
            match = {cands[i][0]: _model_identity_match(rows_by_key[cands[i][0]], models)
                     for i in range(len(cands))}
            adj = [rel[i] * _role_penalty(rows_by_key[cands[i][0]]) for i in range(len(cands))]
            for j in range(len(order) - 1):
                a, b = order[j], order[j + 1]
                if (abs(adj[a] - adj[b]) <= tol and match[cands[b][0]] > match[cands[a][0]]):
                    order[j], order[j + 1] = b, a
    return [cands[i] for i in order], scores


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


def _params_fingerprint() -> tuple:
    return tuple(config.get(k) for k in _CACHE_PARAM_KEYS)


def reset_cache() -> None:
    """清空全部进程内缓存:结果、查询向量、覆盖率、投影表。

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


def _cache_key(table, query, category, top_k, mode, rerank, file, max_per_doc):
    return (table.version, query, category or "", top_k, mode, bool(rerank),
            file or "", max_per_doc or 0, _params_fingerprint())


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

def search(table, query: str, category: str | None = None, top_k: int = 5,
           mode: str = "mixed", rerank: bool = True, file: str | None = None,
           max_per_doc: int = 0, diagnostics: dict | None = None) -> list[dict]:
    """混合检索,返回命中列表。

    file        按文件路径子串限定检索范围(如 "QMC6309")
    max_per_doc 同一文件最多返回几条(0 = 用配置值)
    diagnostics 可选 out 参数,写入降级路径与候选计数
    """
    diag = diagnostics if diagnostics is not None else {}
    degraded: list[str] = []
    diag["degraded"] = degraded
    max_per_doc = max_per_doc or config.get("max_per_doc")

    ckey = _cache_key(table, query, category, top_k, mode, rerank, file, max_per_doc)
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

    if not cands:
        diag["counts"] = {"candidates": 0, "returned": 0}
        return []

    pool = max(top_k * config.get("rerank_pool_mult"), config.get("rerank_pool_floor"))
    picked = _pick_latest(cands.top(pool), cands.rows, cands.scores)

    rerank_scores: dict[tuple, float] = {}
    if rerank and picked:
        try:
            picked, rerank_scores = _rerank_and_order(picked, cands.rows, query)
        except Exception as e:
            degraded.append("rerank")
            log.warning("rerank 失败: %s", e)

    out = _build_results(picked, cands, rerank_scores, query, top_k, max_per_doc)
    diag["counts"] = {"candidates": len(picked), "returned": len(out)}
    if degraded:
        diag["notice"] = ("降级路径: " + "、".join(sorted(set(degraded)))
                          + " —— 结果可能不完整,请检查嵌入服务连通性")
    else:
        # 只缓存完整结果:降级可能是接口的暂时故障,不该被缓存住
        _cache_put(ckey, [dict(x) for x in out],
                   {"degraded": [], "counts": diag["counts"], "notice": ""})
    return out


def _build_results(picked, cands: _Candidates, rerank_scores: dict, query: str,
                   top_k: int, max_per_doc: int) -> list[dict]:
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
            "snippet": page_snippet(cands.chunks.get(k, [row]), query),
        }
        if k in rerank_scores:
            item["rerank_score"] = round(rerank_scores[k], _SCORE_DECIMALS)
        out.append(item)
        if len(out) >= top_k:
            break
    return out
