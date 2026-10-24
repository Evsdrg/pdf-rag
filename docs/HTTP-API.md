# HTTP API 参考

REST 查询与读取统一使用 `/api/v2/*`，与 MCP 共用 `backend/agent_api.py`。本文列出端点和参数；返回字段、游标、页码、引用与错误语义以[MCP/Agent 协议](MCP-PROTOCOL.md)为准。

旧 `/api/search`、`/api/page`、`/api/pages`、`/api/grep`、`/api/outline`、`/api/files`、`/api/categories` 查询/读取别名已删除。索引、配置、数据包和统计管理接口仍使用各自的 `/api/*` 路径。

## 1. 查询与文档读取

| 方法与路径 | 主要参数 | 用途 |
|---|---|---|
| `GET /api/v2/search` | `query`、`category`、`file`、`top_k`、`max_per_doc`、`mode`、`rerank` | 混合检索，返回片段、块引用和诊断 |
| `GET /api/v2/grep` | `pattern`、`category`、`file`、`max_hits`、`context`、`flex_separator`、`cursor` | 精确正则检索，按页聚合上下文 |
| `GET /api/v2/page` | `file`、`page`、`max_chars`、`cursor` | 读取单页，支持续读 |
| `GET /api/v2/pages` | `file`、`pages`、`max_chars`、`cursor` | 一次读取最多 50 页，整次共享预算 |
| `GET /api/v2/outline` | `file`、`max_level`、`limit`、`cursor` | 分页目录与 `section_id` |
| `GET /api/v2/section` | `file`、`section_id`、`max_chars`、`cursor` | 读取 Markdown 标题范围或 PDF 书签页范围 |
| `GET /api/v2/files` | `category`、`file`、`model_no`、`kind`、`limit`、`cursor` | 已索引文件元数据分页 |
| `GET /api/v2/categories` | 无 | 已索引类别 |
| `GET /api/v2/status` | 无 | 源文件/索引覆盖与 OCR 最近真实调用 |
| `GET /api/v2/render` | `file`、`page`、`clip`、`max_size` | 本地 PDF 页图 JPEG，不调用模型 |

`file` 是 `PDF_ROOT` 内的相对路径，不接受绝对路径或 `..` 穿越。搜索/grep 的文件过滤是字面子串，`%` 和 `_` 不作为通配符。`render.clip` 在 HTTP 查询中用 JSON 字符串表示，例如 `[0,0,0.5,0.5]`；页图元数据位于 `X-PDF-RAG-Metadata`。

示例：

```text
GET /api/v2/search?query=QMC6309%20供电电压&file=QMC6309&top_k=3
GET /api/v2/page?file=01_传感器/QMC6309.pdf&page=5&max_chars=8000
```

成功返回 `schema_version=2` 的 JSON；预期错误为 `{error:{code,message,details}}` 并使用相应 HTTP 状态码。FastAPI 参数类型校验保留标准 422。长结果看 `truncated/next_cursor`，续读时保持其余参数不变。

## 2. 原文件、统计与提取质量

| 方法与路径 | 用途 |
|---|---|
| `GET /api/pdf?file=` | 原文件内联/下载；PDF 可用 `#page=N`，Markdown 按下载处理 |
| `GET /api/stats` | 索引文档/块数、类别、历史与向量分区覆盖率 |
| `GET /api/state` | 当前或最近一次索引任务进度 |
| `GET /api/history` | 索引历史 |
| `GET /api/extract/report?limit=` | 逐文档提取质量与低文本告警 |
| `GET /api/ocr/health` | OCR 配置与最近一次真实调用，不主动探测 |

`/api/stats` 与 `/api/v2/status` 用途不同：前者偏索引和向量分区，后者增加源目录覆盖对比。`run_state.json` 的进度不能替代索引数量。

## 3. 配置

| 方法与路径 | 用途 |
|---|---|
| `GET /api/config` | 读取可调参数、默认值、范围和覆盖状态，不含环境密钥 |
| `PUT /api/config` | 保存 `{"values":{...}}` 中的可调参数 |
| `POST /api/config/reset` | 恢复全部或指定项默认值 |

配置类别、优先级和生效时机见[配置说明](CONFIGURATION.md)。

## 4. 索引任务

| 方法与路径 | 用途 |
|---|---|
| `POST /api/ingest?rebuild=` | 启动增量或主表重建任务 |
| `POST /api/ingest/files` | 对 `{"files":[相对路径,...]}` 强制重提取 |

这些接口会改变索引，不是只读状态查询。调用前确认目标文件与任务锁，不能当作检索可用性探针。

## 5. 配置与数据包导入导出

| 方法与路径 | 用途 |
|---|---|
| `GET /api/export/config` | 导出可调配置，不含密钥 |
| `POST /api/import/config` | 导入可调配置 |
| `POST /api/export/bundle` | 构建数据包 |
| `GET /api/export/bundles` | 列出数据包 |
| `GET /api/export/download` | 下载数据包 |
| `DELETE /api/export/bundle` | 删除指定数据包，需明确名称 |
| `POST /api/import/inspect` | 导入预检与契约比较 |
| `POST /api/import/bundle` | 执行数据包导入 |

迁移顺序和备份语义见[运维手册](OPERATIONS.md#3-数据包迁移)。

## 6. 管理接口

| 方法与路径 | 用途 |
|---|---|
| `POST /api/admin/restart` | 重启后端，需 `X-Admin-Token` |
| `POST /api/admin/shutdown` | 关闭后端，需 `X-Admin-Token` |

`ADMIN_TOKEN` 留空时管理接口返回 403。令牌只在环境层，不能通过配置接口或数据包传递。
