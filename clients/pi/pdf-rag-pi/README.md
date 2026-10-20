# pdf-rag-pi —— pi 的原生 PDF-RAG 接入

给 **pi 编码 agent** 用的 PDF-RAG 接入包。pi 从 1.2 起已内置 MCP，但这里仍用 pi 的
原生途径，因为它更贴合 pi 的工具面（见下）：

| 组成 | 文件 | 作用 |
|---|---|---|
| **扩展** | `extensions/pdf-rag.ts` | 注册 8 个带 TypeBox schema 的工具，直接打 pdf-rag 的 REST API |
| **技能** | `skills/pdf-rag/SKILL.md` | 领域知识：三条检索路径怎么选、引用规范、易踩的坑 |

## 为什么用原生扩展而不是 MCP

pi 原生扩展与 MCP 都能接到同一个后端，但原生扩展有几处优势：

- **有 schema**：参数是 TypeBox 类型化 schema，模型不用靠拼字符串（引号/转义/中文/正则都是出错面）。
- **双载荷结果**：返回 `content`（模型读）+ `details`（渲染用）两份，而非一段纯文本。
- **分层提示词注入**：`promptSnippet`/`promptGuidelines` 能进系统提示；MCP 工具只能靠 docstring。
- **工具名干净**：扩展是 `pdf_rag_search`，MCP 会是 `mcp__pdf-rag__pdf_rag_search`。

路线图上曾考虑"把 MCP 包一层命令行再 shell 出去"，这是最差的做法：丢 schema、
结果降级成 stdout 文本、`degraded`（嵌入/重排降级）信号与普通文本混在一起、
每次调用多 fork 一个进程。已放弃。

## 安装

```bash
pi install <本目录路径>
```

装进 `~/.pi/agent/settings.json` 的 `packages`。**零 npm 依赖**（`typebox` 由 pi 供给，
`fetch` 是 Node 全局），不需要 `npm install`、不需要构建。

## 配置

默认连 `http://127.0.0.1:8100`。覆盖：

```bash
export PDF_RAG_URL=http://your-pdf-rag-host:8100
export PDF_RAG_TIMEOUT_MS=60000                # 默认 30000
```

## 工具

8 个，与 MCP 侧同名（统一 `pdf_rag_` 前缀，和 pi 自带的 `grep`/`read` 明确区分——
后者搜工作区文件系统，这里搜手册语料）：

`pdf_rag_search` · `pdf_rag_grep` · `pdf_rag_read_page` · `pdf_rag_read_pages` ·
`pdf_rag_get_outline` · `pdf_rag_list_categories` · `pdf_rag_list_files` · `pdf_rag_status`

底层是 pdf-rag 的 HTTP API（`/api/search` `/api/grep` `/api/page` `/api/pages`
`/api/outline` `/api/categories` `/api/files` `/api/stats`）。其中 `grep`/`pages`/
`outline` 三个 REST 端点是为非 MCP 客户端新补的（原先只在 MCP 侧有）。

8 个工具全部声明 `annotations: { readOnlyHint: true }`——它们只读。不带这个注解时，
pi 按 MCP 默认语义把工具当作"可能破坏数据、可能触达开放世界"，权限门控扩展（如
`permission-gate.ts`）会对每次调用弹确认框。该字段是 pi 1.2 新增的，0.87.1 会静默
忽略它，故两个版本都能用。

## 与 pi 1.2 的兼容性

**在 pi 1.2.0 上实测：8 工具 + 技能全部正常加载与执行，无需改动。** 依赖的 API 面
（`registerTool`、`ToolDefinition` 的 `name`/`label`/`description`/`promptSnippet`/
`promptGuidelines`/`parameters`/`execute`、`pi.extensions`/`pi.skills` 清单）均未变。
1.2 新增的字段（`outputSchema`/`exposure`/`namespace`/`reachesTools`/`defaultActive`/
`annotations`）全部可选，我们只用 `annotations`。

两个需知的版本差异（均不影响本插件）：

- `execute` 第 5 个参数的类型名由 `ExtensionContext` 改为 `ExtensionToolContext`。
  本扩展不使用该参数，无影响。
- **pi 1.2 已内置 MCP 客户端**（`pi mcp add`、`/mcp`、`~/.pi/agent/mcp.json`），
  工具命名为 `mcp__<server>__<tool>`。我们仍维持扩展方案：MCP 方式拿不到 pi 原生的
  `promptSnippet`/`promptGuidelines` 分层注入，且工具名会多一层前缀。两者命名空间
  不相干（`pdf_rag_*` vs `mcp__*`），并存不冲突。

## 开发时的快速校验

不需要起模型。用 pi 自带的 SDK 加载本包,看工具与技能是否注册成功:

```bash
# pi 的包目录带内容哈希;直接解析 pi 启动器里指向的那份(同一版本可能有多个哈希目录)
PKG=$(sed -n 's|.*\(.*/node_modules/@earendil-works/pi-coding-agent\).*|\1|p' \
      "$(readlink -f "$(command -v pi)")" | head -1)
[ -d "$PKG" ] || { echo "未解析到 pi 包目录,请检查 pi 安装"; exit 1; }
cat > "$PKG/_check.mjs" <<'EOF'
import { DefaultResourceLoader, getAgentDir } from "@earendil-works/pi-coding-agent";
const loader = new DefaultResourceLoader({ cwd: "/tmp", agentDir: getAgentDir() });
await loader.reload();
const ext = loader.getExtensions().extensions.find((e) => e.path.includes("pdf-rag.ts"));
console.log("工具数:", ext?.tools.size ?? 0, "| 错误:", JSON.stringify(loader.getExtensions().errors));
for (const [name, t] of ext?.tools ?? []) console.log(" ", name, "|", t.definition.promptSnippet);
console.log("技能:", loader.getSkills().skills.filter((s) => s.name === "pdf-rag").length);
EOF
node "$PKG/_check.mjs"; rm -f "$PKG/_check.mjs"
```

期望输出:工具数 8、错误 `[]`、技能 1。注意脚本必须放在包目录内运行——ESM 从脚本自身
位置解析 `@earendil-works/pi-coding-agent`,放 `/tmp` 会 `ERR_MODULE_NOT_FOUND`。
