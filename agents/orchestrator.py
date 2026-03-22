"""
Orchestrator Agent - 协调器，负责任务分发和结果汇总
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.mcp_config import MCPConfig
from shared.utils import (
    format_diff_summary,
    format_file_tree,
    format_issues_report,
    generate_review_summary,
    timestamp
)

from .performance_agent import PerformanceAgent


class OrchestratorAgent:
    """
    协调器 Agent

    职责:
    1. 接收用户请求
    2. 分析请求类型
    3. 分发任务给专业 Agent
    4. 汇总结果生成报告
    """

    def __init__(self):
        self.config = MCPConfig()
        self.security_agent = SecurityAgent()
        self.quality_agent = QualityAgent()
        self.docs_agent = DocumentationAgent()
        self.performance_agent = PerformanceAgent()

    async def process_pr(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        处理 PR 审查请求

        Args:
            repo: 仓库全名
            pr_number: PR 编号

        Returns:
            审查结果
        """
        print(f"[{timestamp()}] 🚀 开始审查 PR: {repo}#{pr_number}")

        # 获取 PR 信息
        pr_info = await self._fetch_pr_info(repo, pr_number)
        if not pr_info:
            return {"error": "无法获取 PR 信息"}

        print(f"[{timestamp()}] 📄 PR 标题：{pr_info['title']}")
        print(f"[{timestamp()}] 📊 变更文件数：{len(pr_info['files'])}")

        # 并行执行多个 Agent
        print(f"[{timestamp()}] 🤖 启动多 Agent 协作...")

        results = await asyncio.gather(
            self.security_agent.analyze(pr_info),
            self.quality_agent.analyze(pr_info),
            self.docs_agent.analyze(pr_info),
            self.performance_agent.analyze(pr_info),
            return_exceptions=True
        )

        security_result = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        quality_result = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
        docs_result = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
        performance_result = results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])}

        # 生成最终报告
        report = self._generate_report(pr_info, security_result, quality_result, docs_result, performance_result)

        print(f"[{timestamp()}] ✅ 审查完成")
        return report

    async def _fetch_pr_info(self, repo: str, pr_number: int) -> Optional[Dict]:
        """获取 PR 信息"""
        # 这里应该调用 GitHub MCP Server
        # 简化版本：模拟数据
        await asyncio.sleep(0.5)  # 模拟网络请求

        # 实际应该使用 httpx 调用 GitHub API
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.config.GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                }

                # 获取 PR 详情
                pr_response = await client.get(
                    f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
                    headers=headers
                )
                if pr_response.status_code != 200:
                    print(f"❌ 获取 PR 失败：{pr_response.text}")
                    return None

                pr_data = pr_response.json()

                # 获取文件变更
                files_response = await client.get(
                    f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files",
                    headers=headers
                )
                files_data = files_response.json() if files_response.status_code == 200 else []

                return {
                    "number": pr_data["number"],
                    "title": pr_data["title"],
                    "description": pr_data.get("body", ""),
                    "author": pr_data["user"]["login"],
                    "files": files_data,
                    "base_branch": pr_data["base"]["ref"],
                    "head_branch": pr_data["head"]["ref"]
                }
        except Exception as e:
            print(f"❌ 获取 PR 信息失败：{e}")
            return None

    def _generate_report(
        self,
        pr_info: Dict,
        security_result: Dict,
        quality_result: Dict,
        docs_result: Dict,
        performance_result: Dict
    ) -> Dict[str, Any]:
        """生成审查报告"""

        # 计算总体评分
        security_score = 100 - len(security_result.get("issues", [])) * 15
        quality_score = quality_result.get("quality_score", 0)
        docs_score = docs_result.get("doc_score", 0)
        performance_score = performance_result.get("performance_score", 0)
        overall_score = (security_score + quality_score + docs_score + performance_score) // 4

        # 构建报告
        report = {
            "pr_info": {
                "repo": pr_info.get("full_name", ""),
                "number": pr_info["number"],
                "title": pr_info["title"],
                "author": pr_info["author"]
            },
            "timestamp": timestamp(),
            "scores": {
                "security": max(0, security_score),
                "quality": quality_score,
                "documentation": docs_score,
                "performance": performance_score,
                "overall": overall_score
            },
            "results": {
                "security": security_result,
                "quality": quality_result,
                "documentation": docs_result,
                "performance": performance_result
            },
            "summary": self._generate_summary(
                security_result, quality_result, docs_result, performance_result, overall_score
            )
        }

        return report

    def _generate_summary(
        self,
        security_result: Dict,
        quality_result: Dict,
        docs_result: Dict,
        performance_result: Dict,
        overall_score: int
    ) -> str:
        """生成文字摘要"""
        lines = [
            "## 📋 代码审查报告",
            "",
            generate_review_summary(security_result, quality_result, docs_result),
            "",
            format_issues_report(
                security_result.get("issues", []),
                "🔒 安全问题"
            ),
            "",
            format_issues_report(
                quality_result.get("issues", []),
                "💎 代码质量问题"
            ),
            "",
            format_issues_report(
                docs_result.get("issues", []),
                "📖 文档问题"
            ),
            "",
            format_issues_report(
                performance_result.get("issues", []),
                "⚡ 性能问题"
            ),
            "",
            "## 💡 改进建议",
            ""
        ]

        # 收集所有建议
        suggestions = []
        suggestions.extend(security_result.get("suggestions", []))
        suggestions.extend(quality_result.get("suggestions", []))
        suggestions.extend(docs_result.get("suggestions", []))
        suggestions.extend(performance_result.get("suggestions", []))

        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"{i}. {suggestion}")
        else:
            lines.append("✅ 代码质量良好，无需特别改进")

        return "\n".join(lines)


class SecurityAgent:
    """安全检查 Agent"""

    async def analyze(self, pr_info: Dict) -> Dict:
        """分析代码安全问题"""
        issues = []
        suggestions = []

        for file in pr_info.get("files", []):
            patch = file.get("patch", "")
            filename = file.get("filename", "")

            # 安全检查
            security_patterns = [
                ("password", "可能包含密码"),
                ("secret", "可能包含密钥"),
                ("token", "可能包含令牌"),
                ("api_key", "可能包含 API 密钥"),
                ("credential", "可能包含凭证"),
            ]

            for pattern, message in security_patterns:
                if pattern.lower() in patch.lower():
                    # 检查是否有防护
                    if "env" not in patch.lower() and "config" not in patch.lower():
                        issues.append({
                            "type": "potential_secret",
                            "severity": "high",
                            "message": message,
                            "filename": filename
                        })

            # 检查 SQL 注入
            if any(x in patch.lower() for x in ["execute(", "raw(", "query("]):
                if "prepared" not in patch.lower() and "parameterized" not in patch.lower():
                    issues.append({
                        "type": "sql_injection",
                        "severity": "high",
                        "message": "可能存在 SQL 注入风险",
                        "filename": filename
                    })
                    suggestions.append("使用参数化查询防止 SQL 注入")

        return {
            "issues": issues,
            "suggestions": suggestions,
            "risk_level": "high" if any(i["severity"] == "high" for i in issues) else "low"
        }


class QualityAgent:
    """代码质量 Agent"""

    async def analyze(self, pr_info: Dict) -> Dict:
        """分析代码质量"""
        issues = []
        suggestions = []

        for file in pr_info.get("files", []):
            patch = file.get("patch", "")
            filename = file.get("filename", "")

            # 检查长行
            for i, line in enumerate(patch.split("\n"), 1):
                if line.startswith("+") and len(line) > 120:
                    issues.append({
                        "type": "long_line",
                        "severity": "low",
                        "message": f"代码行过长 ({len(line)} 字符)",
                        "filename": filename
                    })
                    break  # 每个文件只报告一次

            # 检查 TODO/FIXME
            if "TODO" in patch or "FIXME" in patch:
                issues.append({
                    "type": "todo_comment",
                    "severity": "low",
                    "message": "存在待办注释",
                    "filename": filename
                })

            # 检查调试代码
            if any(x in patch.lower() for x in ["console.log", "print(", "debugger"]):
                issues.append({
                    "type": "debug_code",
                    "severity": "medium",
                    "message": "存在调试代码",
                    "filename": filename
                })
                suggestions.append("移除调试代码后再提交")

        # 质量评分
        score = max(0, 100 - len(issues) * 10)

        return {
            "issues": issues,
            "suggestions": suggestions,
            "quality_score": score
        }


class DocumentationAgent:
    """文档检查 Agent"""

    async def analyze(self, pr_info: Dict) -> Dict:
        """分析文档完整性"""
        issues = []
        suggestions = []

        # 检查 PR 描述
        description = pr_info.get("description", "")
        if not description or len(description) < 20:
            issues.append({
                "type": "missing_description",
                "severity": "medium",
                "message": "PR 描述过于简单或缺失"
            })
            suggestions.append("补充 PR 描述，说明修改目的和测试方法")

        # 检查文件变更
        for file in pr_info.get("files", []):
            patch = file.get("patch", "")
            filename = file.get("filename", "")

            # 新增文件检查
            if file.get("status") == "added":
                # 检查是否有文档
                if filename.endswith(".py") or filename.endswith(".js") or filename.endswith(".ts"):
                    if '"""' not in patch and "/**" not in patch and "//!" not in patch:
                        issues.append({
                            "type": "missing_file_docs",
                            "severity": "low",
                            "message": "新文件缺少文档注释",
                            "filename": filename
                        })

        score = max(0, 100 - len(issues) * 20)

        return {
            "issues": issues,
            "suggestions": suggestions,
            "doc_score": score,
            "has_description": bool(description and len(description) > 0)
        }


# CLI 入口
async def main():
    import argparse

    parser = argparse.ArgumentParser(description="代码审查 Orchestrator")
    parser.add_argument("--repo", type=str, required=True, help="仓库全名 (owner/repo)")
    parser.add_argument("--pr", type=int, required=True, help="PR 编号")
    parser.add_argument("--output", type=str, default="report.json", help="输出文件路径")

    args = parser.parse_args()

    orchestrator = OrchestratorAgent()
    result = await orchestrator.process_pr(args.repo, args.pr)

    # 输出结果
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n📄 报告已保存到：{args.output}")
    print("\n" + result.get("summary", ""))


if __name__ == "__main__":
    asyncio.run(main())
