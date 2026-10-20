/**
 * PDF-RAG —— 元器件手册库检索(pi 原生工具)
 *
 * 为什么用扩展而不是 MCP:pi 从 1.2 起已内置 MCP、也能直连 /mcp;但原生扩展
 * 是更贴合 pi 的接法 —— 工具进模型工具池、参数有 TypeBox schema、结果分
 * content(模型读)/details(渲染)两份载荷,与内置 read/grep 平级;还能用
 * promptSnippet/promptGuidelines 做分层提示词注入,且工具名不带 mcp__ 前缀。
 * (pi 0.87.x 时代无 MCP 客户端,扩展是当时唯一可行方案,故保留至今。)
 *
 * 为什么工具名带 pdf_rag_ 前缀:内置 grep 搜的是工作区文件系统,本库的
 * pdf_rag_grep 搜的是已索引的手册语料。同名会让模型选错工具。
 *
 * 零依赖:typebox 由 pi 供给,fetch 是 Node 全局。不需要 package.json,
 * 单文件放进 ~/.pi/agent/extensions/ 即可生效。
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const BASE = (process.env.PDF_RAG_URL ?? "http://127.0.0.1:8100").replace(/\/+$/, "");
const TIMEOUT_MS = Number(process.env.PDF_RAG_TIMEOUT_MS ?? 30000);

/** GET 一个 JSON 端点。失败抛错 —— execute 抛错会变成"失败的工具结果",模型能看到。 */
async function api<T = unknown>(path: string, params: Record<string, unknown> = {}): Promise<T> {
	const qs = new URLSearchParams();
	for (const [k, v] of Object.entries(params)) {
		if (v === undefined || v === null || v === "") continue;
		qs.set(k, String(v));
	}
	const url = `${BASE}${path}${qs.size ? `?${qs}` : ""}`;
	let res: Response;
	try {
		res = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT_MS) });
	} catch (e) {
		// 连不上/超时:给出可操作的提示,而不是裸 fetch 错误
		throw new Error(
			`无法连接 PDF-RAG 服务(${BASE})。请确认容器在运行、PDF_RAG_URL 指向正确地址。原因:${(e as Error).message}`,
		);
	}
	if (!res.ok) {
		const body = await res.text().catch(() => "");
		throw new Error(`PDF-RAG ${path} 返回 HTTP ${res.status}${body ? `: ${body.slice(0, 200)}` : ""}`);
	}
	return (await res.json()) as T;
}

/** 把检索结果渲染成模型易读的文本,并保留结构化 details 供渲染层使用。 */
function formatHits(hits: Array<Record<string, unknown>>): string {
	if (!hits.length) return "无命中。可换关键词、放宽 category,或用 pdf_rag_grep 精确查找。";
	return hits
		.map((h, i) => {
			const kind = h.kind === "md" ? "MD" : "PDF";
			const model = h.model_no || h.product || "";
			const head = `${i + 1}. [${h.file} p${h.page}] (${kind}${model ? ` ${model}` : ""})`;
			const score = h.rerank_score !== undefined ? ` rerank=${h.rerank_score}` : ` score=${h.score}`;
			return `${head}${score}\n${h.snippet}`;
		})
		.join("\n\n");
}

export default function pdfRagExtension(pi: ExtensionAPI) {
	// ---------- 检索 ----------

	pi.registerTool({
		name: "pdf_rag_search",
		label: "PDF-RAG 检索",
		description:
			"在元器件手册库(已索引的 PDF/Markdown 手册语料)中做混合检索:BM25 + 型号子串 + 向量三路召回,RRF 融合后重排,返回已定位到答案的片段窗口。这是查手册的首选入口。",
		promptSnippet: "在已索引的元器件手册库(PDF/Markdown)中检索某个主题",
		annotations: { readOnlyHint: true },
		promptGuidelines: [
			"查元器件参数、规格、引脚、电气特性时,优先用 pdf_rag_search(它检索的是已索引的手册语料,不是工作区文件)。",
			"要精确定位某个符号/型号串(如 VDD_APC、IddHP)用 pdf_rag_grep;它不走向量,断网或嵌入服务降级时最可靠。",
			"pdf_rag_search 返回的 file 字段是库内相对路径,直接传给 pdf_rag_read_page / pdf_rag_read_pages 读全文。",
			"若检索结果明显不合预期,先用 pdf_rag_status 确认索引与依赖是否正常。",
		],
		parameters: Type.Object({
			query: Type.String({ description: "查询内容,中英文均可,如 \"W25Q32 供电电压\"" }),
			category: Type.Optional(Type.String({ description: "按类别过滤,如 \"02_存储\";可先用 pdf_rag_list_categories 看全部类别" })),
			top_k: Type.Optional(Type.Number({ description: "返回条数,默认 5" })),
			file: Type.Optional(Type.String({ description: "只在文件名含该子串的文档内检索,如 \"QMC6309\"" })),
			max_per_doc: Type.Optional(Type.Number({ description: "同一文件最多返回几条,0=不限" })),
		}),
		async execute(_id, p) {
			// /api/search 直接返回命中数组(降级信息只在 MCP 侧包装;HTTP 侧保持裸列表,
			// 前端也按裸列表消费)。
			const hits = await api<Array<Record<string, unknown>>>("/api/search", {
				q: p.query,
				category: p.category,
				top_k: p.top_k ?? 5,
				file: p.file,
				max_per_doc: p.max_per_doc,
			});
			return {
				content: [{ type: "text", text: `命中 ${hits.length} 条:\n\n${formatHits(hits)}` }],
				details: { hits },
			};
		},
	});

	pi.registerTool({
		name: "pdf_rag_grep",
		label: "PDF-RAG 精确检索",
		description:
			"在手册库文本里按字面/正则精确检索,返回命中行及上下文。适合查精确符号(如 VDD_APC、IddHP、SMPA1)。不经过向量检索,天然不受嵌入服务可用性影响。注意:这搜的是手册语料,不是工作区文件(那用内置 grep)。",
		promptSnippet: "在手册库文本中做正则/字面检索(非工作区文件系统)",
		annotations: { readOnlyHint: true },
		promptGuidelines: [
			"默认 flex_separator 会把下划线/空白视为等价,因为 PDF 提取常丢失下标,同一符号有 \"VDD_APC\" 与 \"VDD APC\" 两种形态。",
		],
		parameters: Type.Object({
			pattern: Type.String({ description: "正则或字面串(正则特殊字符需转义),如 \"VDD_APC\"、\"2\\\\.4MHz\"" }),
			category: Type.Optional(Type.String({ description: "按类别过滤" })),
			file: Type.Optional(Type.String({ description: "只在文件名含该子串的文档内检索" })),
			max_hits: Type.Optional(Type.Number({ description: "最多命中数,默认 20" })),
			context: Type.Optional(Type.Number({ description: "命中处上下文字符数,默认 60" })),
			flex_separator: Type.Optional(Type.Boolean({ description: "下划线/空白视为等价,默认 true" })),
		}),
		async execute(_id, p) {
			const data = await api<{ hits: number; results: Array<Record<string, unknown>> }>("/api/grep", {
				pattern: p.pattern,
				category: p.category,
				file: p.file,
				max_hits: p.max_hits ?? 20,
				context: p.context ?? 60,
				flex_separator: p.flex_separator ?? true,
			});
			const rows = data.results ?? [];
			const text = rows.length
				? rows
						.map((r) => `[${r.file} p${r.page}] ${r.model_no ? `${r.model_no} | ` : ""}${r.match}\n  ${r.context}`)
						.join("\n")
				: "无命中。";
			return {
				content: [{ type: "text", text: `命中 ${data.hits} 处:\n\n${text}` }],
				details: { hits: data.hits, results: rows },
			};
		},
	});

	// ---------- 读取 ----------

	pi.registerTool({
		name: "pdf_rag_read_page",
		label: "PDF-RAG 读页",
		description:
			"读取手册某页的完整原文(含表格 markdown)。file 用 pdf_rag_search 返回的路径,page 从 1 开始。支持 PDF 与 Markdown(.md 按一级标题分页);扫描页会自动回退 OCR。",
		promptSnippet: "按库内相对路径读取手册的某一页",
		annotations: { readOnlyHint: true },
		parameters: Type.Object({
			file: Type.String({ description: "库内相对路径,来自 pdf_rag_search / pdf_rag_list_files" }),
			page: Type.Number({ description: "页码,从 1 开始" }),
		}),
		async execute(_id, p) {
			const data = await api<{ text?: string; error?: string; ocr?: boolean }>("/api/page", {
				file: p.file,
				page: p.page,
			});
			const body = data.text || data.error || "(空)";
			const ocrNote = data.ocr ? "\n\n[本页为 OCR 结果]" : "";
			return {
				content: [{ type: "text", text: body + ocrNote }],
				details: { file: p.file, page: p.page, ocr: data.ocr ?? false, error: data.error },
			};
		},
	});

	pi.registerTool({
		name: "pdf_rag_read_pages",
		label: "PDF-RAG 读多页",
		description:
			"一次读取手册多页,支持 \"62,63,64\" 或 \"62-65\"。规格表(绝对最大值表、PDN 表)常跨页,逐页读要多跑数次。单页越界会在对应项内回报,不中断其余页。",
		promptSnippet: "一次读取手册的多页(支持 62-65 这类范围)",
		annotations: { readOnlyHint: true },
		parameters: Type.Object({
			file: Type.String({ description: "库内相对路径" }),
			pages: Type.String({ description: '页码列表,如 "62,63" 或 "62-65"' }),
		}),
		async execute(_id, p) {
			const data = await api<{ total_pages: number; pages: Array<Record<string, unknown>> }>("/api/pages", {
				file: p.file,
				pages: p.pages,
			});
			const parts = (data.pages ?? []).map((pg) =>
				pg.error ? `--- 第 ${pg.page} 页:${pg.error} ---` : `--- 第 ${pg.page} 页 ---\n${pg.text}`,
			);
			return {
				content: [{ type: "text", text: `共 ${data.total_pages} 页\n\n${parts.join("\n\n")}` }],
				details: { file: p.file, total_pages: data.total_pages },
			};
		},
	});

	pi.registerTool({
		name: "pdf_rag_get_outline",
		label: "PDF-RAG 目录",
		description:
			"取手册的书签/标题目录(章节 + 页码),用于在大手册里先导航再精确读页。支持 PDF 与 Markdown。无目录时提示改用 pdf_rag_grep 定位关键节标题。",
		promptSnippet: "取手册的书签/标题目录",
		annotations: { readOnlyHint: true },
		parameters: Type.Object({
			file: Type.String({ description: "库内相对路径" }),
		}),
		async execute(_id, p) {
			const data = await api<{ total_pages: number; outline: Array<Record<string, unknown>>; note?: string }>(
				"/api/outline",
				{ file: p.file },
			);
			const toc = data.outline ?? [];
			const text = toc.length
				? toc.map((e) => `${"  ".repeat(Math.max(0, Number(e.level) - 1))}${e.title}  (p${e.page})`).join("\n")
				: data.note || "无目录。";
			return {
				content: [{ type: "text", text: `${p.file}(共 ${data.total_pages} 页)\n\n${text}` }],
				details: { file: p.file, entries: toc.length },
			};
		},
	});

	// ---------- 索引信息 ----------

	pi.registerTool({
		name: "pdf_rag_list_categories",
		label: "PDF-RAG 类别",
		description: "列出手册库中的所有类别目录,用于给 pdf_rag_search / pdf_rag_list_files 的 category 参数取值。",
		promptSnippet: "列出手册库的类别目录",
		annotations: { readOnlyHint: true },
		parameters: Type.Object({}),
		async execute() {
			const cats = await api<string[]>("/api/categories");
			return {
				content: [{ type: "text", text: `共 ${cats.length} 个类别:\n${cats.join("\n")}` }],
				details: { categories: cats },
			};
		},
	});

	pi.registerTool({
		name: "pdf_rag_list_files",
		label: "PDF-RAG 文件列表",
		description:
			"列出手册库中已索引的文件及元数据(file/category/model_no/product/pages/chunks)。用于确认某份文档是否已入库、有多少页,避免不必要地翻本地文件。",
		promptSnippet: "列出手册库已索引的文件及其元数据",
		annotations: { readOnlyHint: true },
		parameters: Type.Object({
			category: Type.Optional(Type.String({ description: "按类别过滤" })),
		}),
		async execute(_id, p) {
			const files = await api<Array<Record<string, unknown>>>("/api/files", { category: p.category });
			const text = files
				.map((f) => `${f.file}  [${f.category}] ${f.model_no || f.product || ""} ${f.pages}p/${f.chunks}块`)
				.join("\n");
			return {
				content: [{ type: "text", text: `共 ${files.length} 份文档:\n${text}` }],
				details: { files },
			};
		},
	});

	pi.registerTool({
		name: "pdf_rag_status",
		label: "PDF-RAG 状态",
		description:
			"手册库索引与依赖的健康状态(文档数/块数/类别数、OCR 后端)。检索结果质量突然变差时,先用它确认索引与依赖是否正常。",
		promptSnippet: "检查手册库索引与依赖的健康状态",
		annotations: { readOnlyHint: true },
		parameters: Type.Object({}),
		async execute() {
			const data = await api<Record<string, unknown>>("/api/stats");
			return {
				content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
				details: data,
			};
		},
	});
}
