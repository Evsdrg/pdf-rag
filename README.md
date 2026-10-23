# PDF-RAG

本地元器件手册检索：对 PDF/Markdown 手册库做**语义向量 + 全文(FTS) + 子串**三路混合检索
（RRF 融合 → 同文档去重 → 可选重排），支持表格识别与扫描页 OCR 兜底，通过 **Web 界面**、
**MCP 工具**、**REST API** 三种方式对外提供服务。

```
                     ┌──────────────┐
   浏览器   ──────▶  │  Web UI      │ Vue 3 + naive-ui（打进镜像，由后端托管）
                     ├──────────────┤
  MCP 客户端 ─────▶  │  /mcp        │ 8 个 pdf_rag_* 工具（默认内嵌进后端进程）
  pi 等 REST ─────▶  │  /api/*      │ 与 MCP 共用 backend/library.py 的实体逻辑
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

| 文档 | 内容 |
|---|---|
| [docs/README.md](docs/README.md) | **文档索引**：架构设计、向量分区、实验记录与维护约定 |
| [DEPLOY.md](DEPLOY.md) | 部署指南、REST API 全表、索引与数据包运维（内网部署记录 `DEPLOY-NAS.md` 仅留本机） |
| [THIRD-PARTY.md](THIRD-PARTY.md) | 依赖许可清单与第三方声明 |

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
  ocr_policy.py   低文本页的本地内容判定（不调用模型）
  ocr_queue.py    索引期共享的有界 OCR 请求通路
  bundle.py       数据包（.tar.zst）导出/导入
  vecstore.py     向量分区:uid、分区表、覆盖率(见 docs/VECTOR-PARTITION.md)
server.py         MCP 服务（默认内嵌；MCP_INPROC=0 时独立进程）
ocr_service.py    本机 OCR 服务（独立进程，依赖 ocr-env，可选）
run_backend.py    后端守护：崩溃自愈 + 单例锁
eval_retrieval.py 检索质量评测
eval_queries.json 评测集（55 条）
docs/BENCHMARKS.md 评测结果与历次实验记录
DEPLOY.md         部署指南（裸机 / 交付包 / API 参考）
tools/            开发期诊断与维护脚本
web/              前端源码（Vue 3 + Vite + naive-ui）
index.lance/      LanceDB 索引（运行时生成）
data/             运行时配置覆盖值与导出包（运行时生成）
```

各模块**为什么这样分层、彼此依赖方向、哪些约束不能破**，见
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## 环境要求

- **Python 3.13** + [uv](https://docs.astral.sh/uv/)
- **Node.js**（仅前端开发/构建；镜像里已有构建好的 `web/dist`）
- **嵌入 / 重排服务**：OpenAI 兼容的 `/v1/embeddings` 与 `/v1/rerank`
- **OCR（可选）**：本机 Paddle 需独立 `ocr-env`（约 4.9GB）；也可用远程视觉模型，无需本地环境

## 配置

配置分两层，边界是**密钥只在环境层**。

**① 环境层**（`.env`，改完需重启）：

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

**② 可调参数层**（56 项 / 10 组）：Web「配置中心」页修改并持久化到
`data/settings.json`。检索参数即时生效；索引并发在下一轮任务生效，不改变正在运行的池。
OCR 地址/模型/提示词在此层（按 `ocr_backend` 联动），但 `OCR_API_KEY`
永远只在环境层；**向量维度必须与索引一致**（当前 768，随数据包导出），不符时向量通道明确
降级并记日志。

> 设计约束：系统**不以任何方式定时或主动探测**嵌入/重排/OCR 服务的可用性；OCR 状态展示
> 最近一次真实调用的结果。要确认上游可用，跑一次真实检索即可。这类"刻意不做"的决定
> 见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) §7。

## 使用

**Web**（6 个页面）：索引状态（触发索引/实时进度）、资料库（统计与历史）、文件库（筛选与
提取质量体检）、检索测试（三模式/重排开关/命中页预览）、配置中心（56 项）、数据管理
（配置与数据包导入导出）。

**MCP**：8 个工具，统一 `pdf_rag_` 前缀（与客户端自带的 `grep`/`read` 区分——后者搜工作区
文件，这里搜手册语料）。

| 工具 | 用途 |
|---|---|
| `pdf_rag_search(query, category, top_k, file, max_per_doc)` | 混合检索，返回已定位到答案的片段窗口 |
| `pdf_rag_grep(pattern, category, file, context, flex_separator)` | 字面/正则精确检索，不走向量，不受嵌入服务影响 |
| `pdf_rag_read_page(file, page)` / `pdf_rag_read_pages(file, pages)` | 读整页原文（扫描页自动 OCR）/ 一次读多页 |
| `pdf_rag_get_outline(file)` | 书签/标题目录，用于大手册导航 |
| `pdf_rag_list_categories()` / `pdf_rag_list_files(category)` | 类别 / 已索引文件与元数据 |
| `pdf_rag_status()` | 索引与依赖状态（含 OCR 最近一次真实调用）。**不探测上游** |

**REST**：与 MCP 能力等价，完整端点表见 [DEPLOY.md](DEPLOY.md)。`clients/pi/pdf-rag-pi/`
附带一个 **pi 编码 agent 的原生扩展示例**（同名 `pdf_rag_*` 工具 + 用法 SKILL），底层走这套
REST 接口，可作为其它非 MCP 客户端的接入参考。

## 索引

```bash
uv run python -m backend.ingest            # 增量（按 MD5 跳过未变化文件）
uv run python -m backend.ingest --rebuild  # 全量重建（换嵌入模型后必须）
```

也可在 Web「索引状态」触发，或在「文件库」勾选指定文件重跑（含 OCR）。长期增量会产生
索引碎片，定期用 `tools/compact_index.py` 整理（见 [DEPLOY.md](DEPLOY.md)）。

低文本页先经纯本地内容筛选，再决定是否 OCR；入库与读页共用判定。可用
`ocr_smart_filter=false` 恢复仅按字数触发。离线对照工具
`python tools/audit_ocr_policy.py <手册目录>` 不调用任何模型；规则与边界见
[架构设计 §5.1](docs/ARCHITECTURE.md#51-低文本页的-ocr-判定)。改策略不会自动重提取已有索引。

Web「配置中心 → 索引与并发」可独立调整 **本地解析进程数**（`extract_workers`，默认 4）
与 **索引 OCR 并发数**（`ocr_workers`，默认 4），范围均为 1–32。
前者同时处理不同文档的文本、表格与页面渲染；后者为整轮索引共用的页面请求通路，
同一份 PDF 也可多页并发，**不会按解析进程数相乘**。本地进程按 CPU/内存配置，
OCR 通路还受服务商限流或本地 OCR 算力约束；两项保存后均在下一轮索引生效。
读页接口不属于索引请求池，因此此上限不是全服务所有 OCR 的总上限。

配置中心默认展示常用项，按「服务与模型 / 索引与并发 / OCR 与提取 / 检索效果 /
性能与连接」分类，高级项默认收起。可跨分类搜索中文名称、说明或变量名；
未保存项集中查看，切换分类保留草稿，保存、单项恢复默认与全部撤销沿用同一套状态。

## 数据包（导出 / 导入）

把**索引 + PDF + 配置**打成一个 `.tar.zst`，可在另一台机器完整复原；导入预检会比对包内
与本地的服务配置，模型不一致时明确拒绝，不让新旧向量静默混用。命令与细节见
[DEPLOY.md](DEPLOY.md)；**密钥不入包**。

## 评测

```bash
uv run python eval_retrieval.py              # 55 条评测集（hand 10 / topic 4 / mined 41）
```

两级指标：`recall@k`（期望文档进没进 top-k）与 `snippet@1/@k`（片段是否含答案字面值——
判别指标）。当前基线：**recall@5 100% / snippet@1 62% / snippet@5 91%**。重排器有固有
随机性（±2pp），改动前后各跑两遍；评测方法、匹配规则与历次实验见
[docs/BENCHMARKS.md](docs/BENCHMARKS.md)。

## 开发

```bash
cd web && pnpm install && pnpm dev    # 前端开发（Vite 代理 /api 到 8100）
cd web && pnpm build                  # 构建 → web/dist，Dockerfile 会 COPY 它
```

**测试**：关键路径单测在 `tests/`（纯逻辑，不访问网络与索引，158 个用例）：

```bash
uv run python -m unittest discover -s tests
```

覆盖：路径边界防护、分块、版本合并去重、融合排序与平局裁决、缓存失效、file 过滤字面
语义、片段窗口、向量分区（uid 唯一性 / slug 契约区分 / 覆盖率口径 / 索引保真）、
数据包导入判断、OCR 内容筛选与读页/入库判定一致性。改动检索/索引逻辑后跑一遍；端到端质量另用 `eval_retrieval.py` 对比
`snippet@1`；前端配置页可用 `cd web && pnpm test` 校验分类、搜索和并发入口，
用 `pnpm build` 执行类型检查与构建。

## 鸣谢

- 感谢 [futureppo](https://api.futureppo.top/) 提供了几乎无限的免费向量化/重排序模型，
  帮助本项目完成测试与调优。

## 许可证

本项目以 **GNU AGPL v3.0 或更高版本**（`AGPL-3.0-or-later`）发布，见 [LICENSE](LICENSE)。
这不是偏好而是**依赖约束**：直接依赖的 PyMuPDF（MuPDF）为 AGPL-3.0 / 商业双许可，传染性
使整体必须按 AGPL 分发。

| 场景 | 是否可以 |
|---|---|
| 自用 / 内部部署 | ✅ 可以 |
| 修改后对外提供网络服务 | ✅ 可以，但须按 AGPL §13 向网络用户提供对应源码 |
| 分发修改版 | ✅ 可以，但须同样以 AGPL 开放源码 |
| 闭源 SaaS / 闭源分发 | ❌ 需要 Artifex 商业许可，或替换掉 PyMuPDF |

依赖许可核对与第三方声明见 [THIRD-PARTY.md](THIRD-PARTY.md)。
