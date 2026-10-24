# PDF-RAG

[![CI](https://github.com/Evsdrg/pdf-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/Evsdrg/pdf-rag/actions/workflows/ci.yml)

本地元器件手册检索：对 PDF/Markdown 手册库做**语义向量 + 全文（FTS）+ 型号子串**三路混合检索，支持表格提取、低文本页 OCR、页图读取，并通过 Web、MCP 和 REST 对外提供服务。

目标不是泛泛地“找到一份手册”，而是定位**某个参数在哪份文档、哪一页、哪一段**，并保留可继续核对的来源引用。

```text
浏览器       → Web UI（Vue 3，由后端托管）
MCP 客户端   → /mcp（10 个 pdf_rag_* 工具）
Web / pi     → /api/v2/*（统一查询与读取协议）
管理接口     → /api/*（索引、配置、数据包和统计）
                    │
                    └→ LanceDB：主表文本/FTS + 按模型划分的向量分区
```

## 快速上手

要求 Python 3.13 和 [uv](https://docs.astral.sh/uv/)。前端产物已随仓库提供，仅使用系统时不需要 Node.js。

```bash
cp .env.example .env        # 填入自己的嵌入服务配置和 EMBED_API_KEY
uv sync
uv run run_backend.py       # http://127.0.0.1:8100
```

1. 将 PDF/Markdown 手册放入 `pdf/`，或在 `.env` 中设置 `PDF_ROOT`。
2. 打开 Web「索引状态」，手动触发**增量索引**。
3. 在「检索测试」查询，或使用 MCP / REST 读页与检索。

没有嵌入凭据时仍可使用全文和精确检索，但向量通道会明确降级。密钥只放在环境层，不进入索引、数据包、配置页面或公开文档。配置详见 [配置说明](docs/CONFIGURATION.md)。

## 按任务查文档

| 要做什么 | 入口 |
|---|---|
| 安装、启动、接入 MCP | [部署指南](DEPLOY.md) |
| 配置模型、路径、OCR 与并发 | [配置说明](docs/CONFIGURATION.md) |
| 增量索引、数据包迁移、故障排查 | [运维手册](docs/OPERATIONS.md) |
| 调用 MCP / REST、理解游标和错误 | [MCP/Agent 协议](docs/MCP-PROTOCOL.md) · [HTTP API 参考](docs/HTTP-API.md) |
| 修改检索、索引或存储 | [架构设计](docs/ARCHITECTURE.md) · [向量分区](docs/VECTOR-PARTITION.md) |
| 对比检索质量、查阅历史实验 | [评测与实验记录](docs/BENCHMARKS.md) |
| 接入 pi 编码 agent | [pi 扩展](clients/pi/pdf-rag-pi/README.md) |
| 核对许可证 | [第三方声明](THIRD-PARTY.md) |

完整文档地图和维护约定见 [docs/README.md](docs/README.md)。

## 主要能力

- **三路召回与重排**：FTS、型号子串和向量候选经 RRF 融合、同文档去重和可选重排；降级原因显式返回。
- **可追溯结果**：命中带文件、物理页/伪页、块标识和偏移；表格和曲线可继续回读原文或页图。
- **有界 Agent 输出**：文件和目录分页，长页、跨页与章节支持游标续读，错误使用稳定错误码。
- **保守 OCR**：根据整份文档画像、页面内容、图片和矢量特征决定是否请求 OCR；证据不足时保留 OCR。
- **独立并发**：本地解析进程与整轮 OCR 通路分别配置，不层层相乘；运行中的任务不动态扩容。
- **多模型向量分区**：主表文本与向量解耦，每个分区记录模型、维度和输入类型契约，旧分区可保留。

设计理由与不能破坏的不变量见 [架构设计](docs/ARCHITECTURE.md)。

## 代码导航

```text
backend/
  main.py              管理、统计、原文件和应用装配
  agent_routes.py      /api/v2 传输层
  agent_api.py         统一响应、错误、诊断与参数边界
  agent_documents.py   按需读页、目录、章节和续读缓存
  agent_grep.py        精确匹配与上下文聚合
  agent_images.py      本地 PDF 页图
  agent_paging.py      输出预算和版本绑定游标
  retrieval.py         三路召回、融合、去重、重排和片段
  ingest.py            提取、嵌入与索引写入
  library.py           表句柄、元数据、源文件覆盖和参数解析
  vecstore.py          uid、向量分区、契约与覆盖率
  doc_utils.py         PDF/Markdown 提取和表格处理
  ocr*.py              OCR 策略、后端与索引期请求队列
  bundle.py            数据包导出/导入
server.py              MCP 工具适配
web/                   Vue 3 + TypeScript + Vite 前端
clients/pi/            pi 原生扩展示例
tests/                 离线关键路径测试
docs/                  设计、接口、配置、运维和实验文档
```

## 索引与数据包

```bash
uv run python -m backend.ingest            # 增量：处理新增/变化/删除的文件
uv run python -m backend.ingest --rebuild  # 重建主表文本；不是换模型的专用命令
```

`--rebuild-vectors`、碎片整理、指定文件重跑及数据包迁移属于运维操作，见[运维手册](docs/OPERATIONS.md)。系统不会仅因文档或配置改变而自动重建索引。

## 开发与验证

```bash
uv run python -m unittest discover -s tests
cd web && pnpm install && pnpm test && pnpm build
node --experimental-strip-types --test clients/pi/pdf-rag-pi/tests/adapter.test.mjs
python tools/check_docs.py
```

- 后端和客户端测试使用临时夹具或确定性替身，不请求上游模型。
- 真实检索质量使用 `uv run python eval_retrieval.py` 评估；方法、环境和历史基线见[评测记录](docs/BENCHMARKS.md)，不要把离线协议测试当成准确率证明。
- GitHub Actions 分别运行后端测试、前端测试与构建、文档检查；依赖安装仍需要可访问的软件包源。
- `web/dist` 是 Docker 镜像直接使用的受跟踪构建产物，前端改动后需重新构建。

## 鸣谢

感谢 [futureppo](https://api.futureppo.top/) 提供向量化/重排序模型测试资源。

## 许可证

本项目采用 **GNU AGPL v3.0 或更高版本**（`AGPL-3.0-or-later`），见 [LICENSE](LICENSE)。直接依赖的 PyMuPDF（MuPDF）采用 AGPL-3.0 / 商业双许可；修改后对外提供网络服务时需注意 AGPL §13 的对应源码义务。

第三方手册的版权属于各厂商，本仓库不附带其再分发授权。依赖核对与分发边界见[第三方声明](THIRD-PARTY.md)。
