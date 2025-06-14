# MCP Feedback Enhanced（交互反馈 MCP）

**🌐 语言切换 / Language:** [English](README.md) | [繁體中文](README.zh-TW.md) | **简体中文**

**原作者：** [Fábio Ferreira](https://x.com/fabiomlferreira) | [原始项目](https://github.com/noopstudios/interactive-feedback-mcp) ⭐
**分支版本：** [Minidoracat](https://github.com/Minidoracat)
**UI 设计参考：** [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

## 🎯 核心概念

这是一个 [MCP 服务器](https://modelcontextprotocol.io/)，建立**反馈导向的开发工作流程**，采用**纯 Web UI 架构**，完美适配本地、**SSH Remote 环境**（Cursor SSH Remote、VS Code Remote SSH）与 **WSL (Windows Subsystem for Linux) 环境**。通过引导 AI 与用户确认而非进行推测性操作，可将多次工具调用合并为单次反馈导向请求，大幅节省平台成本并提升开发效率。

**🌐 Web-Only 架构优势：**
- 🚀 **简化部署**：无需 GUI 依赖，安装更轻量
- 🌍 **跨平台兼容**：支持所有操作系统和环境
- 🔧 **维护简单**：统一的 Web 界面，降低复杂度
- 📦 **体积精简**：移除重型 GUI 库，安装包大幅缩小

**🔮 未来计划：** 我们计划在功能稳定后重新引入桌面版应用程序，目前专注于 Web UI 功能的完善和优化。

**支持平台：** [Cursor](https://www.cursor.com) | [Cline](https://cline.bot) | [Windsurf](https://windsurf.com) | [Augment](https://www.augmentcode.com) | [Trae](https://www.trae.ai)

### 🔄 工作流程
1. **AI 调用** → `mcp-feedback-enhanced` 工具
2. **Web UI 启动** → 自动打开浏览器界面（纯 Web 架构）
3. **智能交互** → 提示词选择、文字输入、图片上传、自动提交
4. **即时反馈** → WebSocket 连接即时传递信息给 AI
5. **会话追踪** → 自动记录会话历史与统计
6. **流程继续** → AI 根据反馈调整行为或结束任务

## 🌟 主要功能

### 🌐 纯 Web UI 架构系统
- **Web-Only 设计**：完全移除桌面 GUI 依赖，采用纯 Web 界面
- **通用兼容性**：支持本地、SSH Remote 和 WSL 环境
- **自动适配**：智能环境检测与最佳配置
- **轻量部署**：无需复杂的 GUI 环境配置

### 📝 智能提示词管理系统（v2.4.0 新功能）
- **CRUD 操作**：新增、编辑、删除、使用常用提示词
- **使用统计**：追踪使用频率并智能排序
- **快速应用**：一键选择和应用提示词
- **自动提交整合**：支持自动提交标记和优先显示

### ⏰ 自动定时提交功能（v2.4.0 新功能）
- **弹性计时**：可设定 1-86400 秒的倒数计时器
- **视觉化显示**：即时倒数显示和状态指示
- **深度整合**：与提示词管理系统无缝配合
- **完整控制**：支持暂停、恢复、取消操作

### 📊 会话管理与追踪（v2.4.3 重构增强）
- **独立页签设计**：从左侧边栏迁移到专属页签，解决浏览器兼容性问题
- **本地历史保存**：支持会话记录本地保存，可设定保存期限
- **隐私控制**：用户消息记录支持三种隐私等级设定
- **数据管理**：支持会话历史导出和清理功能
- **实时统计**：今日会话数量和平均时长统计

### 🔗 连接监控系统（v2.4.0 新功能）
- **即时监控**：WebSocket 连接状态即时监控
- **品质指示**：延迟测量和连接品质指示
- **自动重连**：智能重连机制和错误处理
- **详细统计**：完整的连接统计信息

### 🔊 音效通知系统（v2.4.3 新功能）
- **智能提醒**：会话更新时自动播放音效通知
- **多种音效**：内建经典提示音、通知铃声、轻柔钟声
- **自定义音效**：支持上传 MP3、WAV、OGG 格式的自定义音效
- **完整控制**：音量调节、测试播放、音效管理功能

### 🎨 现代化界面设计
- **模块化架构**：JavaScript 完全模块化重构
- **响应式设计**：适配不同屏幕尺寸和窗口大小
- **统一风格**：一致的设计语言和视觉体验
- **智能布局**：AI 摘要区域自动扩展，提交按钮位置优化

### 🖼️ 图片支持
- **格式支持**：PNG、JPG、JPEG、GIF、BMP、WebP
- **上传方式**：拖拽文件 + 剪贴板粘贴（Ctrl+V）
- **无限制上传**：支持任意大小的图片文件，自动智能处理

### 💾 智能记忆功能（v2.4.3 新功能）
- **输入框高度记忆**：自动保存和恢复文字输入框的高度设定
- **一键复制**：项目路径和会话ID支持点击复制到剪贴板
- **设定持久化**：所有用户偏好设定自动保存

### 🌏 多语言
- **三语支持**：简体中文、英文、繁体中文
- **智能检测**：根据系统语言自动选择
- **即时切换**：界面内可直接切换语言
- **完整国际化**：包含 tooltip 和按钮提示的多语言支持

### ✨ WSL 环境支持（v2.2.5）
- **自动检测**：智能识别 WSL (Windows Subsystem for Linux) 环境
- **浏览器整合**：WSL 环境下自动启动 Windows 浏览器
- **多种启动方式**：支持 `cmd.exe`、`powershell.exe`、`wslview` 等多种浏览器启动方法
- **无缝体验**：WSL 用户可直接使用 Web UI，无需额外配置

### 🌐 SSH Remote 环境支持（v2.3.0 新功能）
- **智能检测**：自动识别 SSH Remote 环境（Cursor SSH Remote、VS Code Remote SSH 等）
- **浏览器启动指引**：当无法自动启动浏览器时，提供清晰的解决方案
- **端口转发支持**：完整的端口转发设置指引和故障排除
- **MCP 整合优化**：改善与 MCP 系统的整合，提供更稳定的连接体验
- **详细文档**：[SSH Remote 环境使用指南](docs/zh-CN/ssh-remote/browser-launch-issues.md)

## 🌐 界面预览

### Web UI 界面（v2.4.0 - Web-Only 架构）

<div align="center">
  <img src="docs/zh-CN/images/web1.jpeg" width="400" alt="Web UI 主界面 - 提示词管理与自动提交" />
</div>

<details>
<summary>📱 点击查看完整界面截图</summary>

<div align="center">
  <img src="docs/zh-CN/images/web2.jpeg" width="800" alt="Web UI 完整界面 - 会话管理与设置" />
</div>

</details>

*Web UI 界面 - 纯 Web 架构，支持提示词管理、自动提交、会话追踪等智能功能*

**快捷键支持**
- `Ctrl+Enter`（Windows/Linux）/ `Cmd+Enter`（macOS）：提交反馈（主键盘与数字键盘皆支持）
- `Ctrl+V`（Windows/Linux）/ `Cmd+V`（macOS）：直接粘贴剪贴板图片
- `Ctrl+I`（Windows/Linux）/ `Cmd+I`（macOS）：快速聚焦输入框 (感谢 @penn201500)

## 🚀 快速开始

### 1. 安装与测试
```bash
# 安装 uv（如果尚未安装）
pip install uv

# 快速测试
uvx mcp-feedback-enhanced@latest test
```

### 2. 配置 MCP
**基本配置**（适合大多数用户）：
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

**进阶配置**（需要自定义环境）：
```json
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "env": {
        "MCP_DEBUG": "false",
        "MCP_WEB_PORT": "8765"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

### 3. 设定提示工程
为了获得最佳效果，请在 AI 助手中添加以下规则：

```
# MCP Interactive Feedback 规则

1. 在任何流程、任务、对话进行时，无论是询问、回复、或完成阶段性任务，皆必须调用 MCP mcp-feedback-enhanced。
2. 每当收到用户反馈，若反馈内容非空，必须再次调用 MCP mcp-feedback-enhanced，并根据反馈内容调整行为。
3. 仅当用户明确表示「结束」或「不再需要交互」时，才可停止调用 MCP mcp-feedback-enhanced，流程才算结束。
4. 除非收到结束指令，否则所有步骤都必须重复调用 MCP mcp-feedback-enhanced。
5. 完成任务前，必须使用 MCP mcp-feedback-enhanced 工具向用户询问反馈。
```

## ⚙️ 进阶设定

### 环境变量
| 变量 | 用途 | 值 | 默认 |
|------|------|-----|------|
| `MCP_DEBUG` | 调试模式 | `true`/`false` | `false` |
| `MCP_WEB_PORT` | Web UI 端口 | `1024-65535` | `8765` |

### 测试选项
```bash
# 版本查询
uvx mcp-feedback-enhanced@latest version       # 检查版本

# 界面测试
uvx mcp-feedback-enhanced@latest test --web    # 测试 Web UI (自动持续运行)

# 调试模式
MCP_DEBUG=true uvx mcp-feedback-enhanced@latest test
```

### 开发者安装
```bash
git clone https://github.com/Minidoracat/mcp-feedback-enhanced.git
cd mcp-feedback-enhanced
uv sync
```

**本地测试方式**
```bash
# 功能测试
uv run python -m mcp_feedback_enhanced test              # 标准功能测试
uvx --with-editable . mcp-feedback-enhanced test --web   # Web UI 测试 (持续运行)

# 单元测试
make test                                                # 运行所有单元测试
make test-fast                                          # 快速测试 (跳过慢速测试)
make test-cov                                           # 测试并生成覆盖率报告

# 代码质量检查
make check                                              # 完整代码质量检查
make quick-check                                        # 快速检查并自动修复
```

**测试说明**
- **功能测试**：测试 MCP 工具的完整功能流程
- **单元测试**：测试各个模块的独立功能
- **覆盖率测试**：生成 HTML 覆盖率报告到 `htmlcov/` 目录
- **质量检查**：包含 linting、格式化、类型检查

## 🆕 版本更新记录

📋 **完整版本更新记录：** [RELEASE_NOTES/CHANGELOG.zh-CN.md](RELEASE_NOTES/CHANGELOG.zh-CN.md)

### 最新版本亮点（v2.4.3）
- 📋 **会话管理重构**: 从左侧边栏迁移到独立页签，解决浏览器兼容性问题
- 🔊 **音效通知系统**: 会话更新音效提醒，支持内建和自定义音效
- 📚 **会话历史增强**: 本地保存、隐私控制、导出清理功能
- 💾 **智能记忆功能**: 输入框高度记忆、一键复制等便利功能
- 🎨 **界面布局优化**: AI 摘要自动扩展、按钮位置调整、简化设计
- 🌐 **多语言完善**: tooltip 和按钮提示的完整国际化支持
- 🐛 **问题修复**: 修复会话详情按钮、弹窗关闭延迟等用户体验问题

## 🐛 常见问题

### 🌐 SSH Remote 环境问题
**Q: SSH Remote 环境下浏览器无法启动**
A: 这是正常现象。SSH Remote 环境没有图形界面，需要手动在本地浏览器打开。详细解决方案请参考：[SSH Remote 环境使用指南](docs/zh-CN/ssh-remote/browser-launch-issues.md)

**Q: 为什么没有接收到 MCP 新的反馈？**
A: 可能是 WebSocket 连接问题。**解决方法**：直接重新刷新浏览器页面。

**Q: 为什么没有调用出 MCP？**
A: 请确认 MCP 工具状态为绿灯。**解决方法**：反复开关 MCP 工具，等待几秒让系统重新连接。

**Q: Augment 无法启动 MCP**
A: **解决方法**：完全关闭并重新启动 VS Code 或 Cursor，重新打开项目。

### 🔧 一般问题
**Q: 如何使用旧版 GUI 界面？**
A: v2.4.0 版本已完全移除 PyQt6 GUI 依赖，转为纯 Web UI 架构。如需使用旧版 GUI，请指定 v2.3.0 或更早版本：
```bash
# 使用 v2.3.0（最后支持 GUI 的版本）
uvx mcp-feedback-enhanced@2.3.0

# 或在 MCP 配置中指定版本
{
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@2.3.0"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```
**注意**：旧版本不包含 v2.4.0 的新功能（提示词管理、自动提交、会话管理等）。

**Q: 出现 "Unexpected token 'D'" 错误**
A: 调试输出干扰。设置 `MCP_DEBUG=false` 或移除该环境变量。

**Q: 中文字符乱码**
A: 已在 v2.0.3 修复。更新到最新版本：`uvx mcp-feedback-enhanced@latest`

**Q: 多屏幕环境下窗口消失或定位错误**
A: 已在 v2.1.1 修复。进入「⚙️ 设置」标签页，勾选「总是在主屏幕中心显示窗口」即可解决。特别适用于 T 字型屏幕排列等复杂多屏幕配置。

**Q: 图片上传失败**
A: 检查文件格式（PNG/JPG/JPEG/GIF/BMP/WebP）。系统支持任意大小的图片文件。

**Q: Web UI 无法启动**
A: 检查防火墙设置或尝试使用不同的端口。

**Q: UV Cache 占用过多磁盘空间**
A: 由于频繁使用 `uvx` 命令，cache 可能会累积到数十 GB。建议定期清理：
```bash
# 查看 cache 大小和详细信息
python scripts/cleanup_cache.py --size

# 预览清理内容（不实际清理）
python scripts/cleanup_cache.py --dry-run

# 执行标准清理
python scripts/cleanup_cache.py --clean

# 强制清理（会尝试关闭相关程序，解决 Windows 文件占用问题）
python scripts/cleanup_cache.py --force

# 或直接使用 uv 命令
uv cache clean
```
详细说明请参考：[Cache 管理指南](docs/zh-CN/cache-management.md)

**Q: AI 模型无法解析图片**
A: 各种 AI 模型（包括 Gemini Pro 2.5、Claude 等）在图片解析上可能存在不稳定性，表现为有时能正确识别、有时无法解析上传的图片内容。这是 AI 视觉理解技术的已知限制。建议：
1. 确保图片质量良好（高对比度、清晰文字）
2. 多尝试几次上传，通常重试可以成功
3. 如持续无法解析，可尝试调整图片大小或格式

## 🙏 致谢

### 🌟 支持原作者
**Fábio Ferreira** - [X @fabiomlferreira](https://x.com/fabiomlferreira)
**原始项目：** [noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)

如果您觉得有用，请：
- ⭐ [为原项目按星星](https://github.com/noopstudios/interactive-feedback-mcp)
- 📱 [关注原作者](https://x.com/fabiomlferreira)

### 设计灵感
**sanshao85** - [mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

### 贡献者
**penn201500** - [GitHub @penn201500](https://github.com/penn201500)
- 🎯 自动聚焦输入框功能 ([PR #39](https://github.com/Minidoracat/mcp-feedback-enhanced/pull/39))

### 社群支援
- **Discord：** [https://discord.gg/Gur2V67](https://discord.gg/Gur2V67)
- **Issues：** [GitHub Issues](https://github.com/Minidoracat/mcp-feedback-enhanced/issues)

## 📄 授权

MIT 授权条款 - 详见 [LICENSE](LICENSE) 档案

---
**🌟 欢迎 Star 并分享给更多开发者！**
