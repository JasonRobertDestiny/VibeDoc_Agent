# 🚀 VibeDoc 部署指南

## 📋 目录
- [快速部署](#快速部署)
- [魔塔ModelScope部署](#魔塔modelscope部署)
- [Docker部署](#docker部署)
- [本地开发](#本地开发)
- [环境配置](#环境配置)
- [故障排除](#故障排除)

## 🚀 快速部署

### 方法1：魔塔ModelScope一键部署（推荐）

1. **登录魔塔ModelScope**
   - 访问 [ModelScope](https://modelscope.cn)
   - 注册并登录账户

2. **导入项目**
   ```
   仓库地址: https://github.com/JasonRobertDestiny/VibeDocs.git
   分支: modelscope
   SDK: Gradio
   ```

3. **配置环境变量**
   ```bash
   SILICONFLOW_API_KEY=your_api_key_here
   NODE_ENV=production
   PORT=3000
   ```

4. **启动部署**
   - 点击"启动"按钮
   - 等待构建完成

### 方法2：本地快速启动

```bash
# 克隆项目
git clone https://github.com/JasonRobertDestiny/VibeDocs.git
cd VibeDocs

# 切换到正确分支
git checkout modelscope

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥

# 启动应用
python app.py
```

## 🌟 魔塔ModelScope部署

### 完整部署配置

**项目信息：**
- **仓库地址：** `https://github.com/JasonRobertDestiny/VibeDocs.git`
- **分支：** `modelscope`
- **SDK：** `Gradio`
- **Python版本：** `3.11`

**环境变量配置：**

| 变量名 | 值 | 说明 | 必填 |
|--------|----|----|------|
| `SILICONFLOW_API_KEY` | `your_api_key` | Silicon Flow API密钥 | ✅ |
| `NODE_ENV` | `production` | 运行环境 | ✅ |
| `PORT` | `3000` | 应用端口 | ✅ |
| `DEEPWIKI_SSE_URL` | `http://localhost:8080` | DeepWiki MCP服务 | ❌ |
| `FETCH_SSE_URL` | `http://localhost:8081` | 通用抓取MCP服务 | ❌ |
| `DOUBAO_SSE_URL` | `http://localhost:8082` | 图像生成MCP服务 | ❌ |
| `DOUBAO_API_KEY` | `your_doubao_key` | Doubao API密钥 | ❌ |

### 部署步骤详解

1. **准备API密钥**
   - 访问 [Silicon Flow](https://siliconflow.cn) 注册账户
   - 获取免费API密钥

2. **创建创空间**
   - 在ModelScope中创建新的创空间
   - 选择"从Git仓库导入"

3. **配置项目设置**
   ```yaml
   title: "VibeDoc AI Agent - Agent应用开发赛道"
   emoji: "🤖"
   sdk: gradio
   sdk_version: 5.34.1
   app_file: app.py
   ```

4. **设置环境变量**
   - 在创空间设置中添加环境变量
   - 确保 `SILICONFLOW_API_KEY` 正确配置

5. **构建和部署**
   - 点击"构建"按钮
   - 等待构建完成
   - 测试应用功能

### 常见问题解决

**问题1：构建失败**
- 确保使用 `modelscope` 分支
- 检查 `requirements.txt` 文件是否存在
- 验证Python版本兼容性

**问题2：API调用失败**
- 检查 `SILICONFLOW_API_KEY` 是否正确
- 验证API密钥是否有效
- 确认网络连接正常

**问题3：MCP服务不可用**
- MCP服务是可选的，不影响核心功能
- 如果不使用外部链接解析，可以忽略相关错误

## 🐳 Docker部署

### 使用Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/JasonRobertDestiny/VibeDocs.git
cd VibeDocs

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f vibedoc
```

### 使用Docker直接构建

```bash
# 构建镜像
docker build -t vibedoc .

# 运行容器
docker run -d \
  --name vibedoc \
  -p 3000:3000 \
  -e SILICONFLOW_API_KEY=your_api_key \
  -e NODE_ENV=production \
  vibedoc
```

## 💻 本地开发

### 环境要求
- Python 3.11+
- pip 或 pipenv
- Git

### 开发环境设置

```bash
# 1. 克隆项目
git clone https://github.com/JasonRobertDestiny/VibeDocs.git
cd VibeDocs

# 2. 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加必要的配置

# 5. 启动开发服务器
python app.py
```

### 开发工具推荐

- **IDE：** VS Code, PyCharm
- **Python插件：** Python Extension Pack
- **代码格式化：** Black, isort
- **类型检查：** mypy
- **测试框架：** pytest

## ⚙️ 环境配置

### 必填配置

```bash
# Silicon Flow API密钥（必填）
SILICONFLOW_API_KEY=your_siliconflow_api_key

# 应用配置
NODE_ENV=production
PORT=3000
```

### 可选配置

```bash
# MCP服务配置（可选）
DEEPWIKI_SSE_URL=http://localhost:8080
FETCH_SSE_URL=http://localhost:8081
DOUBAO_SSE_URL=http://localhost:8082
DOUBAO_API_KEY=your_doubao_api_key

# 调试配置
DEBUG=false
LOG_LEVEL=INFO
API_TIMEOUT=120
MCP_TIMEOUT=30
```

### 配置文件说明

- `.env.example`: 环境变量模板
- `app_config.yaml`: 魔塔部署配置
- `requirements.txt`: Python依赖
- `Dockerfile`: Docker镜像配置
- `docker-compose.yml`: 容器编排配置

## 🛠️ 故障排除

### 常见错误及解决方案

**错误1：`ModuleNotFoundError`**
```bash
# 解决方案：重新安装依赖
pip install -r requirements.txt
```

**错误2：API密钥错误**
```bash
# 检查环境变量
echo $SILICONFLOW_API_KEY

# 验证密钥格式
# 应该以 "sk-" 开头
```

**错误3：端口占用**
```bash
# 查找占用端口的进程
lsof -i :3000

# 杀死进程
kill -9 <PID>

# 或者更改端口
export PORT=3001
```

**错误4：网络连接问题**
```bash
# 测试网络连接
curl -I https://api.siliconflow.cn/v1/chat/completions

# 检查防火墙设置
# 确保端口3000可以访问
```

### 日志调试

```bash
# 查看应用日志
tail -f /var/log/vibedoc.log

# Docker日志
docker logs vibedoc

# 实时日志
docker logs -f vibedoc
```

### 性能优化

1. **内存优化**
   - 增加容器内存限制
   - 使用更高效的Python版本

2. **网络优化**
   - 配置CDN加速
   - 使用负载均衡

3. **缓存优化**
   - 启用Redis缓存
   - 配置HTTP缓存头

## 📞 技术支持

如果遇到问题，请：

1. 检查本文档的故障排除部分
2. 查看项目Issues页面
3. 提交新的Issue并提供：
   - 错误信息
   - 系统环境
   - 配置信息
   - 复现步骤

## 🔄 更新升级

```bash
# 拉取最新代码
git pull origin modelscope

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启应用
docker-compose restart vibedoc
```

---

**🎯 提示：** 建议优先使用魔塔ModelScope部署，这是最简单且稳定的方式。本地开发时使用Docker可以确保环境一致性。