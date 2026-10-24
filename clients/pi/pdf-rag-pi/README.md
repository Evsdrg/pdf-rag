# pdf-rag-pi

pi 编码 agent 的原生接入包，注册 **10 个** `pdf_rag_*` 工具，与 MCP 同名，通过 REST v2 使用同一套有界 JSON 协议。

## 安装与配置

```bash
pi install <本目录路径>
export PDF_RAG_URL=http://127.0.0.1:8100
export PDF_RAG_TIMEOUT_MS=60000
```

`typebox` 和 pi SDK 由宿主供给，`fetch` 使用 Node 内置实现，无需安装运行依赖。此版要求支持 `/api/v2/*` 的后端，不静默回退旧响应。

## 工具

- `pdf_rag_search`、`pdf_rag_grep`：混合检索、按页聚合精确符号。
- `pdf_rag_read_page`、`pdf_rag_read_pages`：读页与有界续读。
- `pdf_rag_get_outline`、`pdf_rag_read_section`：目录和章节。
- `pdf_rag_list_categories`、`pdf_rag_list_files`：类别和分页文件列表。
- `pdf_rag_status`：只读本地状态及 OCR 最近真实调用，不探测上游。
- `pdf_rag_render_page`：本地按需 PDF 页图，返回原生图片块，不调用 OCR。

所有工具声明只读。文本结果在 `content` 返回一份 JSON，结构保留在 `details` 供宿主使用。`truncated=true` 时必须继续传 `next_cursor`；警告、降级、页码口径和引用规则见 [协议说明](../../../docs/MCP-PROTOCOL.md)。图片消费取决于 pi 宿主及模型支持，不能用文本坐标轴代替曲线读值。

## 离线测试

仓库前端依赖安装完成后，可从仓库根运行：

```bash
node --experimental-strip-types --test clients/pi/pdf-rag-pi/tests/adapter.test.mjs
```

测试用临时模块、TypeBox/宿主替身和 `fetch` 替身，验证十个工具注册、v2 请求参数、JSON 续读信息和图片载荷，不调用模型或实际服务。
