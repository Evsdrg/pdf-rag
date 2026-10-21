"""配置中心。

分两层:
* **环境/路径类**(部署相关,不暴露给前端):密钥(嵌入/OCR)、根目录、索引路径、
  MCP 开关、管理令牌。从项目根 .env 读取,改动需重启。
* **可调参数**(SETTINGS):检索融合、片段、排序、缓存、外部接口、文档提取、
  索引吞吐、OCR 后端。 .env 提供初始值,前端可在运行时覆盖;覆盖持久化到
  data/settings.json。

调用方统一用 get("name") 读取可调参数,前端改动即时生效,
不需要重启进程,也不必把参数一路透传。
"""
import json
import os
import threading
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# ---------- 环境类(部署相关) ----------

# 默认值按**仓库内布局**定位:交付包解压到任意路径都能直接跑,不必先改配置。
# 指向别处(如手册放在别的盘)时在 .env 里给 PDF_ROOT / DB_PATH 覆盖即可。
# 用 `or` 而非 getenv 默认值:.env 里 "PDF_ROOT="(空值)也算留空,须回退包内布局,
# 与 DEPLOY.md「留空即用包内布局」的承诺一致(getenv 只对"变量不存在"生效)。
PDF_ROOT = os.getenv("PDF_ROOT") or str(ROOT / "pdf")
DB_PATH = os.getenv("DB_PATH") or str(ROOT / "index.lance")

# 嵌入服务密钥始终只从环境读取,绝不入库、不入包、不进前端。
EMBED_API_KEY = os.getenv("EMBED_API_KEY", "")

# OCR 远程服务的密钥同理:只从环境读。OCR 的地址/模型/提示词已进注册表可前端调,
# 但密钥绝不进 —— 与 EMBED_API_KEY 同一条边界。
OCR_API_KEY = os.getenv("OCR_API_KEY", "")

# 管理接口令牌:为空时 /api/admin/* 全部返回 403(默认关闭)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

# MCP 是否挂载进后端进程(单容器单进程,省一个 Python
# 进程的内存)。默认开启:后端启动时把 MCP 应用挂在 /mcp 路径,与 HTTP API 同端口(8100)。
# 设 MCP_INPROC=0 则后端不挂 MCP,改为独立进程跑 server.py(旧的 8101 双容器形态)。
MCP_INPROC = os.getenv("MCP_INPROC", "1") not in ("0", "false", "False")
MCP_PATH = os.getenv("MCP_PATH", "/mcp")

SKIP_DIRS = {".venv", ".git", "__pycache__", ".uv"}
SETTINGS_FILE = ROOT / "data" / "settings.json"


# ---------- 可调参数注册表 ----------

class Spec:
    """一个可调项:类型、默认值、取值范围与说明。kind 决定前端控件类型。

    label 是面向人的中文名(前端默认显示它);name 是机器标识符
    (settings.json 的键、API 参数),永不显示给用户除非开"显示变量名"。
    """

    __slots__ = ("name", "label", "kind", "default", "group", "desc", "env_key", "lo", "hi")

    def __init__(self, name, label, kind, default, group, desc, env_key=None, lo=None, hi=None):
        self.name = name
        self.label = label
        self.kind = kind
        self.default = default
        self.group = group
        self.desc = desc
        self.env_key = env_key
        self.lo = lo
        self.hi = hi

    def coerce(self, raw):
        """把外部输入转成正确类型并校验范围。"""
        if self.kind == "bool":
            if isinstance(raw, bool):
                return raw
            return str(raw).strip().lower() in ("1", "true", "yes", "on")
        if self.kind == "int":
            val = int(raw)
        elif self.kind == "float":
            val = float(raw)
        else:
            return str(raw)
        if self.lo is not None and val < self.lo:
            raise ValueError(f"「{self.label}」不能小于 {self.lo}")
        if self.hi is not None and val > self.hi:
            raise ValueError(f"「{self.label}」不能大于 {self.hi}")
        return val

    def initial(self):
        """初始值:优先 .env,其次内置默认值。"""
        if self.env_key and os.getenv(self.env_key) is not None:
            return self.coerce(os.getenv(self.env_key))
        return self.default


_SPECS = [
    # ---- 嵌入服务 ----
    # 与向量强绑定:换模型会使已有向量与新查询向量不在同一空间,检索静默变差。
    # 因此这几项随数据包一起导出导入,让数据自带"解释自己所需的模型"。
    # **密钥不在此列** —— 密钥只从环境读取,绝不写入配置文件或数据包。
    Spec("embed_base_url", "嵌入服务地址", "str", "https://api.siliconflow.cn/v1", "嵌入服务",
         "嵌入/重排接口的服务地址。随数据包导出,导入时可一并应用",
         "EMBED_BASE_URL"),
    Spec("embed_model", "嵌入模型", "str", "Qwen/Qwen3-Embedding-8B", "嵌入服务",
         "嵌入模型名。换模型会使已有向量不可比,导入前按此校验", "EMBED_MODEL"),
    Spec("reranker_model", "重排模型", "str", "qwen3-reranker-8b", "嵌入服务",
         "重排模型名。不影响向量可比性,只影响结果排序", "RERANKER_MODEL"),
    # Cohere 系嵌入模型要求区分"建库"与"查询"两种输入类型,且两者产生的向量不同空间,
    # 必须配对使用。留空则不发送该字段(OpenAI 兼容模型如 qwen3 系不需要)。
    # 这两项属于嵌入契约的一部分,因此随数据包一起导出导入。
    Spec("embed_input_type_doc", "建库输入类型", "str", "", "嵌入服务",
         "建索引时的 input_type,如 search_document。留空则不发送(仅 Cohere 系模型需要)",
         "EMBED_INPUT_TYPE_DOC"),
    Spec("embed_input_type_query", "查询输入类型", "str", "", "嵌入服务",
         "检索时的 input_type,如 search_query。留空则不发送", "EMBED_INPUT_TYPE_QUERY"),
    # 显式声明输出维度,不依赖服务商默认值。上游默认值是可变的(Qwen3-8B 原生 4096,
    # 实测某服务商默认返回 768),一旦默认值变化,查询向量就会与索引维度不符;
    # 高维查低维索引时 lance 会静默截断,不会报错。
    # 0 = 不发送该字段(仅用于兼容不支持 dimensions 的服务商)。
    Spec("embed_dimensions", "向量维度", "int", 768, "嵌入服务",
         "嵌入输出维度,必须与索引一致。0 = 不发送该参数,由服务商决定(不推荐)",
         "EMBED_DIMENSIONS", 0, 4096),

    # ---- 向量分区 ----
    # 一个块可以同时存有多个模型的向量(用户先后用不同模型索引过)。检索时每个块
    # 只用一个模型的向量 —— 不同模型的向量空间不可比,混在一次距离计算里没有意义。
    # 这两项决定"用哪个模型、不用哪个",格式为逗号分隔的分区 slug 或模型名。
    Spec("vector_models_priority", "向量模型优先级", "str", "", "向量分区",
         "逗号分隔的优先顺序(分区 slug 或模型名)。一个块有多个模型的向量时用列表中"
         "第一个命中的;留空 = 只用当前配置的模型", "VECTOR_MODELS_PRIORITY"),
    Spec("vector_models_exclude", "排除的向量模型", "str", "", "向量分区",
         "逗号分隔、不参与检索的分区 slug 或模型名。与优先级冲突时以排除为准。"
         "被排除模型的块仍可被全文/子串通道召回", "VECTOR_MODELS_EXCLUDE"),
    Spec("vector_coverage_min", "向量覆盖率下限", "float", 1.0, "向量分区",
         "分区覆盖率低于此值时向量通道标记降级(部分块没有该模型的向量,候选池缩水)。"
         "1.0 = 必须全覆盖才算可信;0 = 不检查", "VECTOR_COVERAGE_MIN", 0.0, 1.0),

    # ---- 检索融合 ----
    Spec("rrf_k", "融合平滑常数", "int", 60, "检索融合",
         "RRF 融合常数:第 r 名的贡献为 1/(rrf_k+r),越大则名次差异越平缓",
         "RRF_K", 1, 1000),
    Spec("substring_bonus_rank", "型号召回名次", "int", 5, "检索融合",
         "精确子串(型号)召回折算成的名次,越小权重越高",
         "SUBSTRING_BONUS_RANK", 0, 60),
    Spec("cand_mult", "候选放大倍数", "int", 8, "检索融合",
         "每通道候选数 = top_k × 该倍数(不按类别过滤时)", "CAND_MULT", 1, 50),
    Spec("cand_mult_category", "类别候选倍数", "int", 10, "检索融合",
         "每通道候选数 = top_k × 该倍数(按类别过滤时)", "CAND_MULT_CATEGORY", 1, 50),
    Spec("cand_floor", "候选数下限", "int", 80, "检索融合",
         "每通道候选数下限。过浅会让答案页进不了重排池(实测大手册如 MSM8916 的"
         "答案页单通道第 6 名但融合后进不了前 40,提到 80 后 snippet@5 +14pp)",
         "CAND_FLOOR", 5, 500),
    Spec("rerank_pool_mult", "重排池倍数", "int", 8, "检索融合",
         "进入重排的候选数 = top_k × 该倍数", "RERANK_POOL_MULT", 1, 50),
    Spec("rerank_pool_floor", "重排池下限", "int", 64, "检索融合",
         "进入重排的候选数下限", "RERANK_POOL_FLOOR", 5, 300),
    Spec("rerank_rank_weight", "重排名次权重", "float", 0.0, "检索融合",
         "最终排序 = 召回名次与重排名次的倒数排名融合,该值是重排项的权重。"
         "0 = 纯重排分排序。实测(55 条评测)任何 >0 的取值都会让参数值类查询"
         "的 top1 被概述/目录页抢占(58%→38%),仅当更换重排模型后可重测",
         "RERANK_RANK_WEIGHT", 0.0, 10.0),
    Spec("rerank_tie_tolerance", "重排平局阈值", "float", 0.0, "检索融合",
         "相邻两页重排分差小于该值视为平局,平局时查询型号与文件身份匹配者在前。"
         "背景:同族手册两页的重排分差(实测 0.006)低于重排自身抖动(0.004-0.008)。"
         "实测(55 条评测)0.02-0.05 无净收益(查询不含型号时无从裁决);"
         "换用含型号的查询方式后可重测。0 = 禁用", "RERANK_TIE_TOLERANCE", 0.0, 0.5),

    # ---- 片段 ----
    # 宽度 900 是实测结果:表格页的答案值常在页文本 1300-2000 字符处,600 宽的窗口
    # 框不住(55 条评测 snippet@1 58%→62%、snippet@5 73%→91%)。
    Spec("snippet_width", "片段宽度", "int", 900, "片段",
         "返回片段的目标宽度(字符)。片段取查询感知窗口而非块首", "SNIPPET_WIDTH", 120, 3000),
    Spec("window_stride_div", "滑窗精细度", "int", 4, "片段",
         "滑窗步长 = 片段宽度 ÷ 该值,越小越精细也越慢", "WINDOW_STRIDE_DIV", 1, 16),
    Spec("num_unit_bonus", "参数值加分", "float", 1.5, "片段",
         "窗口含「数字+单位」时的加分:参数值几乎总以这种形式出现",
         "NUM_UNIT_BONUS", 0.0, 10.0),
    Spec("toc_scan_chars", "目录页扫描字数", "int", 900, "片段",
         "判定封面/目录/修订史页时扫描的页首字符数", "TOC_SCAN_CHARS", 100, 5000),

    # ---- 排序 ----
    Spec("penalty_cover", "封面惩罚系数", "float", 0.90, "排序",
         "文档首页(封面)的排序惩罚系数,1.0 表示不惩罚", "PENALTY_COVER", 0.1, 1.0),
    Spec("penalty_toc_rev", "目录页惩罚系数", "float", 0.75, "排序",
         "目录/修订史页的排序惩罚系数", "PENALTY_TOC_REV", 0.1, 1.0),
    Spec("block_sim_threshold", "同文档判定阈值", "float", 0.4, "排序",
         "判定两份文件为同一文档的块文本相似度阈值(型号须先一致)",
         "BLOCK_SIM_THRESHOLD", 0.0, 1.0),
    Spec("max_per_doc", "单文件条数上限", "int", 0, "排序",
         "同一文件最多返回几条。0 = 不限。实测收紧会挤掉正确文件的名额",
         "MAX_PER_DOC", 0, 50),
    Spec("rerank_on_window", "窗口送重排", "bool", True, "排序",
         "只把最相关窗口送重排(而非整块):提升答案命中并大幅降低重排载荷",
         "RERANK_ON_WINDOW"),
    Spec("rerank_meta", "重排带身份行", "bool", True, "排序",
         "送重排时前置一行文档身份(文件名/型号/类别),用于区分同族文档",
         "RERANK_META"),

    # ---- 缓存 ----
    Spec("query_cache_ttl", "结果缓存时长", "float", 600.0, "缓存",
         "相同查询的结果缓存秒数。0 = 关闭", "QUERY_CACHE_TTL", 0.0, 86400.0),
    Spec("query_cache_size", "结果缓存条数", "int", 256, "缓存",
         "结果缓存条数上限", "QUERY_CACHE_SIZE", 0, 100000),
    Spec("embed_cache_size", "查询向量缓存条数", "int", 512, "缓存",
         "查询向量本地缓存条数。命中后不再请求嵌入接口。0 = 关闭", "EMBED_CACHE_SIZE", 0, 100000),

    # ---- 外部接口 ----
    Spec("http_timeout", "接口总超时", "float", 180.0, "外部接口",
         "调用嵌入/重排接口的总超时(秒)", "HTTP_TIMEOUT", 5.0, 600.0),
    Spec("http_connect_timeout", "连接超时", "float", 15.0, "外部接口",
         "建立连接的超时(秒)", "HTTP_CONNECT_TIMEOUT", 1.0, 120.0),
    Spec("retry_attempts", "失败重试次数", "int", 4, "外部接口",
         "接口失败重试次数。服务商密集请求下会返回 403/429", "RETRY_ATTEMPTS", 1, 10),
    Spec("retry_base_delay", "重试退避基数", "float", 1.0, "外部接口",
         "重试基础退避时长(秒),按 2^i 递增", "RETRY_BASE_DELAY", 0.0, 30.0),
    Spec("embed_attempts", "嵌入重试次数", "int", 5, "外部接口",
         "建索引时每批嵌入的重试次数。限流(403/429)按分钟计,退避比普通失败长得多",
         "EMBED_ATTEMPTS", 1, 12),
    Spec("http_keepalive", "连接池保活数", "int", 16, "外部接口",
         "连接池保活连接数。复用连接可省掉每次 TLS 握手", "HTTP_KEEPALIVE", 0, 128),
    Spec("http_max_conn", "连接池上限", "int", 32, "外部接口",
         "连接池最大连接数", "HTTP_MAX_CONN", 1, 256),

    # ---- 文档提取 ----
    Spec("chunk_max_chars", "分块最大字数", "int", 3000, "文档提取",
         "分块最大字符数", "CHUNK_MAX_CHARS", 200, 20000),
    Spec("chunk_overlap_chars", "分块重叠字数", "int", 150, "文档提取",
         "相邻块的重叠字符数,缓解边界信息断裂", "CHUNK_OVERLAP_CHARS", 0, 2000),
    Spec("ocr_min_chars", "OCR 触发字数", "int", 200, "文档提取",
         "单页提取文本低于该值时触发 OCR 兜底", "OCR_MIN_CHARS", 0, 5000),
    Spec("min_chars_per_page", "每页字数告警线", "int", 100, "文档提取",
         "整份文档平均每页字符低于该值时告警(说明提取与 OCR 都没成功)",
         "MIN_CHARS_PER_PAGE", 0, 5000),
    Spec("ocr_dpi", "OCR 渲染精度", "int", 200, "文档提取",
         "渲染扫描页送 OCR 的 DPI", "OCR_DPI", 72, 600),
    Spec("ocr_timeout", "OCR 调用超时", "float", 300.0, "文档提取",
         "调用本地 OCR 服务的超时(秒)", "OCR_TIMEOUT", 10.0, 1800.0),
    Spec("page_max_chars", "单页返回上限", "int", 8000, "文档提取",
         "read_page 返回单页文本的字符上限", "PAGE_MAX_CHARS", 500, 200000),
    Spec("table_min_ratio", "表格有效率下限", "float", 0.10, "文档提取",
         "表格有效内容率低于该值视为误检并丢弃", "TABLE_MIN_RATIO", 0.0, 1.0),

    # ---- 索引吞吐 ----
    Spec("embed_batch", "嵌入批量大小", "int", 64, "索引吞吐",
         "每批送嵌入接口的文本块数。服务商限流时调小", "EMBED_BATCH", 1, 512),
    Spec("embed_workers", "嵌入并发数", "int", 8, "索引吞吐",
         "嵌入并发线程数。限流(403/429)严重时调小", "EMBED_WORKERS", 1, 32),
    Spec("extract_workers", "提取进程数", "int", 4, "索引吞吐",
         "PDF 提取进程数。受 CPU 与内存约束(每子进程约 150MB)", "EXTRACT_WORKERS", 1, 16),

    # ---- OCR 后端 ----
    # 密钥(OCR_API_KEY)与 EMBED_API_KEY 同理:只从环境读,绝不进本注册表。
    Spec("ocr_backend", "OCR 后端类型", "str", "local", "OCR 后端",
         "扫描页兜底来源:local=本机 PaddleOCR 服务,remote=OpenAI 兼容视觉模型 API",
         "OCR_BACKEND"),
    Spec("ocr_url", "本机 OCR 地址", "str", "http://127.0.0.1:8900", "OCR 后端",
         "local 后端的服务地址(/ocr 与 /health)", "OCR_URL"),
    Spec("ocr_api_base", "远程 OCR 地址", "str", "", "OCR 后端",
         "remote 后端的 API 根地址,如 https://api.example.com/v1", "OCR_API_BASE"),
    Spec("ocr_model", "远程 OCR 模型", "str", "paddleocr-vl-1.6", "OCR 后端",
         "remote 后端的模型名。实测:OCR_PROMPT=OCR 时 hunyuan-ocr 输出 markdown(标题+表格)、paddleocr-vl 走版面解析",
         "OCR_MODEL"),
    Spec("ocr_prompt", "OCR 提示词", "str", "OCR", "OCR 后端",
         '送 remote 模型的提示词。默认 "OCR" 对两模型均最优;hunyuan 的 "doc_parse" 会改写原文,检索场景勿用',
         "OCR_PROMPT"),
]

SPECS: dict[str, Spec] = {s.name: s for s in _SPECS}
GROUPS: list[str] = list(dict.fromkeys(s.group for s in _SPECS))

_lock = threading.Lock()
_overrides: dict = {}
_loaded = False


def _load():
    global _overrides, _loaded
    if _loaded:
        return
    with _lock:
        if _loaded:
            return
        try:
            _overrides = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _overrides = {}
        _loaded = True


def reload():
    """丢弃内存里的覆盖值,从磁盘重新读取。

    配置文件被**本进程之外**改过时(导入数据包会把包内 settings.json 直接复制
    到位)必须调用:否则 `_loaded` 仍为真,进程继续用旧值;更糟的是之后任何一次
    `set_many()` 都会把旧值 `_persist()` 回磁盘,把刚导入的配置整个覆盖掉。
    表现是"界面说已恢复配置,但所有参数都没变",且重启前一直如此。

    读-放-读全过程在锁内完成:`_lock` 是普通 Lock 且 _load 只在未加载时才取锁,
    这里直接内联读取;若先清空标志再出锁,并发 get() 会短暂看到空覆盖值、
    回落到默认配置。
    """
    global _overrides, _loaded
    with _lock:
        try:
            _overrides = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _overrides = {}
        _loaded = True


def get(name: str):
    """读取可调参数:运行时覆盖 > .env > 默认值。"""
    _load()
    spec = SPECS.get(name)
    if spec is None:
        raise KeyError(f"未知配置项: {name}")
    if name in _overrides:
        try:
            return spec.coerce(_overrides[name])
        except (TypeError, ValueError):
            pass                      # 覆盖值损坏时回退,不让坏配置拖垮检索
    return spec.initial()


def _persist():
    if _overrides:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = SETTINGS_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(_overrides, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(SETTINGS_FILE)
    else:
        SETTINGS_FILE.unlink(missing_ok=True)


def set_many(values: dict) -> dict:
    """批量写入覆盖值并持久化,返回生效后的完整快照。"""
    _load()
    with _lock:
        for name, raw in values.items():
            if name not in SPECS:
                raise KeyError(f"未知配置项: {name}")
            _overrides[name] = SPECS[name].coerce(raw)
        _persist()
    return snapshot()


def override_local(values: dict) -> None:
    """**只在本进程生效**的覆盖:改内存,不写 data/settings.json。

    给"绕开缓存做测量"这类脚本用。用 set_many 会把评测/调参的临时值持久化 ——
    评测跑完用户的服务配置就被改了(实测过一次:评测把 query_cache_ttl 设为 0,
    结果是线上查询缓存被永久关掉,而这一切没有任何提示)。
    进程退出即失效,所以不需要还原。
    """
    _load()
    with _lock:
        for name, raw in values.items():
            if name not in SPECS:
                raise KeyError(f"未知配置项: {name}")
            _overrides[name] = SPECS[name].coerce(raw)


def reset(names: list[str] | None = None) -> dict:
    """清除覆盖值(全部或指定项),回到 .env/默认值。"""
    _load()
    with _lock:
        if names:
            for n in names:
                _overrides.pop(n, None)
        else:
            _overrides.clear()
        _persist()
    return snapshot()


def snapshot() -> dict:
    """当前全部可调参数 + 元数据,供前端渲染配置面板。"""
    return {
        name: {
            "label": spec.label,
            "value": get(name), "default": spec.default, "kind": spec.kind,
            "group": spec.group, "desc": spec.desc, "env_key": spec.env_key or "",
            "lo": spec.lo, "hi": spec.hi, "overridden": name in _overrides,
        }
        for name, spec in SPECS.items()
    }
