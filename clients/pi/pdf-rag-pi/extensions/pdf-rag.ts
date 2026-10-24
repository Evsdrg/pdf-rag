/** pi 原生适配:与 MCP 共用 REST v2 的有界 JSON 协议。 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const BASE = (process.env.PDF_RAG_URL ?? "http://127.0.0.1:8100").replace(/\/+$/, "");
const TIMEOUT_MS = Number(process.env.PDF_RAG_TIMEOUT_MS ?? 30000);

function url(path: string, params: Record<string, unknown>) {
	const qs = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		if (value !== undefined && value !== null && value !== "") qs.set(key, String(value));
	}
	return `${BASE}/api/v2/${path}${qs.size ? `?${qs}` : ""}`;
}

async function request(path: string, params: Record<string, unknown>) {
	const response = await fetch(url(path, params), { signal: AbortSignal.timeout(TIMEOUT_MS) });
	if (!response.ok) {
		const body = await response.text();
		throw new Error(`PDF-RAG HTTP ${response.status}: ${body.slice(0, 1000)}`);
	}
	return response;
}

const file = Type.String({ description: "库内相对路径,来自搜索/文件列表" });
const cursor = Type.Optional(Type.String({ description: "上一批的next_cursor;保持其余筛选条件不变" }));
const max_chars = Type.Optional(Type.Integer({ minimum: 256, maximum: 12000, description: "整次文本预算,默认8000" }));
const category = Type.Optional(Type.String({ description: "类别,先用list_categories读取" }));

export default function pdfRagExtension(pi: ExtensionAPI) {
	function register(name: string, label: string, description: string, path: string,
		parameters: ReturnType<typeof Type.Object>) {
		pi.registerTool({
			name: `pdf_rag_${name}`, label, description, parameters,
			annotations: { readOnlyHint: true },
			promptSnippet: description,
			promptGuidelines: [
				"返回是schema_version=2的JSON;truncated=true时使用next_cursor继续,不要当作完整内容。",
				"检查warnings/degraded;型号身份未确认和重排分都不是答案正确率。",
				"检索的是手册语料,不是工作区文件;status不主动探测上游。",
			],
			async execute(_id, params) {
				const response = await request(path, params);
				const data = await response.json();
				return { content: [{ type: "text", text: JSON.stringify(data) }], details: data };
			},
		});
	}

	register("search", "手册检索", "混合检索参数/规格,返回页码片段与块引用;检查降级提示。", "search", Type.Object({
		query: Type.String({ minLength: 1, maxLength: 200 }), category,
		top_k: Type.Optional(Type.Integer({ minimum: 1, maximum: 20 })),
		file: Type.Optional(Type.String({ description: "文件路径字面子串" })),
		max_per_doc: Type.Optional(Type.Integer({ minimum: 0, maximum: 20 })),
	}));
	register("grep", "手册精确查找", "正则查符号,不调用模型;每页聚合contexts,计数是索引文本口径。", "grep", Type.Object({
		pattern: Type.String({ minLength: 1, maxLength: 300 }), category,
		file: Type.Optional(Type.String()), cursor,
		max_hits: Type.Optional(Type.Integer({ minimum: 1, maximum: 100 })),
		context: Type.Optional(Type.Integer({ minimum: 0, maximum: 500 })),
		flex_separator: Type.Optional(Type.Boolean()),
	}));
	register("read_page", "手册读页", "读PDF物理页或Markdown一级标题伪页;低文本页可能调用OCR。", "page", Type.Object({
		file, page: Type.Integer({ minimum: 1 }), max_chars, cursor,
	}));
	register("read_pages", "手册多页", "一次读最多50页,pages如62-65;max_chars为整次预算。", "pages", Type.Object({
		file, pages: Type.String(), max_chars, cursor,
	}));
	register("read_section", "手册章节", "使用目录section_id读取章节,重复标题由标识区分。", "section", Type.Object({
		file, section_id: Type.String(), max_chars, cursor,
	}));
	register("get_outline", "手册目录", "分页取目录和section_id,默认前两级;PDF无书签时不猜章节。", "outline", Type.Object({
		file, cursor,
		max_level: Type.Optional(Type.Integer({ minimum: 1, maximum: 6 })),
		limit: Type.Optional(Type.Integer({ minimum: 1, maximum: 100 })),
	}));
	register("list_categories", "手册分类", "列出索引类别,不访问上游。", "categories", Type.Object({}));
	register("list_files", "手册文件", "分页列文件,默认30份;pages是索引最大页号,非物理总页数。", "files", Type.Object({
		category, cursor,
		file: Type.Optional(Type.String()), model_no: Type.Optional(Type.String()),
		kind: Type.Optional(Type.Union([Type.Literal("pdf"), Type.Literal("md")])),
		limit: Type.Optional(Type.Integer({ minimum: 1, maximum: 100 })),
	}));
	register("status", "手册状态", "只读索引规模与OCR最近真实调用,不探测模型或服务。", "status", Type.Object({}));

	pi.registerTool({
		name: "pdf_rag_render_page", label: "手册页图",
		description: "本地按需渲染PDF曲线/封装/原理图,不调用OCR;clip为归一化[x0,y0,x1,y1]。",
		annotations: { readOnlyHint: true },
		parameters: Type.Object({ file, page: Type.Integer({ minimum: 1 }),
			clip: Type.Optional(Type.Array(Type.Number(), { minItems: 4, maxItems: 4 })),
			max_size: Type.Optional(Type.Integer({ minimum: 256, maximum: 2400 })),
		}),
		async execute(_id, params) {
			const response = await request("render", { ...params, clip: params.clip ? JSON.stringify(params.clip) : undefined });
			const metadata = JSON.parse(response.headers.get("x-pdf-rag-metadata") ?? "{}");
			const data = Buffer.from(await response.arrayBuffer()).toString("base64");
			return { content: [
				{ type: "text", text: JSON.stringify(metadata) },
				{ type: "image", data, mimeType: "image/jpeg" },
			], details: metadata };
		},
	});
}
