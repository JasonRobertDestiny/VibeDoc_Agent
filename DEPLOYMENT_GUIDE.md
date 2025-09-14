# 🚀 VibeDoc ModelScope 部署指南

## 📋 部署准备清单

### ✅ 文件检查
确保以下文件已准备完成：
- `app.py` - 主应用程序
- `requirements.txt` - 依赖清单
- `README.md` - 项目说明（包含ModelScope前言）
- `config.py` - 配置管理
- `mcp_manager.py` - MCP服务管理
- `prompt_optimizer.py` - 提示词优化器
- `explanation_manager.py` - AI可解释性组件
- `streaming_manager.py` - 流式响应管理

### ✅ 环境变量准备
必需的环境变量：
- `SILICONFLOW_API_KEY` - Silicon Flow API密钥（必填）
- `PORT` - 应用端口（默认3000）

可选的MCP服务变量：
- `DEEPWIKI_SSE_URL` - DeepWiki MCP服务URL
- `FETCH_SSE_URL` - Fetch MCP服务URL

## 🏗️ ModelScope部署步骤

### 第1步：创建新的创空间

1. 访问 [ModelScope创空间](https://www.modelscope.cn/studios)
2. 点击"创建新的创空间"
3. 填写基本信息：
   - **空间名称**: `Vibedocs`
   - **空间标识**: `your-username/Vibedocs`
   - **可见性**: 公开
   - **SDK**: Gradio
   - **硬件**: CPU Basic (免费)

### 第2步：上传项目文件

方式1：Git仓库关联
```bash
# 如果有GitHub仓库
git clone https://github.com/your-username/Vibedocs.git
cd Vibedocs
git push origin main
```

方式2：文件上传
1. 在创空间界面点击"文件"
2. 逐一上传所有Python文件
3. 确保文件结构正确

### 第3步：配置环境变量

1. 在创空间设置中选择"环境变量"
2. 添加必需的环境变量：

```env
# 必填项
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
PORT=3000

# 可选项（如果有MCP服务）
DEEPWIKI_SSE_URL=your_deepwiki_service_url
FETCH_SSE_URL=your_fetch_service_url  
DOUBAO_SSE_URL=your_doubao_service_url
DOUBAO_API_KEY=your_doubao_api_key
```

### 第4步：部署配置

确保`README.md`文件顶部包含正确的配置：

```yaml
---
title: VibeDoc - AI驱动的开发计划生成器
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.34.1
app_file: app.py
pinned: true
license: mit
---
```

### 第5步：启动部署

1. 点击"部署"按钮
2. 系统会自动安装依赖并启动应用
3. 等待部署完成（通常需要2-5分钟）

## 🔧 常见问题排查

### Q1: 部署失败，提示依赖安装错误
**解决方案**：
1. 检查`requirements.txt`格式是否正确
2. 确保所有依赖版本兼容
3. 查看部署日志了解具体错误

### Q2: 应用启动后显示配置错误
**解决方案**：
1. 检查环境变量是否正确设置
2. 确认`SILICONFLOW_API_KEY`已配置
3. 检查API密钥是否有效

### Q3: MCP服务连接失败
**解决方案**：
1. 检查MCP服务URL是否可访问
2. 确认API密钥配置正确
3. 查看应用日志定位问题

### Q4: 页面加载缓慢
**解决方案**：
1. 检查网络连接
2. 尝试刷新页面
3. 查看是否有资源加载问题

## 🎯 部署后验证

### 功能测试清单

1. **基础功能**：
   - [ ] 页面正常加载
   - [ ] 输入框可正常使用
   - [ ] 示例按钮工作正常

2. **AI生成功能**：
   - [ ] 创意输入验证
   - [ ] AI优化功能
   - [ ] 开发计划生成
   - [ ] 编程提示词生成

3. **交互功能**：
   - [ ] 复制按钮工作
   - [ ] 编辑提示词功能
   - [ ] 下载功能
   - [ ] 处理过程查看

4. **MCP服务**：
   - [ ] 参考链接处理
   - [ ] 外部知识获取
   - [ ] 服务状态监控

## 📊 性能优化建议

### 1. 减少启动时间
- 优化导入语句
- 减少不必要的初始化操作
- 使用懒加载机制

### 2. 提升响应速度
- 启用缓存机制
- 优化API调用
- 减少不必要的计算

### 3. 资源管理
- 监控内存使用
- 优化文件I/O操作
- 管理临时文件

## 🔐 安全注意事项

1. **API密钥管理**：
   - 不要在代码中硬编码API密钥
   - 使用环境变量存储敏感信息
   - 定期更换API密钥

2. **输入验证**：
   - 验证用户输入格式
   - 防止恶意输入
   - 限制输入长度

3. **错误处理**：
   - 不要暴露内部错误信息
   - 提供友好的错误提示
   - 记录错误日志便于排查

## 📈 监控和维护

### 日志监控
```python
# 应用已配置日志系统
import logging
logger = logging.getLogger(__name__)

# 查看应用日志
logger.info("应用启动成功")
logger.error("错误信息")
```

### 性能监控
- 监控响应时间
- 追踪错误率
- 观察资源使用情况

### 定期维护
- 更新依赖版本
- 优化代码性能
- 备份重要数据

## 🎉 部署成功！

部署完成后，您的VibeDoc应用将在以下地址可用：
`https://www.modelscope.cn/studios/your-username/Vibedocs`

### 下一步建议：
1. 分享您的创空间链接
2. 收集用户反馈
3. 持续优化功能
4. 参加魔塔MCP&Agent挑战赛

---

**技术支持**：
- 如遇问题，请查看ModelScope文档
- 或提交Issue到项目仓库
- 联系开发者获取帮助

**祝您部署成功！🚀**