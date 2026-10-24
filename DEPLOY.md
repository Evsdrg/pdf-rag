# 部署说明

面向把本系统部署到另一台机器（或交付给他人）的场景。仓库自身的开发说明见 [README.md](README.md)。

交付包（`pdf-rag-<日期>.tar.zst`，也提供 `.zip`）里已经包含**项目源码 + 原始手册 PDF + 解析后数据 + 预处理好的向量索引**，正常情况下**不需要重新索引**，解压配好 `.env` 就能跑。

## 〇、解压

包是 **zstd 压缩的 tar**（`.tar.zst`）。Windows 资源管理器不能直接打开，任选一种：

```bash
# 1) 有 7-Zip / WinRAR:直接右键解压(它们认得 .tar.zst)
# 2) 装了 zstd 命令行:
zstd -d pdf-rag-<日期>.tar.zst        # 得到 .tar
tar -xf pdf-rag-<日期>.tar           # 再解开
# 3) 用 Python(目标机本来就要装 Python):
python -c "import tarfile,zstandard as z; \
f=open('pdf-rag-<日期>.tar.zst','rb'); \
tarfile.open(fileobj=z.ZstdDecompressor().stream_reader(f), mode='r|').extractall('.')"
```

解压后顶层是一个 `pdf-rag-<日期>/` 目录。**路径尽量不含中文与空格**（Python 多进程与部分依赖对中文路径敏感）。

## 一、交付包内容

```
pdf-rag-<日期>/
├── DEPLOY.md                  本文档(部署方法)
├── README.md                  项目说明
├── MANIFEST.txt               构建信息:构建时间、提交号、文档/块数、所用嵌入服务与模型
├── .env.example               配置模板
├── backend/                   FastAPI 应用 + 检索核心 + 索引构建 + 数据包
├── server.py                  MCP 服务
├── ocr_service.py             OCR 服务(可选)
├── run_backend.py             后端守护启动脚本
├── eval_retrieval.py / eval_queries.json   检索质量评测
├── tools/                     诊断与维护脚本(含 compact_index.py、build_vec_index.py、build_release.py)
├── web/                       前端源码 + **已构建好的 dist/**
├── pdf/                       原始手册(份数以 MANIFEST.txt 为准;目录结构与索引一致)
├── parsed/                    解析后数据(见下)
└── index.lance/               向量索引,含全文索引(块数以 MANIFEST.txt 为准)
```

三份数据的关系:

| 目录 | 内容 | 用途 |
|---|---|---|
| `pdf/` | 原始 PDF | 逐字原文、人工查阅 |
| `parsed/` | 解析后数据:`chunks.jsonl`(每块一行,含文本与元数据)+ `pages/*.txt`(按页重建的可读文本) | 审阅提取质量;重建索引时不必重新解析 PDF |
| `index.lance/` | 向量 + 全文索引 | 直接检索,**无需重建** |

`parsed/` 与索引同源(取自索引,未重新解析 PDF),页级文本的重建保真度说明见 `parsed/README.txt`。

## 二、前置条件

| 项 | 要求 | 说明 |
|---|---|---|
| Python | **3.13** | 用 [uv](https://docs.astral.sh/uv/) 管理；`uv.lock` 已随包提供 |
| 磁盘 | 按实际交付包预留 | 手册与索引体积见包内 MANIFEST.txt，另需依赖与运行余量 |
| 嵌入/重排 API | 需可访问 | OpenAI 兼容的 `/v1/embeddings` 与 `/v1/rerank`；**用自己的 API Key** |
| Node.js | **不需要** | 包内已含构建好的 `web/dist`；只有改前端源码时才需要 |
| OCR 环境 | 可选 | 仅扫描版 PDF 需要；4.9 GB，见第五节 |

> 显卡/内存：OCR 用 GPU 时需 CUDA 环境。不装 OCR 也能正常检索，只是扫描页无法取文（会提示）。

## 三、部署步骤

### 1. 解压

见上文「〇、解压」。解压到任意路径，例如 `D:\pdf-rag`。

### 2. 装后端依赖

```bash
cd D:\pdf-rag
uv sync
```

### 3. 写 `.env`

复制 `.env.example` 为 `.env`，按下表填写。**`PDF_ROOT` 与 `DB_PATH` 可以留空**——留空时会自动用包内布局（`<项目>/pdf`、`<项目>/index.lance`），这正是交付包的目录结构，所以通常只需填嵌入服务那几项。

```ini
# 手册与索引位置(留空 = 用包内布局,推荐)
PDF_ROOT=
DB_PATH=

# 嵌入 / 重排服务 —— 必须与包内索引所用模型一致,见下
EMBED_BASE_URL=https://api.example.com/v1     # 换成你自己的服务商地址
EMBED_API_KEY=你的key
EMBED_MODEL=qwen3-embedding-8b
RERANKER_MODEL=qwen3-reranker-8b

# OCR 服务地址(装了 OCR 才需要)
OCR_URL=http://127.0.0.1:8900

# 管理接口令牌(留空则 /api/admin/* 一律 403,无法重启后端)
# 生成:python -c "import secrets; print(secrets.token_hex(16))"
ADMIN_TOKEN=
```

> ⚠️ **`EMBED_MODEL` 必须与包内索引所用模型一致**。向量只在同一模型、同一向量空间下才可比；
> 换了模型，已有向量与新查询向量对不上，检索会**静默变差**而不是报错。
> 包内 `MANIFEST.txt` 记录了构建时所用的服务地址与模型，照抄即可。
> 确实要换模型：改完 `.env` 后必须**全量重建索引**（见第六节），否则结果不可信。
>
> ⚠️ API Key **不会随包提供**，需自行填入。密钥只从环境读取，不写入任何配置文件或数据包。

### 4. 启动

```bash
# 后端(守护式:崩溃自动重启 + 单例锁)
uv run run_backend.py                    # http://127.0.0.1:8100

# OCR 服务(可选,见第五节)
ocr-env\Scripts\python.exe ocr_service.py
```

打开 `http://127.0.0.1:8100` 即为 Web 界面；「索引状态」页应显示导入的文档与块数，
以包内 `MANIFEST.txt` 和页面实际数据为准。

### 5. 验证

```bash
# 健康检查
uv run python -c "import json,urllib.request;print(json.load(urllib.request.urlopen('http://127.0.0.1:8100/api/stats'))['files'],'份文档')"

# 跑评测(可选,确认检索质量与索引匹配)
uv run python eval_retrieval.py
```

`eval_retrieval.py` 末尾会打印 `degraded` 计数——**若不为 0 说明嵌入接口被限流**，该次分数不代表系统水平，请稍后重跑。
当前基线与历次实验记录见 [BENCHMARKS.md](docs/BENCHMARKS.md)。

## 四、MCP 接入（给 LLM 用）

在客户端的 MCP 配置里加一项（以 ZCode 为例，路径按实际部署位置改）：

```json
{
  "pdf-rag": {
    "type": "stdio",
    "command": "D:\\pdf-rag\\.venv\\Scripts\\python.exe",
    "args": ["D:\\pdf-rag\\server.py"],
    "cwd": "D:\\pdf-rag",
    "timeoutMs": 60000
  }
}
```

`cwd` 必须是项目根目录。注册后可用 8 个工具（统一 `pdf_rag_` 前缀，与客户端自带的
`grep`/`read` 区分）：`pdf_rag_search` / `pdf_rag_grep` / `pdf_rag_read_page` /
`pdf_rag_read_pages` / `pdf_rag_get_outline` / `pdf_rag_list_categories` /
`pdf_rag_list_files` / `pdf_rag_status`。

> MCP 服务与后端 API **各自独立**：MCP 直接读 LanceDB，不依赖 8100 端口在跑。
> 但两者都不要同时写索引（重建索引时建议先停 MCP 查询，或接受一次短暂的不一致）。

> **想让 MCP 与后端共用进程**（省一个约 650 MiB 的 Python 进程，并让两侧共享
> 元数据缓存）：在 `.env` 设 `MCP_INPROC=1`，MCP 会挂在后端同端口的 `/mcp` 路径下，
> 客户端改用 `"type": "http", "url": "http://<host>:8100/mcp"`。
> 这是当前生产（NAS）采用的形态。内网部署记录 `DEPLOY-NAS.md` 含内网地址与账号，
> 仅存于部署机、不随仓库分发。

## 五、OCR 服务（可选）

只处理**没有文本层的扫描页**。不装也能用，扫描页会返回空文本。

包内**不含** `ocr-env`（4.9 GB）。在项目根目录重建：

```bash
uv venv ocr-env --python 3.12
# GPU 版(需 CUDA)
ocr-env\Scripts\python.exe -m pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
# 或 CPU 版
# ocr-env\Scripts\python.exe -m pip install paddlepaddle==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
ocr-env\Scripts\python.exe -m pip install "paddleocr==3.7.0" "paddlex==3.7.2"
```

首次运行会自动下载模型（约数百 MB）。服务行为：

- 监听 `127.0.0.1:8900`，接口 `GET /health`、`POST /ocr`。
- **空闲 300s 自动卸载模型**释放显存（`OCR_IDLE_TIMEOUT_SECONDS` 可调）。
- 推理**串行化**：PP-StructureV3 管线非线程安全，并发会让 shape 冲突。
- 模型缓存重定向到项目内 `.paddlex_cache/`，避免用户主目录下的缓存目录损坏。

## 六、索引维护

```bash
uv run python -m backend.ingest             # 增量(按 MD5 跳过未变化)
uv run python -m backend.ingest --rebuild   # 全量重建
```

- 加了新 PDF 后：把文件放进 `pdf/<类别>/` 再跑增量索引。
- **换了嵌入模型后：必须 `--rebuild`**（增量不会重算已有文档的向量）。
- 重建的进度实时写入 `run_state.json`，Web「索引状态」页可看。
- 索引里存的是**相对路径**（如 `01_传感器/xxx.PDF`），所以移动整个 `pdf/` 目录不影响，改 `PDF_ROOT` 即可。

**碎片整理**：增量索引每跑一次留一个新版本，长期累积磁盘占用远超真实数据（实测本仓库
8561 块真实数据约 26 MB，目录曾涨到 248 MB / 517 版本 / 1457 文件，约 9 倍）：

```bash
uv run python tools/compact_index.py            # 合并碎片 + 清理 1h 前的旧版本
uv run python tools/compact_index.py --dry-run  # 只看现状
```

不改任何一行数据。作者最近一次实测：**128 MB / 521 版本 / 228 文件 → 43 MB / 8 文件**，
行数与全文索引不变，检索结果一致。清理后重启后端，让它在最新版本上重新持有句柄。

**向量索引**：每个向量分区带一个 `IvfFlat` 索引(查询侧配 `refine_factor=2`)。
正常流程会自动维护 —— 增量索引、`--rebuild-vectors`、迁移脚本建完分区后都会重建。
只有老版本建成的索引库需要手动补一次：

```bash
uv run python tools/build_vec_index.py            # 缺索引的分区补建,已有的跳过
uv run python tools/build_vec_index.py --rebuild  # 全部重建
```

- 不补也能用,只是退化为暴力扫描(结果同样精确,只是慢)
- 分区少于 4096 行时**拒绝**建索引:Lance 的 KMeans 在小数据上产出空簇,
  索引结果与暴力扫描不一致 —— 此时暴力扫描既更快也更准
- 实测收益:生产 12421 块,向量检索 59.9ms → 32.8ms;建索引耗时 0.5s

## 七、数据包（迁移到另一套实例）

Web「数据」页或接口可把索引+PDF+配置打成 `.tar.zst`：

```bash
# 构建(含 PDF)
curl -X POST "http://127.0.0.1:8100/api/export/bundle?include_docs=true&level=3"
# 预检:看包内服务配置与本地差异、是否阻断
curl -X POST -H "Content-Type: application/json" -d '{"name":"包文件名"}' http://127.0.0.1:8100/api/import/inspect
# 导入
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"包文件名","restore_docs":true,"replace_index":true,"apply_provider":true}' \
     http://127.0.0.1:8100/api/import/bundle
```

导入前会**自动备份**现有索引到 `index.lance.bak-<时间戳>`。

**数据与模型强绑定**：包内声明了构建时的嵌入服务与模型。导入时

- 勾选「应用包内服务配置」→ 数据与模型重新配对，可用；
- 不勾选、且本地模型与包内不一致 → **明确拒绝导入**（避免新旧向量混用导致检索静默劣化）。

密钥不入包：对方用自己的 Key 访问同一个服务地址即可。

## 八、运维要点

| 事项 | 说明 |
|---|---|
| 端口 | 后端固定 `8100`（可用环境变量 `BACKEND_PORT` 改）；OCR `8900` |
| 重启/关闭 | `POST /api/admin/restart` / `/api/admin/shutdown`，需 `X-Admin-Token` 头 |
| 守护 | `run_backend.py` 拉起 uvicorn，异常退出后自动重启；日志 `logs/backend.log` |
| 单例锁 | `run_backend.lock` 用文件字节锁，进程崩溃由系统释放，**不会出现"锁被永久占用"** |
| 配置改动 | 改 `.env` 后需重启后端；`data/settings.json`（可调参数）即时生效，无需重启 |
| 可调参数 | 51 项 / 9 组，Web「检索配置」页可运行时修改、**即时生效**；覆盖值存 `data/settings.json`（不入版本库） |
| 日志 | `logs/backend.log`（后端）、`logs/ocr.log`（OCR） |

## 九、常见问题

**Q：`uv sync` 很慢或失败？** 需要能访问 PyPI。若目标机有内网源，先在 `~/.config/uv/uv.toml` 或环境变量里配镜像。

**Q：首屏「索引状态」页显示 0 分块 / 0 MB，是不是索引不认？** 不是。那个页面读的是**索引进度**（`run_state.json`，运行期产物，不随包提供），不是索引内容。实际文档数与分块数看「文件库」页，或 `GET /api/stats`（应与包内 `MANIFEST.txt` 一致）。跑一次索引后该页就会显示进度信息。

**Q：`data/settings.json` 不存在，要紧吗？** 不要紧。它是运行时覆盖值，默认值都在 `backend/config.py` 里，没有这个文件就是全默认值。

**Q：打开 8100 是空白页？** `web/dist` 缺失或不完整。确认包内存在 `web/dist/index.html`；或自行 `cd web && pnpm install && pnpm build`（仓库用 pnpm，有 `pnpm-lock.yaml`）。

**Q：检索结果明显不对/质量差？**
1. 先跑 `uv run python eval_retrieval.py`，看 `degraded` 是否非空——限流会导致分数虚低；
2. 再核对 `EMBED_MODEL` 是否与 `MANIFEST.txt` 记录的一致——不一致必须 `--rebuild`；
3. 最后看「索引状态」页的文档数是否为 205。

**Q：扫描版 PDF 取不到文字？** 没启动 OCR 服务。见第五节。也可在「文件库」页勾选该文件后点重新索引。

**Q：端口 8100 被占用？** 守护启动时会等待 30s，仍被占用则退出并记日志。改 `BACKEND_PORT`，或找到占用进程释放。

**Q：后台进程看起来有两层 PID？** 正常。`uv` 创建的 venv 里 `python.exe` 是启动器存根，会再 exec 真正的解释器，所以一个逻辑进程显示为两层 PID，**不要当成重复进程去 kill**。


## 十、API 参考（完整端点表）

| 端点 | 说明 |
|---|---|
| `GET /api/search?q=&category=&top_k=&mode=&rerank=&file=&max_per_doc=` | 混合检索 |
| `GET /api/grep?pattern=&category=&file=&max_hits=&context=&flex_separator=` | 正则精确检索 |
| `GET /api/page?file=&page=` | 单页原文（低文本页回退 OCR） |
| `GET /api/pages?file=&pages=62-65` | 多页 |
| `GET /api/outline?file=` | 书签目录 |
| `GET /api/pdf?file=` | 原文内联（PDF 可用 `#page=N` 深链；MD 走下载） |
| `GET /api/stats` | 文档数/块数/类别分布/索引历史 |
| `GET /api/categories` | 全部类别目录 |
| `GET /api/files?category=` | 文件清单与元数据（含提取质量字段） |
| `GET /api/extract/report?limit=` | 逐文档提取质量体检（低文本页标记） |
| `GET /api/history` | 索引历史 |
| `GET /api/state` | 索引进度 |
| `GET /api/config` | 读全部可调参数（含中文名/默认值/范围/是否被覆盖） |
| `PUT /api/config` | 保存可调参数（即时生效） |
| `POST /api/config/reset` | 恢复默认（全部或指定项） |
| `GET /api/ocr/health` | OCR 配置 + 最近一次真实调用（不探测） |
| `POST /api/ingest?rebuild=` · `POST /api/ingest/files` | 触发索引 / 重跑指定文件 |
| `GET /api/export/config` · `POST /api/import/config` | 配置导出导入（不含密钥） |
| `POST /api/export/bundle` · `GET /api/export/bundles` · `GET /api/export/download` · `DELETE /api/export/bundle` | 数据包构建/列表/下载/删除 |
| `POST /api/import/inspect` · `POST /api/import/bundle` | 导入预检 / 执行导入 |
| `POST /api/admin/restart` | 重启后端（需 `X-Admin-Token`） |
| `POST /api/admin/shutdown` | 关闭后端（需 `X-Admin-Token`） |

所有接受 `file` 的端点只认**语料库内的相对路径**（正斜杠；Windows 风格反斜杠会自动
归一），绝对路径与 `..` 穿越一律拒绝。`/api/search` 与 `/api/grep` 的 `file` 过滤按
**字面子串**匹配（`%`/`_` 不作通配符解释）。
