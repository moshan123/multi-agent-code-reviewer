# Multi-Agent 代码审查助手

一个基于 MCP (Model Context Protocol) 的多 Agent 协作系统，用于自动化代码审查和质量管理。

## 功能特性

- 🤖 **多 Agent 协作**：Orchestrator 协调 Security、Quality、Documentation 三个专业 Agent
- 🔗 **MCP 集成**：通过 MCP 协议与 GitHub、LSP 等服务无缝集成
- 📊 **实时 Dashboard**：Next.js 构建的可视化界面，展示审查进度和结果
- 💬 **自然语言交互**：用自然语言指挥 Agent 团队完成审查任务

## 项目架构

```
┌─────────────────────────────────────────────────────────┐
│                   用户 (自然语言)                        │
│              "帮我审查这个 PR 的代码质量"                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Orchestrator Agent (协调器)                  │
│         分析请求，分发任务给专业 Agent                        │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Security     │ │ Quality      │ │ Documentation│
    │ Agent        │ │ Agent        │ │ Agent        │
    │ (安全检查)    │ │ (代码质量)    │ │ (文档检查)    │
    └──────────────┘ └──────────────┘ └──────────────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│              MCP Servers                                 │
│   • GitHub MCP (获取 PR 代码)                             │
│   • 自定义 MCP Server (业务逻辑)                           │
│   • jdtls-lsp (代码分析)                                 │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- GitHub Token (可选，用于审查私有仓库)

### 安装

```bash
# 克隆项目
cd multi-agent-code-reviewer

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Dashboard 依赖
cd dashboard
npm install
```

### 运行

#### 方式 1: 启动 Dashboard (推荐)

```bash
cd dashboard
npm run dev
# 访问 http://localhost:3000
```

#### 方式 2: 命令行审查

```bash
# 使用 Orchestrator 审查 PR
python agents/orchestrator.py --repo owner/repo --pr 123

# 单独运行 Security Agent
python agents/security_agent.py --code "your code here"

# 单独运行 Quality Agent
python agents/quality_agent.py --file path/to/file.py
```

### 测试

```bash
# 运行测试脚本
python test_agents.py
```

### 命令行审查

```bash
# 使用 Orchestrator 审查 PR
python agents/orchestrator.py --repo owner/repo --pr 123

# 单独运行 Security Agent
python agents/security_agent.py --code "your code here"

# 单独运行 Quality Agent
python agents/quality_agent.py --file path/to/file.py

# 单独运行 Documentation Agent
python agents/docs_agent.py --file path/to/file.py --description "PR 描述"
```

## Agents 详情

### 🔒 Security Agent
- 检测敏感信息泄露（密码、API 密钥等）
- SQL 注入风险检查
- XSS 漏洞检查
- 命令注入检查
- 路径遍历检查
- 弱加密算法检查

### 💎 Quality Agent
- 代码行长度检查
- 函数长度分析
- 循环复杂度计算
- TODO/FIXME 注释检测
- 调试代码检测
- 魔法数字检测

### 📖 Documentation Agent
- PR 描述完整性检查
- 函数/类文档字符串检查
- 注释质量分析
- 类型注解检查

## 技术栈

## 项目结构

```
multi-agent-code-reviewer/
├── mcp-servers/
│   ├── code-analyzer/          # 代码分析 MCP Server
│   └── github-integration/     # GitHub 集成 MCP Server
├── agents/
│   ├── orchestrator.py         # 协调器 Agent
│   ├── security_agent.py       # 安全检查 Agent
│   ├── quality_agent.py        # 代码质量 Agent
│   └── docs_agent.py           # 文档检查 Agent
├── dashboard/
│   ├── app/
│   │   ├── page.tsx            # 主页面
│   │   ├── api/                # API 路由
│   │   └── components/         # UI 组件
│   └── package.json
├── shared/
│   ├── mcp_config.py           # MCP 配置
│   └── utils.py
└── requirements.txt
```

## License

MIT
