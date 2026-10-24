# MCP / Agent 返回协议

本文记录 MCP 与唯一 REST 查询/读取接口 `/api/v2/*` 的返回契约。旧 `/api/search`、`page/pages/outline/grep/files/categories` 已移除，不保留兼容别名；Web 和 pi 扩展示例都使用统一协议。索引、配置、数据包管理及原文件下载接口不受此移除影响。

## 1. 返回与错误

文本工具返回一份 JSON 文本，含 `schema_version: 2`。不同时复制到 `structuredContent`，避免重复载荷。

- 单页：`file/kind/page/page_basis/total_pages/text/ocr/warnings`。
- 多页、章节：`file/kind/page_basis/total_pages/pages[]`；单页越界在该项内返回 `error`，其余项继续。
- 文件列表：`files/count/total/truncated/next_cursor`。
- 目录：`outline/count/total/truncated/next_cursor`；条目含 `section_id`。
- 精确查找：`results/count/total`，一项对应一页，内含 `contexts[]`。
- 搜索：`results/count/degraded/notice/warnings/identity/vector_partitions/cached/counts`。

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

搜索的 `snippet` 使用经过保守展示处理的窗口，并提供 `snippet_ref`：`chunk_id/index_md5/start_offset/end_offset/offset_basis/truncated_before/truncated_after/table_header/warnings`。偏移基于索引块，不是实时读页或图像坐标。展示可有限扩展到行边界、移除无意义控制字符，但不会猜测修复单位、公式、乱码；送重排器的窗口不因此改变。

旧索引不含 OCR 来源、页内坐标、原始表格单元格关系，不能从引用字段推断这些信息。响应协议更新不需要重建索引，也不会自动触发索引。

## 4. 精确查找与诊断

`grep` 按文件/页聚合，每页最多五个不同上下文；同页正文和表格的确定重复可合并，不同条件行保留。`indexed_matches` 是索引文本出现次数（可能包含正文/表格重复和分块重叠），不等于印刷页次数；`contexts_truncated` 表示上下文尚未完整展示。最多返回 100 页，可用游标继续。

向量通道成功但无命中是正常空召回，不是服务故障。降级按全文、子串、嵌入、分区、维度、覆盖率、重排区分，空结果仍给出诊断；不缓存降级结果。

`identity` 只是查询中的候选型号与返回文件身份是否匹配。`unconfirmed` 不等于全库不存在，也不据此过滤结果。`rerank_score` 是相关性分数，不是答案正确率概率。

## 5. 按需页图

`pdf_rag_render_page(file, page, clip?, max_size=1600)` 在本地用 MuPDF 渲染 PDF，一次一页，不调用 OCR、视觉、嵌入或重排服务。

- `clip=[x0,y0,x1,y1]` 为当前页面方向的归一化坐标，需满足 `0≤x0<x1≤1`、`0≤y0<y1≤1`。
- 最长边 256–2400 像素，默认 1600；JPEG 不超过 2 MB，必要时自动缩小。
- MCP 返回一段引用 JSON 和一个原生图片块，不把 base64 塞进文本。
- `GET /api/v2/render` 返回 JPEG 二进制，引用 JSON 位于 `X-PDF-RAG-Metadata`，不落盘、不缓存响应。
- Markdown 不支持页图；是否能消费图片取决于客户端及其模型能力。

## 6. REST v2 对照

| MCP 工具 | HTTP v2 |
|---|---|
| `pdf_rag_search` | `GET /api/v2/search?query=...` |
| `pdf_rag_grep` | `GET /api/v2/grep?pattern=...` |
| `pdf_rag_read_page` | `GET /api/v2/page?file=...&page=...` |
| `pdf_rag_read_pages` | `GET /api/v2/pages?file=...&pages=...` |
| `pdf_rag_read_section` | `GET /api/v2/section?file=...&section_id=...` |
| `pdf_rag_get_outline` | `GET /api/v2/outline?file=...` |
| `pdf_rag_list_files` | `GET /api/v2/files` |
| `pdf_rag_list_categories` | `GET /api/v2/categories` |
| `pdf_rag_status` | `GET /api/v2/status` |
| `pdf_rag_render_page` | `GET /api/v2/render?file=...&page=...` |

除 `render.clip` 在 HTTP 查询中用 JSON 字符串表示外，参数名与 MCP 相同。Web 与 pi 使用同一结构，不在客户端猜测旧数组响应。

## 7. 离线验收

`tests/test_agent_protocol.py`、`test_agent_paging.py`、`test_agent_search.py`、`test_snippet.py` 覆盖 MCP 载荷、续读、版本失效、章节、OCR 回退、页图、空召回和来源偏移。夹具为临时文档，模型为确定性替身；协议测试禁网络连接。pi 扩展的适配测试在 `clients/pi/pdf-rag-pi/tests/`。

这些测试不等于新的端到端检索质量分数。真实语料排序质量仍以 [BENCHMARKS.md](BENCHMARKS.md) 的评测方法为准，不以协议测试宣称准确率提升。
