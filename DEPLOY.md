# 部署指南

本文只回答**如何安装、配置并启动系统，以及怎样接入 MCP**。索引维护、数据包迁移和故障排查见[运维手册](docs/OPERATIONS.md)，参数优先级和模型切换见[配置说明](docs/CONFIGURATION.md)。

## 1. 选择部署方式

| 方式 | 适用场景 | 启动入口 |
|---|---|---|
| 仓库 + uv | 本机开发或裸机运行 | `uv run run_backend.py` |
| 仓库 + Docker Compose | 单容器部署 Web、REST 和 MCP | `docker compose up -d --build` |
| 交付包 | 将源码、索引和可选手册一起迁移到另一台机器 | 解压后按包内布局启动 |

三种方式共用 `.env` 和 `data/settings.json` 的配置语义。默认监听 `127.0.0.1:8100`；容器或局域网部署需按实际环境设置 `BACKEND_HOST=0.0.0.0`。

## 2. 仓库部署

### 2.1 准备配置

要求 Python 3.13 和 [uv](https://docs.astral.sh/uv/)。前端 `web/dist` 已随仓库提供，不修改前端时不需要 Node.js。

```bash
cp .env.example .env
```

至少核对手册路径、索引路径和嵌入服务。`EMBED_API_KEY` 由部署者自行提供，不随仓库或数据包分发。不要用文档中的示例地址、模型或维度覆盖自己索引的实际契约；完整规则见[配置说明](docs/CONFIGURATION.md)。

```bash
uv sync
uv run run_backend.py
```

Docker Compose 则在准备 `.env` 后运行：

```bash
docker compose up -d --build
docker compose ps
```

更新代码时重建镜像，再 `docker compose up -d --pull never`。不要用代码同步命令覆盖 `.env`、`data/`、`index.lance/`、日志或手册目录。

### 2.2 验证

打开 `http://127.0.0.1:8100`，再检查统计接口：

```bash
python -c "import json,urllib.request; print(json.load(urllib.request.urlopen('http://127.0.0.1:8100/api/stats'))['files'])"
```

首次没有索引时，先通过 Web「索引状态」手动运行增量索引。文档数以 `/api/stats` 和文件库为准；`run_state.json` 只表示最近一次任务进度，不是索引内容清单。

## 3. 交付包部署

`tools/build_release.py` 可生成 `.tar.zst`、`.zip` 或两者。包内容取决于构建选项：

```text
pdf-rag-<日期>/
├── backend/、server.py、run_backend.py
├── web/                    前端源码与已构建 dist
├── .env.example、DEPLOY.md、MANIFEST.txt
├── pdf/                    索引引用的原始 PDF/Markdown（可选）
├── parsed/                 块级 JSONL 与按页重建文本，供审阅
└── index.lance/            主表、全文索引和向量分区
```

`MANIFEST.txt` 记录源码提交、数量、体积和当前服务配置；所有向量分区的契约以索引内 `vec_meta` 为准。`parsed/` 是审阅材料，不是服务启动的额外索引。

### 3.1 解压

`.tar.zst` 是 zstd 压缩的 tar。可使用支持该格式的 7-Zip/WinRAR，或：

```bash
zstd -d pdf-rag-<日期>.tar.zst
tar -xf pdf-rag-<日期>.tar
```

也可在 Python 3.13 中解包**可信的自有交付包**：

```bash
python -c "import tarfile,zstandard as z; f=open('pdf-rag-<日期>.tar.zst','rb'); tarfile.open(fileobj=z.ZstdDecompressor().stream_reader(f),mode='r|').extractall('.',filter='data')"
```

`.zip` 用常见解压工具即可。随后进入解压目录，复制 `.env.example` 为 `.env`，按 `MANIFEST.txt` 与 `vec_meta` 核对服务配置，执行 `uv sync` 和 `uv run run_backend.py`。`PDF_ROOT`、`DB_PATH` 留空时分别使用包内 `pdf/` 和 `index.lance/`。

包内已有索引时通常不需要重新提取或嵌入。只有文件、提取策略或目标向量分区需要变化时，才按[运维手册](docs/OPERATIONS.md)选择对应命令。

## 4. 接入 MCP

系统提供 10 个 `pdf_rag_*` 工具。MCP 与后端默认同进程、同端口挂载在 `/mcp`；也可独立以 stdio 运行。两种接入方式按需选择，不要求同时配置。

### 4.1 Streamable HTTP

```json
{
  "type": "http",
  "url": "http://127.0.0.1:8100/mcp",
  "timeoutMs": 60000
}
```

更新服务后，旧 MCP 会话可能失效，需要重启或重连客户端。容器健康不等于旧会话仍有效。

### 4.2 独立 stdio

```json
{
  "type": "stdio",
  "command": "<项目>/.venv/bin/python",
  "args": ["<项目>/server.py"],
  "cwd": "<项目>",
  "timeoutMs": 60000
}
```

Windows 将 Python 路径改为 `.venv\\Scripts\\python.exe`。`cwd` 必须是项目根目录，以便读取 `.env`、语料和索引。独立进程仍与后端共享同一套领域逻辑，但不应同时执行多个索引写任务。

工具清单、返回字段和调用顺序见[MCP/Agent 协议](docs/MCP-PROTOCOL.md)，HTTP 对照见[API 参考](docs/HTTP-API.md)。pi 的原生接入包见[客户端说明](clients/pi/pdf-rag-pi/README.md)。

## 5. 可选：本地 OCR 环境

需要本机 PaddleOCR 时，单独建立约 4.9 GB 的 `ocr-env`，不要让它的依赖替换后端环境。远程 OCR 不需要此环境，配置方式见[配置说明](docs/CONFIGURATION.md)。

```bash
uv venv ocr-env --python 3.12
```

安装 Paddle 和 OCR 组件（Windows 示例）：

```bash
ocr-env\Scripts\python.exe -m pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
# CPU 可改装 paddlepaddle==3.2.1 的 CPU 包
ocr-env\Scripts\python.exe -m pip install "paddleocr==3.7.0" "paddlex==3.7.2"
ocr-env\Scripts\python.exe ocr_service.py
```

Linux/macOS 将可执行文件路径换成 `ocr-env/bin/python`。GPU 包要求匹配的 CUDA 环境；CPU 不需要 GPU。

本地服务默认监听 `127.0.0.1:8900`，首次运行可能下载模型。空闲模型卸载、串行推理和日志行为见[运维手册](docs/OPERATIONS.md)。OCR 只按低文本页策略处理候选页，不能保证恢复所有扫描、曲线化正文或图表内容。

## 6. 启动后的下一步

- 新增或更新手册：[索引维护](docs/OPERATIONS.md#1-状态与索引维护)。
- 迁移索引与配置：[数据包导入导出](docs/OPERATIONS.md#3-数据包迁移)。
- 查询或读页：[MCP/Agent 协议](docs/MCP-PROTOCOL.md) 与 [HTTP API](docs/HTTP-API.md)。
- 检索异常：[故障排查](docs/OPERATIONS.md#5-故障排查)。
