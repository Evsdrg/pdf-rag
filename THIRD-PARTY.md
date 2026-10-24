# 依赖许可清单与第三方声明

主许可证见 [README](README.md#许可证) 与 [LICENSE](LICENSE)。本文件是对当前锁定环境
（2026-10-24 复核）的许可记录与第三方版权声明。依赖版本变化后应重新核对，
不把包数量当成长期不变的承诺。

## 依赖许可清单

对已安装的 82 个包逐一核对 `dist-info`，强 copyleft 为 PyMuPDF；MPL 的文件级弱 copyleft 另列：

| 组件 | 许可证 | 对项目的影响 |
|---|---|---|
| **PyMuPDF 1.28** | **AGPL-3.0 / 商业双许可** | **决定整体许可证** |
| LanceDB 0.36 / PyArrow 25 | Apache-2.0 | 无 |
| FastAPI / Starlette / Uvicorn / FastMCP | MIT 或 BSD | 无 |
| Pydantic 2.x / MCP SDK / httpx / AnyIO | MIT / BSD-3 | 无 |
| numpy / pandas / zstandard / python-dotenv | BSD | 无 |
| certifi / tqdm | MPL-2.0（文件级弱 copyleft） | 无（未修改其源码） |
| **前端**：Vue 3 / Vue Router / naive-ui / Vite / vue-tsc | MIT | 无 |
| **前端**：TypeScript | Apache-2.0 | 无 |
| **OCR**：PaddleOCR | Apache-2.0 | 无（可选组件，独立进程） |
| 运行时：Python 3.13 / Node.js | PSF / MIT 类 | 无 |

> 清单可直接复现：
> `.venv/bin/python -c "import importlib.metadata as m; [print(d.metadata['Name'], d.version,
> d.metadata.get('License') or [c for c in (d.metadata.get_all('Classifier') or []) if 'License' in c])
> for d in m.distributions()]"`

## 第三方声明

- MuPDF / PyMuPDF 版权归 Artifex Software, Inc.，以 AGPL-3.0 使用。
- PaddleOCR 版权归 PaddlePaddle Authors，Apache-2.0。
- 其余依赖的版权与许可条款见各包内 `LICENSE` 文件。

本仓库**不包含**任何第三方手册 PDF 的再分发授权——`pdf/` 下的数据手册版权归各自厂商，
仅供本地检索使用；对外分发本仓库时请勿附带这些手册。
