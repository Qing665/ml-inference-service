# ==================== 定义构建参数 ====================
# 默认留空，使用 Docker Hub；需要阿里云时传入 "crpi-8vw2fragz599b40r.cn-hangzhou.personal.cr.aliyuncs.com/hhq-docker/"
ARG BASE_REGISTRY=""

# ==================== 第一阶段：构建阶段 ====================
FROM ${BASE_REGISTRY}python:3.9-slim AS builder

WORKDIR /app

# 更换为清华源（加速 apt-get）
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# 安装构建所需工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件，创建虚拟环境并安装依赖
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# ==================== 第二阶段：运行阶段 ====================
FROM ${BASE_REGISTRY}python:3.9-slim AS runtime

WORKDIR /app

# 更换为清华源（加速 apt-get）
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# 只复制运行时必要的系统库（xgboost 需要 libgomp）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ⭐ 先创建用户（必须在 COPY --chown 之前）
RUN useradd -m -u 1000 appuser

# ⭐ 复制虚拟环境，同时直接设置所有权（不会产生额外层）
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# 设置环境变量
ENV PATH="/opt/venv/bin:$PATH"

# ⭐ 复制应用代码和模型，同时设置所有权
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser model/ ./model/

# 切换到非 root 用户
USER appuser

WORKDIR /app/app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info"]