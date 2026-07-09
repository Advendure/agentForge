# agentForge

一个功能完整的 AI Coding Agent 框架，包含工具分发、权限边界、hooks 扩展点、任务系统、技能加载、记忆管理、上下文压缩、错误恢复、后台任务、cron 调度、团队协作、worktree 隔离和 MCP 外部工具接入等核心功能。

## ✨ 功能特性

- **工具分发与权限**：内置 27+ 工具，支持权限拦截和安全边界
- **Hooks 扩展系统**：UserPromptSubmit、PreToolUse、PostToolUse、Stop 等扩展点
- **任务与计划**：todo 计划 + 跨会话任务图
- **子 Agent 与团队**：一次性 subagent + 持久队友线程
- **记忆与技能**：`.memory/MEMORY.md` + 技能目录按需加载
- **上下文压缩**：智能压缩管线，支持 reactive compact
- **错误恢复**：429/529 重试、max_tokens 升级、prompt too long 恢复
- **后台任务**：慢操作自动后台执行，不阻塞主循环
- **Cron 调度**：定时任务调度器
- **Worktree 隔离**：独立分支和目录隔离
- **MCP 插件**：支持官方 MCP SDK 连接外部工具

## 🚀 快速开始

### 环境要求

- Python 3.10+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

创建 `.env` 文件：

```env
ANTHROPIC_API_KEY=your-api-key
```

### 运行

```bash
python main.py
```

## 📁 项目结构

```
.
├── main.py              # 入口文件
├── requirements.txt     # 依赖列表
├── mcp_config.json      # MCP 服务器配置
├── src/                 # 核心模块
│   ├── agent_loop.py    # 主循环
│   ├── tool_defs.py     # 工具定义
│   ├── hooks.py         # Hooks 系统
│   ├── task_system.py   # 任务系统
│   ├── subagent.py      # 子 Agent
│   ├── teammate.py      # 队友系统
│   ├── skills.py        # 技能加载
│   ├── compaction.py    # 上下文压缩
│   ├── error_recovery.py# 错误恢复
│   ├── background.py    # 后台任务
│   ├── cron_scheduler.py# Cron 调度
│   ├── worktree.py      # Worktree 隔离
│   ├── mcp.py           # MCP 插件
│   └── tools/           # 内置工具
└── skills/              # 技能目录
    ├── agent-builder/   # Agent 构建技能
    ├── code-review/     # 代码审查技能
    ├── mcp-builder/     # MCP 构建技能
    └── pdf/             # PDF 处理技能
```

## 📝 示例

```bash
# 启动后可尝试：
python main.py

# 输入示例：
# Create a todo list for inspecting this repo, then list Python files
# Connect to the docs MCP server and search for agent loop
# Create two tasks, create worktrees for them, then spawn alice and bob
```

## 📄 许可证

MIT License
