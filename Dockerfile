# VibeDoc Agent应用 - Docker配置
# 为魔塔MCP&Agent挑战赛2025优化
FROM python:3.11-slim

# Agent应用标签
LABEL name="VibeDoc Agent Application"
LABEL description="智能Agent开发计划生成器 - MCP多服务协作"
LABEL version="1.0.0"
LABEL competition="魔塔MCP&Agent挑战赛2025"

# 设置工作目录
WORKDIR /app

# Agent应用环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV AGENT_APP_MODE=production
ENV MCP_SERVICES_ENABLED=true

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# 启动命令
CMD ["python", "app.py"]