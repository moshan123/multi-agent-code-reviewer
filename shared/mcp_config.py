"""
共享配置模块
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class MCPConfig:
    """MCP 配置"""

    # GitHub 配置
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_API: str = "https://api.github.com"

    # MCP Server 配置
    MCP_SERVERS: dict = {
        "code-analyzer": {
            "command": "python",
            "args": ["-m", "mcp_servers.code_analyzer.server"],
            "cwd": str(Path(__file__).parent.parent)
        },
        "github-integration": {
            "command": "python",
            "args": ["-m", "mcp_servers.github_integration.server"],
            "cwd": str(Path(__file__).parent.parent)
        }
    }

    # Agent 配置
    AGENT_CONFIG: dict = {
        "orchestrator": {
            "model": "claude-sonnet-4-6",
            "temperature": 0.3,
            "max_tokens": 4096
        },
        "security": {
            "model": "claude-sonnet-4-6",
            "temperature": 0.1,
            "max_tokens": 4096
        },
        "quality": {
            "model": "claude-sonnet-4-6",
            "temperature": 0.2,
            "max_tokens": 4096
        },
        "documentation": {
            "model": "claude-sonnet-4-6",
            "temperature": 0.3,
            "max_tokens": 4096
        }
    }

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN 环境变量未设置")
        return True

    @classmethod
    def get_anthropic_key(cls) -> str:
        """获取 Anthropic API Key"""
        return os.getenv("ANTHROPIC_API_KEY", "")


# 工具函数
def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent


def get_mcp_server_path(server_name: str) -> Path:
    """获取 MCP Server 路径"""
    return get_project_root() / "mcp-servers" / server_name
