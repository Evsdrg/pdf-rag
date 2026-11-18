# MCP / Agent 返回协议

本文记录 MCP 与唯一 REST 查询/读取接口 `/api/v2/*` 的返回契约。旧 `/api/search`、`page/pages/outline/grep/files/categories` 已移除，不保留兼容别名；Web 和 pi 扩展示例都使用统一协议。索引、配置、数据包管理及原文件下载接口不受此移除影响。

## 1. 返回与错误

文本工具返回一份 JSON 文本，含 `schema_version: 2`。不同时复制到 `structuredContent`，避免重复载荷。

- 单页：`file/kind/page/page_basis/total_pages/text/ocr/warnings`。
- 多页、章节：`file/kind/page_basis/total_pages/pages[]`；单页越界在该项内返回 `error`，其余项继续。
- 文件列表：`files/count/total/truncated/next_cursor`。
- 目录：`outline/count/total/truncated/next_cursor`；条目含 `section_id`。
- 精确查找：`results/count/total`，一项对应一页，内含 `contexts[]`。
- 搜索：`results/count/degraded/notice/warnings/identity/vector_partitions/structured/timings_ms/upstream/cached/counts`。

搜索可选参数 `structured=true` 启用默认关闭的无模型实体桥实验；`structured` 响应对象
只表示本次桥接的运行诊断，不是抽取事实或答案置信度。省略或设为 false 时不构建实体桥；
共享词法、来源保全与页面惩罚仍走当前修正版，不承诺与历史版本排序相同。

`page_basis=physical` 指 PDF 物理页，从 1 开始，可能与印刷页码不同；`h1_section` 指 Markdown 一级标题伪页。文件列表的 `pages_basis=indexed_max_page` 表示索引内最大页号，不承诺原文件物理总页数。

预期错误为 `error: {code, message, details}`。MCP 同时设置 `isError`；HTTP v2 映射为 4xx/5xx。常见码：`FILE_NOT_FOUND`、`PAGE_OUT_OF_RANGE`、`INVALID_ARGUMENT`、`INVALID_CURSOR`、`STALE_CURSOR`、`CATEGORY_NOT_FOUND`、`INDEX_NOT_FOUND`、`UNSUPPORTED_FORMAT`。未预期错误只返回安全摘要，细节留服务日志。HTTP 参数类型校验仍由 FastAPI 返回标准 422。

OCR 失败保留可用原生文本并在 `warnings` 中给出 `OCR_FAILED`；错误提示不充当原文。`ocr` 表示实际选用了 OCR 文本，不是上游健康状态。

## 2. 输出预算与续读

- 文件列表默认 30、最多 100 项，可筛选 `category/file/model_no/kind`；`file/model_no` 是大小写不敏感的字面子串。
- 目录默认两级、60 项，可用 `max_level=6` 展开；最多 100 项。
- 单页、多页、章节的 `max_chars=0` 默认使用 `page_max_chars` 配置（初始8000），实际预算最高12000；也可显式指定256–12000。多页是整次预算，不是每页预算。
- `read_pages` 最多指定 50 页，支持 `62,63`、`62-65`，先校验容量再展开范围。
- 列表、目录、精确查找和文档读取另有 32000 字节 JSON 上限，Unicode 和转义字符按真实序列化大小计。
- 搜索过大时保留排序靠前结果，并返回 `omitted_results` 和缩小查询提示；不声称结果完整。

`truncated=true` 时，保持文件/页码/章节或筛选条件不变，原样传回 `next_cursor`。游标绑定进程、数据版本和请求范围，不能自行构造；服务重启后重新从首批读取。索引、文件或提取配置变化返回 `STALE_CURSOR`。

同版本的按需页提取有短期有界缓存（5 分钟、64 项、16 MB），用于避免续读重复 OCR；失效后重新读取不保证复用旧 OCR 调用。

## 3. 章节与来源引用

`pdf_rag_get_outline` 返回的 `section_id` 可直接传 `pdf_rag_read_section`，同名标题仍有不同标识。

- Markdown：按标题层级读取，包含子节，不包含下一个同级或上级标题。
- PDF：按书签页范围读取，`section_basis=bookmark_pages`；相邻书签共享物理页时可能包含相邻节，不伪称页内精确定位。无书签不自动推断章节。

搜索的 `snippet` 使用经过保守展示处理的窗口，并提供 `snippet_ref`：`chunk_id/index_md5/start_offset/end_offset/offset_basis/truncated_before/truncated_after/table_header/warnings`。偏移基于索引块，不是实时读页或图像坐标。展示可有限扩展到行边界、移除无意义控制字符，但不会猜测修复单位、公式、乱码；默认检索送重排器的窗口不因此改变。

`structured=true` 时主证据优先使用完整 `snippet_width` 预算，尽量贴齐完整行；只有余量足够
且副窗新增查询证据时才加入第二窗，不均分预算、不为副窗截掉主证据条件。
`evidence_refs[]` 分别提供每个窗口的块偏移及组合片段内的 `snippet_start/snippet_end`；
`snippet_ref` 保留第一窗引用用于旧调用方，不能用它解释整个多窗片段。连续 Markdown 表头
可加入窗口预算，不继承已经结束的表格。开启 `rerank_on_window` 时重排正文与最终 `snippet`
完全一致（可另外前置文档身份行）；关闭该设置时仍显式使用整代表块重排。

同 MD5、同物理页的候选可折叠，优先引用查询指定身份；不同字节的同型号/相似标题文件
不会自动合并版本。结果可含最多四个 `source_aliases`（`file/model_no/index_md5/scope=same_bytes`）
及 `source_aliases_omitted`。仅列本次候选中折叠的内容副本，不是全库别名清单，
也不表示料号等同、订购行正确或兼容。引用仍使用结果自身的 file/page/chunk。

旧索引不含 OCR 来源、页内坐标、原始表格单元格关系，不能从引用字段推断这些信息。响应协议更新不需要重建索引，也不会自动触发索引。

结构化命中的结果可含 `retrieval_trace`：`kind=entity_direct/entity_expansion`，
`chunk_id/index_md5` 指向参与实体召回的块；扩展还带 `seed_chunk_id/seed_file/seed_page/seed_index_md5`
和最多四个 `shared_entities`。`scope=retrieval_only` 明确这只是检索连接，不证明兼容、
因果或条件相同。`seed_page` 与搜索页号同为从 1 开始；种子和目标都按 uid 回主表确认，
孤儿种子不放行。轨迹块可能不同于该页最终片段块，以 `snippet_ref` 核对展示证据。

## 4. 精确查找与诊断

结构化搜索每页还可返回最多三条 `structured_facts`：`subject/parameter/symbol/values/unit/conditions/source`。
只接受单块内明确表头、数值角色及单位的完整 Markdown 表；`values` 保留原字符串，
条件空白不继承，同参数不同条件不合并。`source` 除 file/page、chunk_id/index_md5 外，还带
数据行 `start_offset/end_offset` 和表头 `header_start_offset/header_end_offset`，均基于索引块。
它是保守的行列投影，不是完整参数数据库，不推断缺列、修复 OCR 或数值换算；
缺失/破损表回退原文。事实可不在 snippet 窗口内，需单独按来源核对。

`grep` 按文件/页聚合，每页最多五个不同上下文；同一索引块内重叠的窗口合并成连续文本，正文和表格的确定重复可合并，不同条件行与远离的内容区域保留。`indexed_matches` 是索引文本出现次数（可能包含正文/表格重复和分块重叠），不等于印刷页次数；`omitted_contexts` 只统计超出五个而未返回的窗口，`contexts_truncated` 表示确有窗口未展示。最多返回 100 页，可用游标继续。

向量通道成功但无命中是正常空召回，不是服务故障。降级按全文、子串、嵌入、分区、维度、覆盖率、重排区分，空结果仍给出诊断；不缓存降级结果。

`timings_ms` 是本次请求的阶段耗时（毫秒），可能包含 `result_cache_lookup`、`fts`、`substring`、`vector`、`structured`、`candidate_finalize`、`rerank`、`result_render` 和 `total`；未执行的阶段不出现。命中结果缓存时只保留本次缓存查找与总耗时，不复用原请求的阶段耗时。`upstream` 只报告本次请求的嵌入/重排调用次数、尝试次数、重试次数和累计耗时，以及查询向量缓存命中/未命中计数；不包含查询文本、正文、密钥或服务地址。它是性能诊断，不是上游可用性探测，也不代表答案质量。

`status` 中 `source_files` 是源目录内 PDF/Markdown 数，`indexed_files` 是索引文件数；
`unindexed_files` 和 `missing_source_files` 分别表示未索引文件与失效索引引用。按格式计数、
最多五个示例帮助定位，不返回整份差异清单。`source_status` 表示本次目录扫描是否完成；
`last_ingest_status=unknown` 明确表示没有可用的入库时间记录。状态只读本地文件名和真实调用历史，
不主动探测嵌入、重排或 OCR 服务。

`status.health` 是索引健康度，回答"索引本身是否可信"，只读本地索引与文件，不访问上游。
数据体积使用有界分批读取，并按主表身份和各表版本缓存；首次读取或版本变化后仍需扫描表数据，
但不会为计算体积整表物化 Arrow：

- `status` 为 `ok` / `degraded` / `missing` / `unknown`；`degraded` 时逐条给出 `warnings[].code`。
- `fts_index` 与 `vector_partitions[].indices` 列出实际存在的索引；缺失会报
  `FTS_INDEX_MISSING` / `VECTOR_MISSING` / `VECTOR_INDEX_MISSING`（后者意味着向量检索退化为暴力扫描）。
  FTS 元数据读取失败返回 `FTS_INDEX_UNAVAILABLE`，不会把未知状态当成健康。
- `fragmentation_ratio` = 索引目录体积 / 真实数据体积（含向量列）。超过 4 倍报
  `INDEX_FRAGMENTED`，提示可用 `tools/compact_index.py` 合并历史版本。
  数据量低于 1MB 时不判碎片，避免小索引的固定开销造成误报。任一分区不可读时返回
  `DATA_SIZE_UNAVAILABLE`，不使用部分体积计算碎片比。
- `last_ingest` 带上次索引的 `added/removed/chunks/elapsed/skipped`；`skipped` 是保留路径与
  `skipped_omitted` 之和，示例仍有界。有跳过时报告 `FILES_SKIPPED`，表示这些文件未产生文本、没有进入索引。
- `entity_snapshot` 只表示快照文件存在及其大小/时间；实际是否复用仍需通过表目录和版本指纹校验，
  失配时会重建，不能把文件存在等同于必然秒级启动。

采集失败不会让 `status` 整体失败：返回 `HEALTH_UNAVAILABLE` 并把其余字段照常给出。

## 5. 按需页图

`pdf_rag_render_page(file, page, clip?, max_size=1600)` 在本地用 MuPDF 渲染 PDF，一次一页，不调用 OCR、视觉、嵌入或重排服务。

- `clip=[x0,y0,x1,y1]` 为当前页面方向的归一化坐标，需满足 `0≤x0<x1≤1`、`0≤y0<y1≤1`。
- 最长边 256–2400 像素，默认 1600；JPEG 不超过 2 MB，必要时自动缩小。
- MCP 返回一段引用 JSON 和一个原生图片块，不把 base64 塞进文本。
- `GET /api/v2/render` 返回 JPEG 二进制，引用 JSON 位于 `X-PDF-RAG-Metadata`，不落盘、不缓存响应。
- Markdown 不支持页图；是否能消费图片取决于客户端及其模型能力。

## 6. HTTP 对照与客户端

MCP 与 `/api/v2/*` 共用领域入口，参数名基本相同；`render.clip` 在 HTTP 查询中用 JSON 字符串表示。
搜索的 `mode/rerank` 仅REST暴露，MCP `pdf_rag_search` 使用默认混合召回与重排，不能向它传
`mode=fts/rerank=false`。需要确保不调用上游的验收应走REST显式FTS/无重排，或MCP的grep/文件列表；
`structured=true`只保证实体桥本身不请求模型，不会关闭默认搜索中的向量/重排。
完整端点清单和管理接口见[HTTP API 参考](HTTP-API.md)，本文不重复维护另一份端点表。

Web 与 pi 使用同一结构，不猜测旧数组响应。pi 安装与工具说明见[客户端文档](../clients/pi/pdf-rag-pi/README.md)。

### 传输无状态与会话

MCP 的 Streamable HTTP 传输按 **无状态**（`stateless_http=True`）运行，内嵌模式与独立
`server.py` 两种形态一致。服务端不分配、也不校验 `Mcp-Session-Id`，每个请求自包含。

这样选的依据是代码事实：十个工具都不接收 FastMCP 的 `Context`，不使用 sampling、
elicitation、进度通知、资源订阅或服务端主动推送；续读游标本身是带 HMAC 签名的
自包含结构（见 `backend/agent_paging.py`），跨请求不需要服务端记忆。会话不承载任何业务语义。

此前的有状态模式只在进程内存里保存会话，容器重启或空闲超时后，客户端继续使用旧的
`Mcp-Session-Id` 会收到 `404` + `{"code":-32600,"message":"Session not found"}`。
改为无状态后，重启、重连和多副本都不再需要重新 `initialize`。

代价是服务端无法再主动联系客户端，即 sampling、elicitation、进度与订阅不可用。
本服务不提供这些能力，因此无功能损失；若将来要加，需同时改回有状态并重新评估部署形态。

客户端地址应写成带尾斜杠的 `/mcp/`。请求 `/mcp` 会收到 `307` 重定向到 `/mcp/`，
不跟随重定向的客户端会失败。

## 7. 离线验收

`tests/test_agent_protocol.py`、`test_agent_paging.py`、`test_agent_search.py`、`test_snippet.py` 覆盖 MCP 载荷、续读、版本失效、章节、OCR 回退、页图、空召回和来源偏移。`tests/test_mcp_stateless.py` 直接打 ASGI 传输层，断言不返回 `Mcp-Session-Id`、重复 `initialize` 均成功、携带任意旧 session id 仍返回 200（有状态模式下该用例会得到 `-32600 Session not found`），并保持 10 个工具与 `structured` 默认 false 的契约。夹具为临时文档，模型为确定性替身；协议测试禁网络连接。pi 扩展的适配测试在 `clients/pi/pdf-rag-pi/tests/`。

这些测试不等于新的端到端检索质量分数。真实语料排序质量仍以 [BENCHMARKS.md](BENCHMARKS.md) 的评测方法为准，不以协议测试宣称准确率提升。
