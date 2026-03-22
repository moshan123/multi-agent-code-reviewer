"""
GitHub 集成 MCP Server - 提供 GitHub PR 相关工具
"""
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os

mcp = FastMCP("github-integration")

# GitHub 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API = "https://api.github.com"


class PRFile(BaseModel):
    """PR 文件变更"""
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None


class PRInfo(BaseModel):
    """PR 信息"""
    number: int
    title: str
    description: str
    author: str
    files: List[PRFile]


def get_headers() -> dict:
    """获取请求头"""
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "multi-agent-code-reviewer"
    }


@mcp.tool()
async def get_pr_info(repo: str, pr_number: int) -> dict:
    """
    获取 PR 基本信息

    Args:
        repo: 仓库全名 (owner/repo)
        pr_number: PR 编号

    Returns:
        PR 信息
    """
    async with httpx.AsyncClient() as client:
        # 获取 PR 详情
        pr_response = await client.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers=get_headers()
        )
        pr_response.raise_for_status()
        pr_data = pr_response.json()

        # 获取 PR 文件变更
        files_response = await client.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/files",
            headers=get_headers()
        )
        files_response.raise_for_status()
        files_data = files_response.json()

        files = [
            PRFile(
                filename=f["filename"],
                status=f["status"],
                additions=f["additions"],
                deletions=f["deletions"],
                changes=f["changes"],
                patch=f.get("patch")
            )
            for f in files_data
        ]

        return {
            "number": pr_data["number"],
            "title": pr_data["title"],
            "description": pr_data.get("body", ""),
            "author": pr_data["user"]["login"],
            "state": pr_data["state"],
            "created_at": pr_data["created_at"],
            "updated_at": pr_data["updated_at"],
            "files": [f.model_dump() for f in files],
            "base_branch": pr_data["base"]["ref"],
            "head_branch": pr_data["head"]["ref"]
        }


@mcp.tool()
async def get_pr_diff(repo: str, pr_number: int) -> str:
    """
    获取 PR 完整 diff

    Args:
        repo: 仓库全名
        pr_number: PR 编号

    Returns:
        完整 diff 内容
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
            headers={
                **get_headers(),
                "Accept": "application/vnd.github.v3.diff"
            }
        )
        response.raise_for_status()
        return response.text


@mcp.tool()
async def get_pr_files(repo: str, pr_number: int) -> List[dict]:
    """
    获取 PR 变更文件列表

    Args:
        repo: 仓库全名
        pr_number: PR 编号

    Returns:
        文件列表
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/files",
            headers=get_headers()
        )
        response.raise_for_status()
        files = response.json()

        return [
            {
                "filename": f["filename"],
                "status": f["status"],
                "additions": f["additions"],
                "deletions": f["deletions"],
                "changes": f["changes"]
            }
            for f in files
        ]


@mcp.tool()
async def create_pr_comment(repo: str, pr_number: int, body: str) -> dict:
    """
    创建 PR 评论

    Args:
        repo: 仓库全名
        pr_number: PR 编号
        body: 评论内容

    Returns:
        创建的评论信息
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments",
            headers=get_headers(),
            json={"body": body}
        )
        response.raise_for_status()
        data = response.json()
        return {
            "id": data["id"],
            "url": data["html_url"],
            "created_at": data["created_at"]
        }


@mcp.tool()
async def create_review_comment(
    repo: str,
    pr_number: int,
    commit_id: str,
    path: str,
    line: int,
    body: str
) -> dict:
    """
    创建代码审查评论

    Args:
        repo: 仓库全名
        pr_number: PR 编号
        commit_id: commit ID
        path: 文件路径
        line: 行号
        body: 评论内容

    Returns:
        创建的评论信息
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/comments",
            headers=get_headers(),
            json={
                "body": body,
                "commit_id": commit_id,
                "path": path,
                "line": line
            }
        )
        response.raise_for_status()
        data = response.json()
        return {
            "id": data["id"],
            "url": data["html_url"],
            "created_at": data["created_at"]
        }


if __name__ == "__main__":
    mcp.run()
