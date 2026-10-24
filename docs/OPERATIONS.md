# 运维手册

本文负责**索引维护、数据包迁移、状态检查和故障排查**。首次安装见[部署指南](../DEPLOY.md)，参数与模型选择见[配置说明](CONFIGURATION.md)。执行写操作前确认目标目录和配置；不要因目录名含 `tmp`、`backup` 就删除手册、索引或备份。

## 1. 状态与索引维护

### 1.1 先看哪组状态

| 入口 | 用途 |
|---|---|
| `GET /api/stats` | 已索引文档/块数、类别、历史与各向量分区覆盖率 |
| `GET /api/v2/status` | 源文件与索引覆盖差异、OCR 最近真实调用、入库时间是否可知 |
| `GET /api/state` 或 `run_state.json` | 当前/最近一次索引任务进度，不是文档清单 |
| `GET /api/extract/report` | 按文档统计提取字符量和低文本告警 |
| `GET /api/ocr/health` | OCR 配置与最近一次真实调用；不主动探测上游 |

`source_files` 是源目录 PDF/Markdown 数，`indexed_files` 是索引文件数；`unindexed_files` 与 `missing_source_files` 分别表示未索引文件和失效索引引用。`last_ingest_status=unknown` 表示没有可用历史时间，不等于刚更新或从未更新。

### 1.2 常用索引命令

```bash
# 增量：按 MD5 处理新增/变化文件，并移除已删除文件的索引
uv run python -m backend.ingest

# 强制重提取指定文件（含 OCR 策略）；路径相对 PDF_ROOT
uv run python -m backend.ingest --force "01_传感器/example.pdf"

# 重建主表文本；向量分区不动，提取配置与分块结果不变时 uid 保持稳定
uv run python -m backend.ingest --rebuild

# 让当前模型分区覆盖全部块；先把该模型设为当前 embed_model
uv run python -m backend.ingest --rebuild-vectors <同名模型>
```

也可在 Web「索引状态」触发增量，或在「文件库」选择指定文件重跑。索引任务使用锁防止并发写入，不要绕过锁同时启动多个任务。

换模型时，普通增量只覆盖变化文件；需要完整迁移才使用 `--rebuild-vectors`。`--drop-old-vectors` 默认关闭，仅清理目标模型自己的分区，详见[配置说明](CONFIGURATION.md#更换或新增模型)。

### 1.3 碎片与向量索引

长期增量会积累 LanceDB 版本和文件。先观察再整理：

```bash
uv run python tools/compact_index.py --dry-run
uv run python tools/compact_index.py
```

整理只合并碎片和清理旧版本，不应改变行数据。操作前保留现有索引与必要备份，完成后让后端重新持有最新表句柄。

向量分区使用可选的 `IvfFlat` 加速。没有索引时可退化为精确暴力扫描；小数据集不强行建索引。老库需要补建时：

```bash
uv run python tools/build_vec_index.py
# 明确需要全部重建时：uv run python tools/build_vec_index.py --rebuild
```

写入流程会自动维护向量索引，不要把补建当成每次查询前的例行操作。

## 2. OCR 运行维护

- 本地 Paddle 服务与后端环境分离，PP-StructureV3 推理串行化；默认空闲 300 秒卸载模型，可用 `OCR_IDLE_TIMEOUT_SECONDS` 调整。
- 远程 OCR 使用真实读页或索引调用，地址/模型/提示词按配置读取，密钥只在环境层。
- 低文本页先经过内容策略，OCR 不是每页固定执行的预处理。零文本、复杂矢量、截图和无法确认的内容倾向保留 OCR。
- 单页失败保留原生文本并返回告警；单个坏文件不应丢弃整轮其他文件。
- 日志主要看 `logs/backend.log` 和本地 OCR 日志。不要把上游响应中的密钥、完整请求或内部节点信息复制到公开记录。

没有 OCR 或调用失败不等于所有页面为空；原生文本仍可能存在。曲线、封装和图内数值可改用 `pdf_rag_render_page` 读取真实页面，不要根据拉平文本猜图。

## 3. 数据包迁移

数据包用于迁移**索引、可选手册和可调配置**，不包含密钥。构建、预检、导入是三个独立步骤：

```bash
# 构建（包含手册；不含密钥）
curl -X POST "http://127.0.0.1:8100/api/export/bundle?include_docs=true&level=3"

# 预检：比较包内服务配置与当前环境，返回阻断原因
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"包文件名"}' http://127.0.0.1:8100/api/import/inspect

# 确认预检结果后执行导入
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"包文件名","restore_docs":true,"replace_index":true,"apply_provider":true}' \
  http://127.0.0.1:8100/api/import/bundle
```

导入前会备份现有索引到 `index.lance.bak-<时间戳>`。预检不通过时先解决模型、维度、输入类型或路径冲突，不要用重复调用绕过校验。

- `apply_provider=true`：应用包内服务配置，使数据与契约重新配对。
- 不应用且本地模型与包内不一致：可能明确拒绝导入，避免跨向量空间混用。
- `restore_docs` 与 `replace_index` 是不同选择，应分别确认，不能把“保留手册”理解成“保留旧索引”。
- 备份、原索引和手册都是潜在唯一副本，清理前逐路径确认，不能通配删除。

完整交付包的生成使用 `tools/build_release.py`，见[部署指南](../DEPLOY.md#3-交付包部署)。

## 4. 配置与发布检查

- 修改 `.env` 通常需要重启；`data/settings.json` 的检索参数即时生效；并发在下一轮索引用。
- 密钥只在环境层。导出配置或数据包后仍应检查内容，不把“设计上不含密钥”替代实际敏感信息扫描。
- 发布源码使用 `git archive HEAD`，前端使用当前 `web/dist` 构建结果。
- 文档链接与敏感信息检查：`python tools/check_docs.py`。
- 后端、前端和 pi 的关键测试命令见[项目 README](../README.md#开发与验证)。

## 5. 故障排查

### 搜索不到预期文档

1. 看 `/api/v2/status`：文件是否已索引，源目录是否包含该文件。
2. 看搜索响应的 `degraded/notice/warnings`：区分正常无匹配、向量分区不可用、嵌入失败或重排失败。
3. 看 `/api/stats`：目标向量分区是否被排除、覆盖率是否不足、当前优先级是否只选了另一个模型。
4. 用 `pdf_rag_grep` 查精确型号或符号，区分检索排序问题与源文本缺失。
5. 用文件列表按型号筛选，再用页码回读；不要只凭“有语义相近结果”断定目标型号存在。

### 向量或重排质量突然变差

先保留本次真实响应和降级字段，再检查模型、维度、输入类型、分区优先级和上游限流。完整质量评估使用 `eval_retrieval.py`；`degraded` 非空时，该轮成绩不能代表正常水平。不要把单次重排分或名次变化当成确定性回归。

### 页面没有文本或 OCR 失败

检查该页是否本来以图为主、是否为扫描/曲线化正文、OCR 配置与真实调用记录。优先保留原生文本和 `warnings`；需要看图时调用页图工具。修复提取后由用户显式重跑指定文件，旧索引不会自动变化。

### 文件存在但读不了

只接受 `PDF_ROOT` 内的相对路径，路径穿越会被拒绝。PDF 页码从 1 开始且是物理页；Markdown 按一级标题形成伪页。损坏或加密文档会返回结构化错误，不应把异常文本当作手册内容。

### Web 或进程问题

- 空白页：确认 `web/dist/index.html` 存在且完整；前端改动需重新 `pnpm build`。
- 首屏显示 0：检查是否在读任务进度而非索引统计，文档数以 `/api/stats` 和文件库为准。
- 端口占用：调整 `BACKEND_PORT`，或确认并停止真正占用者，不要盲目杀相关进程。
- 客户端调用旧 `/api/search`、`/api/page` 等：查询与读取已统一到 `/api/v2/*`，按[HTTP API](HTTP-API.md)迁移，旧别名不保留。
- MCP 会话失效：服务更新后重启或重连客户端，再用工具清单和 `schema_version=2` 核对版本。

更多性能数据和历史故障背景见[评测与实验记录](BENCHMARKS.md)，接口字段见[MCP/Agent 协议](MCP-PROTOCOL.md)。
