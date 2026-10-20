# pdf-rag 后端(含 Web UI) + MCP 服务共用镜像。
# pdf/ parsed/ index.lance/ 三份(共约 620MB)不进镜像 —— 由 compose bind mount
# 提供,镜像只含代码与依赖(~400MB),升级代码不必动数据。
FROM python:3.13-slim

# 中文路径/文件名必需:slim 默认 POSIX locale 会让文件系统编码退化为 ASCII
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=https://mirrors.cernet.edu.cn/pypi/web/simple

WORKDIR /app

# 依赖层:先只拷贝清单以利用层缓存;uv 版本与仓库 uv.lock 的生成版本一致
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv==0.12.17 \
    && uv sync --frozen --no-install-project

# 代码层
COPY backend/ backend/
COPY web/dist/ web/dist/
COPY server.py run_backend.py ./

# run_backend.py 要在工作目录创建守护锁(run_backend.lock);容器以 uid 1000 运行,
# /app 属主是 root,放开写权限
RUN chmod 0777 /app

ENV PATH="/app/.venv/bin:$PATH"

# 默认跑后端守护(compose 里 mcp 服务以同镜像改 command 覆盖)
CMD ["python", "run_backend.py"]
