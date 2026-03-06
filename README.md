# mcp-interactive

[English](README.en.md) | **简体中文**

MCP 服务器，用于在 AI 辅助开发过程中收集用户的交互式反馈。通过引导 AI 与用户确认而非自行猜测，减少不必要的工具调用，降低平台成本，提高开发效率。

<div align="center">
  <img src="docs/preview.png" width="800" alt="mcp-interactive Web UI" />
</div>

## 工作流程

1. AI 调用 `interactive_feedback` 工具
2. 自动打开浏览器界面（Web UI）
3. 用户输入反馈文本、上传截图、选择常用提示词
4. 通过 WebSocket 实时传递给 AI
5. AI 根据反馈调整行为或结束任务

## 安装

```bash
pip install uv
```

## 配置

将以下内容添加到 MCP 配置文件：

```json
{
  "mcpServers": {
    "mcp-interactive": {
      "command": "uvx",
      "args": ["mcp-interactive@latest"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

支持的 AI 平台：[Cursor](https://www.cursor.com) | [Cline](https://cline.bot) | [Windsurf](https://windsurf.com) | [Augment](https://www.augmentcode.com) | [Trae](https://www.trae.ai)

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MCP_WEB_HOST` | Web UI 监听地址 | `127.0.0.1` |
| `MCP_WEB_PORT` | Web UI 端口 | `8765` |
| `MCP_LANGUAGE` | 界面语言 (`zh-CN` / `en`) | 自动检测 |
| `MCP_DEBUG` | 调试模式 | `false` |

SSH 远程开发时，将 `MCP_WEB_HOST` 设为 `0.0.0.0` 以允许远程访问，或使用 SSH 端口转发。

## 功能

- **提示词管理** - 常用提示词的增删改查和智能排序
- **自动定时提交** - 1-86400 秒可配置定时器，支持暂停/恢复
- **图片上传** - 拖放、粘贴，支持 PNG/JPG/GIF/BMP/WebP
- **音频通知** - 内置音效、自定义上传、音量控制
- **多语言** - 简体中文、English，即时切换
- **WebSocket 实时通信** - 状态监控、自动重连

## 开发

```bash
git clone https://github.com/RealAlexandreAI/mcp-interactive.git
cd mcp-interactive
uv sync

# 测试
make test          # 单元测试
make test-web      # Web UI 测试

# 代码检查
make check         # 完整检查（lint + format + type）
```

## 致谢

- 原始项目：[noopstudios/interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp) by [Fabio Ferreira](https://x.com/fabiomlferreira)
- 上游 fork：[Minidoracat/mcp-feedback-enhanced](https://github.com/Minidoracat/mcp-feedback-enhanced)

## License

MIT
