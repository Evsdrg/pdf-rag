# PDF-RAG

本地元器件手册检索：对 PDF/Markdown 手册库做**语义向量 + 全文(FTS) + 子串**三路混合检索
（RRF 融合 → 同文档去重 → 可选重排），支持表格识别与扫描页 OCR 兜底，通过 **Web 界面**、
**MCP 工具**、**REST API** 三种方式对外提供服务。

```
                   ┌──────────────┐
   浏览器 ────────▶ │  Web UI      │ Vue 3 + naive-ui（打进镜像，由后端托管）
                   ├──────────────┤
   MCP 客户端 ─────▶ │  /mcp        │ 8 个 pdf_rag_* 工具（默认内嵌进后端进程）
   pi 等 REST ─────▶ │  /api/*      │ 与 MCP 共用 backend/library.py 的实体逻辑
                   ├──────────────┤
                   │ LanceDB      │ 向量 + FTS 全文索引
                   └──────────────┘
```

## 快速上手

```bash
cp .env.example .env        # 至少填 EMBED_API_KEY
uv sync                     # 装依赖（Python 3.13）
uv run run_backend.py       # http://127.0.0.1:8100（含 Web UI 与 MCP）
```

手册放进 `pdf/`（或 `.env` 的 `PDF_ROOT`），然后在 Web「索引状态」页点**增量索引**。

> **部署**（另起机器 / 容器）：
> - 容器、生产（当前 NAS 形态）→ **[DEPLOY-NAS.md](DEPLOY-NAS.md)**
> - 裸机、交付包解压 → **[DEPLOY.md](DEPLOY.md)**

## 目录结构

```
backend/
  main.py         FastAPI 应用与全部 HTTP 接口
  config.py       配置中心：环境类常量 + 可调参数注册表（Spec，含中文 label）
  library.py      读页、精确检索、元数据缓存的共享实现（MCP 与 HTTP 共用）
  retrieval.py    检索核心：三路召回 + RRF 融合 + 去重 + 重排 + 片段定位
  ingest.py       索引构建（多进程提取 + 批量嵌入）
  doc_utils.py    PDF/Markdown 文本提取、表格 markdown 化
  ocr.py          OCR 后端抽象（local Paddle / remote VLM）+ 调用状态记录
  bundle.py       数据包（.tar.zst）导出/导入
server.py         MCP 服务（默认内嵌；MCP_INPROC=0 时独立进程）
ocr_service.py    本机 OCR 服务（独立进程，依赖 ocr-env，可选）
run_backend.py    后端守护：崩溃自愈 + 单例锁
eval_retrieval.py 检索质量评测
eval_queries.json 评测集（55 条）
tools/            开发期诊断与维护脚本（见下）
web/              前端源码（Vue 3 + Vite + naive-ui）
index.lance/      LanceDB 索引（运行时生成）
data/             运行时配置覆盖值与导出包（运行时生成）
```
运行时会自动生成 `logs/`、`run_state.json`、`data/settings.json`、`data/exports/`，
这些都不入版本库，删掉不影响启动。

## 环境要求

- **Python 3.13** + [uv](https://docs.astral.sh/uv/)
- **Node.js**（仅前端开发/构建；镜像里已有构建好的 `web/dist`）
- **嵌入 / 重排服务**：OpenAI 兼容的 `/v1/embeddings` 与 `/v1/rerank`
- **OCR（可选）**：本机 Paddle 需独立 `ocr-env`（约 4.9GB）；也可用远程视觉模型，无需本地环境

## 配置

配置分两层，边界是**密钥只在环境层**。

**① 环境层**（`.env`，改完需重启）：路径、密钥、进程绑定。

```ini
PDF_ROOT=/path/to/manuals                     # 留空则用 <项目>/pdf
DB_PATH=/path/to/index.lance                  # 留空则用 <项目>/index.lance
EMBED_BASE_URL=https://api.example.com/v1     # OpenAI 兼容 /v1
EMBED_API_KEY=                                # 只从环境读，绝不入库/入包/进前端
EMBED_MODEL=qwen3-embedding-8b                # 与索引强绑定，必须与建库时一致
EMBED_DIMENSIONS=768                          # 与索引维度一致，建库/查询两侧都显式发送
RERANKER_MODEL=rerank-v4.0-pro
OCR_API_KEY=                                  # remote OCR 密钥（同上，只在环境层）
ADMIN_TOKEN=                                  # 留空则 /api/admin/* 一律 403
```

**② 可调参数层**（51 项 / 9 组）：嵌入服务、检索融合、片段、排序、缓存、外部接口、
文档提取、索引吞吐、OCR 后端。`.env` 给初始值，可在 Web **「检索配置」页**运行时修改，
**即时生效**，覆盖值持久化到 `data/settings.json`。

- 每项有中文名（`label`）；原始变量名默认隐藏，页面右上角「变量名」开关可显示。
- OCR 五项按 `ocr_backend` 联动：`local` 只认 `ocr_url`，`remote` 只认 `api_base/model/prompt`。
- OCR 地址/模型/提示词已在此层；**但 `OCR_API_KEY` 永远只在环境层**。
- **向量维度（`embed_dimensions`）必须与索引一致**（当前 768）。它随数据包导出；
  若与索引不符，向量通道会明确降级并记日志，不会静默返回错误结果。换维度需重建索引。

> ⚠️ 改 `.env` 需重启后端；改可调参数不需要。重启走 `POST /api/admin/restart`
> （需 `X-Admin-Token`）。`data/settings.json` 不入版本库，删掉即回到默认值。

**设计约束：不主动探测上游。** 系统**不以任何方式定时或主动探测**嵌入/重排/OCR 服务的
可用性：那会给服务商带来无意义负载，且可用性不会在几秒内变化。OCR 状态显示的是
**最近一次真实调用**的结果（`last_call`）；要确认上游可用，跑一次真实检索或读页即可。

## 使用

**Web**（6 个页面）：

| 页面 | 用途 |
|---|---|
| 索引状态 | 触发增量/全量索引、实时进度与 ETA、错误与跳过列表 |
| 资料库 | 文档数/块数/类别分布、索引历史 |
| 文件库 | 文档清单、按类别/型号/编号筛选、提取质量体检（低文本页标红并可勾选重跑 OCR） |
| 检索测试 | 混合/FTS/向量三种模式、重排开关、条数、限定文档、命中页预览 |
| 检索配置 | 51 项可调参数（见上） |
| 数据管理 | 配置导出导入、数据包构建/下载/导入预检 |

**MCP**：8 个工具，统一 `pdf_rag_` 前缀（与客户端自带的 `grep`/`read` 区分——后者搜工作区文件，这里搜手册语料）。

| 工具 | 用途 |
|---|---|
| `pdf_rag_search(query, category, top_k, file, max_per_doc)` | 混合检索，返回已定位到答案的片段窗口 |
| `pdf_rag_grep(pattern, category, file, context, flex_separator)` | 字面/正则精确检索，不走向量，不受嵌入服务影响 |
| `pdf_rag_read_page(file, page)` | 读整页原文（扫描页自动 OCR） |
| `pdf_rag_read_pages(file, pages)` | 一次读多页，支持 `"62-65"`（规格表常跨页） |
| `pdf_rag_get_outline(file)` | 书签/标题目录，用于大手册导航 |
| `pdf_rag_list_categories()` / `pdf_rag_list_files(category)` | 类别 / 已索引文件与元数据 |
| `pdf_rag_status()` | 索引与依赖状态（含 OCR 最近一次真实调用）。**不探测上游** |

**REST**：与 MCP 能力等价，供非 MCP 客户端使用。另在 `clients/pi/pdf-rag-pi/` 附带一个
**pi 编码 agent 的原生扩展示例**（`extensions/pdf-rag.ts` 注册同名 `pdf_rag_*` 工具、
`skills/pdf-rag/SKILL.md` 给用法策略），底层走这套 REST 接口，可作为其他非 MCP 客户端
的接入参考。pi 从 1.2 起已内置 MCP、也能直连 `/mcp`；保留原生扩展是因为它能用
`promptSnippet`/`promptGuidelines` 做分层提示词注入，且工具名不带 `mcp__` 前缀。

## API 一览

| 端点 | 说明 |
|---|---|
| `GET /api/search?q=&category=&top_k=&mode=&rerank=&file=&max_per_doc=` | 混合检索 |
| `GET /api/grep?pattern=&category=&file=&max_hits=&context=&flex_separator=` | 正则精确检索 |
| `GET /api/page?file=&page=` | 单页原文（低文本页回退 OCR） |
| `GET /api/pages?file=&pages=62-65` | 多页 |
| `GET /api/outline?file=` | 书签目录 |
| `GET /api/pdf?file=` | 原文内联（PDF 可用 `#page=N` 深链；MD 走下载） |
| `GET /api/stats` | 文档数/块数/类别分布/索引历史 |
| `GET /api/categories` | 全部类别目录 |
| `GET /api/files?category=` | 文件清单与元数据（含提取质量字段） |
| `GET /api/extract/report?limit=` | 逐文档提取质量体检（低文本页标记） |

所有接受 `file` 的端点只认**语料库内的相对路径**（正斜杠；Windows 风格反斜杠会自动
归一），绝对路径与 `..` 穿越一律拒绝。`/api/search` 与 `/api/grep` 的 `file` 过滤按
**字面子串**匹配（`%`/`_` 不作通配符解释）。
| `GET /api/history` | 索引历史 |
| `GET /api/state` | 索引进度 |
| `GET /api/config` | 读全部可调参数（含中文名/默认值/范围/是否被覆盖） |
| `PUT /api/config` | 保存可调参数（即时生效） |
| `POST /api/config/reset` | 恢复默认（全部或指定项） |
| `GET /api/ocr/health` | OCR 配置 + 最近一次真实调用（不探测） |
| `POST /api/ingest?rebuild=` · `POST /api/ingest/files` | 触发索引 / 重跑指定文件 |
| `GET /api/export/config` · `POST /api/import/config` | 配置导出导入（不含密钥） |
| `POST /api/export/bundle` · `GET /api/export/bundles` · `GET /api/export/download` · `DELETE /api/export/bundle` | 数据包构建/列表/下载/删除 |
| `POST /api/import/inspect` · `POST /api/import/bundle` | 导入预检 / 执行导入 |
| `POST /api/admin/restart` | 重启后端（需 `X-Admin-Token`） |
| `POST /api/admin/shutdown` | 关闭后端（需 `X-Admin-Token`） |

## 索引

```bash
uv run python -m backend.ingest            # 增量（按 MD5 跳过未变化文件）
uv run python -m backend.ingest --rebuild  # 全量重建
```

也可在 Web「索引状态」触发，或在「文件库」勾选指定文件重跑（含 OCR）。进度写入
`run_state.json`，前端轮询 `/api/state`（索引运行时 1s、空闲 10s）。

**索引维护**：增量索引每跑一次都会留一个新版本，长期累积磁盘占用远超真实数据。
实测本仓库：8561 块真实数据约 26 MB，目录曾涨到 248 MB / 517 版本 / 1457 文件（约 9 倍），
同时查询要扫更多碎片。

```bash
uv run python tools/compact_index.py            # 合并碎片 + 清理 1h 前的旧版本
uv run python tools/compact_index.py --dry-run  # 只看现状
```

不改任何一行数据。最近一次实测：**128 MB / 521 版本 / 228 文件 → 43 MB / 8 文件**，
行数与全文索引不变，检索结果一致。清理后重启后端，让它在最新版本上重新持有句柄。

## 数据包（导出 / 导入）

把**索引 + PDF + 配置**打成一个 `.tar.zst`，可在另一台机器完整复原：

```bash
POST /api/export/bundle?include_docs=true&level=3   # 构建（先落盘再下载，避免同步大响应超时）
GET  /api/export/bundles                            # 已构建的包
GET  /api/export/download?name=                     # 下载
POST /api/import/inspect                            # 预检（含服务配置差异）
POST /api/import/bundle                             # 执行导入（可应用包内服务配置）
```

**数据与模型强绑定**：包内 manifest 带 `provider` 块（服务地址 + 嵌入/重排模型名）。
导入预检同时给出两个结论——应用包内配置则数据与模型重新配对、可用；保留本地配置则
模型不一致时**明确拒绝**，不让新旧向量混在一起静默劣化。

> 密钥**绝不入包**。包给他人时，对方用自己的密钥访问同一个服务地址即可。

## 评测

```bash
uv run python eval_retrieval.py              # 55 条评测集（hand 10 / topic 4 / mined 41）
uv run python eval_retrieval.py --json out.json
```

指标分两级，**只看文档级会漏掉核心缺陷**：

- `recall@k`：期望文档是否进 top-k。
- `snippet@1` / `snippet@k`：返回的**片段本身**是否含答案字面值——这才是判别指标。
- 分数必须按来源拆分：`hand`（人工手写，最贴近真实体验）/ `topic` / `mined`（自动挖掘）。
- 重排器**不确定**（推理非确定性，同请求分数抖动 ±0.004，且会改变相邻名次），
  同代码重跑 `snippet@1` 波动约 ±2pp；只看粗粒度变化，改动前后各跑两遍更稳。
- 跑之前确认输出里 `degraded` 为空，否则该次分数被限流污染。

**当前基线**（2026-10，片段宽 900 / 重排池 64，287 文档 / 12421 块）：
`recall@5` 100%，`snippet@1` 62%，`snippet@5` 91%。

历次参数实验（含"召回×重排融合""型号平局裁决""查询 instruct""维度提升""换嵌入模型"
等**否定性结果**及其成因）、准确率瓶颈归因漏斗、上游服务行为实测与方法学，
统一记录在 **[BENCHMARKS.md](BENCHMARKS.md)**——调参或换模型前先读它。

匹配规则与数据格式：

- `expect` 按**文件名**（两种分隔符都认）子串匹配，与目录无关——类别目录会被重组，
  完整路径断言会把"检索其实找对了"误判成失败。expect 可列多份等价文档，命中任一即满分。
- `must_contain` 判定对空白/下标分隔符宽容（"500 Ω" 命中 "500Ω"）。
- `eval_queries.json` 里 `_` 前缀字段（`_page`、`_n_chunks_with_val`）是策展时的溯源
  信息，评测不使用；`tools/curate_eval.py` 从 `tools/mined_cases.json` + 内置手写用例
  重新生成整个评测集（需要已有索引）。

## 性能要点（改代码前请先读）

这几处是实测调优的结果，回退会明显变慢：

| 位置 | 做法 | 原因 |
|---|---|---|
| `library.scan_arrow` | 投影下推 `search().select(cols).limit(count_rows())` | 直接 `to_arrow()` 会把 768 维向量列（26MB）也读进内存再丢：54ms → 16ms |
| `main._table` / `server._get_table` | 只比对 `table.version` | 曾用 `to_arrow().num_rows` 探测句柄，等于每请求物化全表（37ms） |
| `library.cached` | 元数据按 `table.version` 缓存 | `/api/files`、`/categories`、`/extract/report` 各扫一遍全表，实际只在 ingest 后变化 |
| `/api/files` 聚合 | `if k not in seen` 而非 `setdefault` | `setdefault` 的默认 dict 每行都构造，让 `product_label` 正则跑满每块（20ms → 1ms） |
| 前端 `getSWR` | 切回页面先用上次结果、后台刷新 | 每次进入都全量重拉是纯开销 |
| `SelectiveGZip` | JSON 压缩，跳过 `/mcp`（SSE）与 `/api/pdf`（已压缩） | JS bundle 708KB 裸传 → gzip；`/api/files` 59KB → 9KB |
| 片段宽 900 / 池 80（默认值） | `snippet_width`、`cand_floor`、`rerank_pool_floor` | 表格页答案值常在页文本 1300–2000 字符处，宽 600 框不住；大手册（MSM8916）答案页融合后进不了前 40 池。55 条评测 snippet@1 58%→62%、snippet@5 73%→91%，两次重复运行逐条一致 |
| 重排排序保持纯重排分 | `rerank_rank_weight`、`rerank_tie_tolerance` 默认 0 | 召回名次与重排名次融合实测让概述页抢走参数值查询的 top1（58%→38%）；型号平局裁决对不含型号的查询无从裁决（55 条评测均无净收益）。两项保留为开关 |

检索核心的设计要点与「勿凭直觉回退」的警告写在 `backend/retrieval.py` 的模块 docstring 里。

## 开发

```bash
# 前端开发（Vite 代理 /api 到 8100）
cd web && pnpm install && pnpm dev

# 前端构建（含 vue-tsc 类型检查）→ web/dist，后端自动托管
cd web && pnpm build
```

改前端后需重新 `pnpm build` 并重建镜像（Dockerfile 会 `COPY web/dist/`）。

**测试**：没有自动化测试套件。改动检索/索引逻辑后，用 `eval_retrieval.py` 对比
`snippet@1` 判断是否回退；改动前端用 `pnpm build` 的类型检查兜底。

## tools/

| 脚本 | 用途 |
|---|---|
| `audit_code.py` | AST 统计函数长度/嵌套/魔数 |
| `audit_extract.py` / `audit_ocr.py` | 提取质量审计 / OCR 兜底失败量化 |
| `profile_rag.py` | 耗时画像 |
| `verify_roundtrip.py` | 数据包端到端往返验证 |
| `mine_eval3.py` + `curate_eval.py` | 从索引挖掘并策展评测集 |
| `reembed_index.py` | 用当前模型重算已有索引向量（对比嵌入模型时省掉提取阶段） |
| `compact_index.py` | 合并索引碎片 + 清理历史版本 |
| `export_parsed.py` | 导出解析后数据（块级 jsonl + 按页重建文本） |
| `build_release.py` | 构建交付包（含 `MANIFEST.txt` 与自检） |

## 许可证

本项目以 **GNU AGPL v3.0 或更高版本**（`AGPL-3.0-or-later`）发布，见 [LICENSE](LICENSE)。

### 为什么是 AGPL-3.0

不是偏好，是**依赖约束**：本项目直接依赖 **PyMuPDF**（引擎为 MuPDF），它以
**AGPL-3.0 / Artifex 商业许可**双许可发布。AGPL 的传染性适用于与其链接/组合的作品，
因此整体必须按 AGPL-3.0 分发——除非另外向 Artifex 购买商业许可。

**这对你意味着什么**：

| 场景 | 是否可以 |
|---|---|
| 自用 / 内部部署 | ✅ 可以 |
| 修改后对外提供网络服务 | ✅ 可以，但须按 AGPL §13 向网络用户提供对应源码 |
| 分发修改版 | ✅ 可以，但须同样以 AGPL 开放源码 |
| 闭源 SaaS / 闭源分发 | ❌ 需要 Artifex 商业许可，或替换掉 PyMuPDF |

如果将来需要闭源分发，最干净的路径是把 PyMuPDF 换成 AGPL-free 的 PDF 引擎
（如 `pypdf` / `pdfplumber`），这会涉及 `doc_utils.py`、`ingest.py`、`library.py`
三处的读页与表格提取逻辑。

### 依赖许可清单

对已安装的 82 个包逐一核对 `dist-info`，**只有 PyMuPDF 是 copyleft**：

| 组件 | 许可证 | 对项目的影响 |
|---|---|---|
| **PyMuPDF 1.28** | **AGPL-3.0 / 商业双许可** | **决定整体许可证** |
| LanceDB 0.36 / PyArrow 25 | Apache-2.0 | 无 |
| FastAPI / Starlette / Uvicorn / FastMCP | MIT 或 BSD | 无 |
| Pydantic 2.x / MCP SDK / httpx / AnyIO | MIT / BSD-3 | 无 |
| numpy / pandas / zstandard / python-dotenv | BSD | 无 |
| certifi / tqdm | MPL-2.0（文件级弱 copyleft） | 无（未修改其源码） |
| **前端**：Vue 3 / Vue Router / naive-ui / Vite / vue-tsc | MIT | 无 |
| **前端**：TypeScript | Apache-2.0 | 无 |
| **OCR**：PaddleOCR | Apache-2.0 | 无（可选组件，独立进程） |
| 运行时：Python 3.13 / Node.js | PSF / MIT 类 | 无 |

> 依赖清单可直接复现：
> `.venv/bin/python -c "import importlib.metadata as m; [print(d.metadata['Name'], d.version,
> d.metadata.get('License') or [c for c in (d.metadata.get_all('Classifier') or []) if 'License' in c])
> for d in m.distributions()]"`

### 第三方声明

- MuPDF / PyMuPDF 版权归 Artifex Software, Inc.，以 AGPL-3.0 使用。
- PaddleOCR 版权归 PaddlePaddle  Authors，Apache-2.0。
- 其余依赖的版权与许可条款见各包内 `LICENSE` 文件。

本仓库**不包含**任何第三方手册 PDF 的再分发授权——`pdf/` 下的数据手册版权归各自厂商，
仅供本地检索使用；对外分发本仓库时请勿附带这些手册。
