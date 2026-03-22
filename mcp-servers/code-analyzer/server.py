"""
代码分析 MCP Server - 提供代码审查和分析工具
"""
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Optional
import httpx
import os

mcp = FastMCP("code-analyzer")


class CodeChange(BaseModel):
    """代码变更"""
    filename: str
    diff: str
    status: str  # added, modified, deleted


class AnalysisResult(BaseModel):
    """分析结果"""
    filename: str
    issues: list[dict]
    suggestions: list[str]
    score: int  # 0-100


@mcp.tool()
async def analyze_code_diff(diff: str, language: str = "java") -> dict:
    """
    分析代码 diff，识别潜在问题

    Args:
        diff: 代码 diff 内容
        language: 编程语言

    Returns:
        分析结果，包含问题列表和建议
    """
    issues = []
    suggestions = []

    # 简单的代码分析逻辑
    lines = diff.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('+'):
            # 检查新增代码
            if 'TODO' in line or 'FIXME' in line:
                issues.append({
                    "line": i,
                    "severity": "low",
                    "message": "发现待办标记",
                    "code": line.strip()
                })
            if 'print(' in line or 'console.log' in line:
                issues.append({
                    "line": i,
                    "severity": "low",
                    "message": "发现调试输出，建议移除",
                    "code": line.strip()
                })
            if 'password' in line.lower() or 'secret' in line.lower() or 'token' in line.lower():
                issues.append({
                    "line": i,
                    "severity": "high",
                    "message": "可能包含敏感信息",
                    "code": line.strip()
                })
            if len(line) > 120:
                issues.append({
                    "line": i,
                    "severity": "medium",
                    "message": "代码行过长（超过 120 字符）",
                    "code": line.strip()[:50] + "..."
                })

    # 生成建议
    if any('import' in line for line in lines):
        suggestions.append("检查 import 是否必要，避免未使用的导入")
    if any('def ' in line or 'function' in line for line in lines):
        suggestions.append("确保函数有清晰的文档字符串")
    if any('if ' in line for line in lines):
        suggestions.append("考虑添加边界条件的测试用例")

    score = max(0, 100 - len(issues) * 10)

    return {
        "issues": issues,
        "suggestions": suggestions,
        "score": score,
        "total_lines": len(lines)
    }


@mcp.tool()
async def check_security_issues(code: str, language: str = "java") -> dict:
    """
    检查代码安全问题

    Args:
        code: 代码内容
        language: 编程语言

    Returns:
        安全问题列表
    """
    security_issues = []

    # 常见安全检查
    checks = [
        ("sql injection", ["execute(", "raw(", "executeQuery"], "high"),
        ("xss", ["innerHTML", "dangerouslySetInnerHTML", "document.write"], "high"),
        ("command injection", ["os.system", "subprocess.call", "exec("], "high"),
        ("path traversal", ["open(", "read_file"], "medium"),
        ("hardcoded credentials", ["password=", "api_key=", "secret=", "token="], "high"),
    ]

    code_lower = code.lower()
    for issue_type, patterns, severity in checks:
        for pattern in patterns:
            if pattern.lower() in code_lower:
                # 检查是否有防护
                if "prepared" not in code_lower and "sanitize" not in code_lower:
                    security_issues.append({
                        "type": issue_type,
                        "severity": severity,
                        "message": f"可能存在{issue_type}风险",
                        "suggestion": f"请检查相关代码并使用适当的防护措施"
                    })

    return {
        "issues": security_issues,
        "risk_level": "high" if any(i["severity"] == "high" for i in security_issues) else "medium" if security_issues else "low"
    }


@mcp.tool()
async def check_code_quality(code: str, language: str = "java") -> dict:
    """
    检查代码质量

    Args:
        code: 代码内容
        language: 编程语言

    Returns:
        质量评分和问题列表
    """
    issues = []
    metrics = {
        "lines": len(code.split('\n')),
        "functions": code.count('def ') + code.count('function '),
        "classes": code.count('class '),
        "complexity": 0
    }

    # 计算复杂度
    for line in code.split('\n'):
        if any(kw in line for kw in ['if ', 'else', 'for ', 'while ', 'switch ', 'try ', 'catch']):
            metrics["complexity"] += 1

    # 检查长函数
    lines = code.split('\n')
    in_function = False
    function_start = 0
    function_lines = 0

    for i, line in enumerate(lines):
        if 'def ' in line or 'function ' in line:
            if in_function and function_lines > 50:
                issues.append({
                    "type": "long_function",
                    "severity": "medium",
                    "message": f"函数过长 ({function_lines} 行)，建议拆分",
                    "line": function_start
                })
            in_function = True
            function_start = i
            function_lines = 0
        elif in_function:
            function_lines += 1

    # 检查魔法数字
    import re
    magic_numbers = re.findall(r'\b\d{2,}\b', code)
    if len(magic_numbers) > 3:
        issues.append({
            "type": "magic_numbers",
            "severity": "low",
            "message": f"发现多个魔法数字，建议使用常量",
            "count": len(magic_numbers)
        })

    # 质量评分
    quality_score = 100
    quality_score -= len(issues) * 10
    if metrics["complexity"] > 20:
        quality_score -= 10
    if metrics["lines"] > 500:
        quality_score -= 5

    return {
        "metrics": metrics,
        "issues": issues,
        "quality_score": max(0, min(100, quality_score))
    }


@mcp.tool()
async def check_documentation(code: str, pr_description: Optional[str] = None) -> dict:
    """
    检查文档完整性

    Args:
        code: 代码内容
        pr_description: PR 描述

    Returns:
        文档检查结果
    """
    doc_issues = []

    # 检查函数文档
    if ('def ' in code or 'function ' in code) and ('"""' not in code and '/**' not in code and '//!' not in code):
        doc_issues.append({
            "type": "missing_docs",
            "severity": "medium",
            "message": "公共函数缺少文档注释"
        })

    # 检查 PR 描述
    if pr_description and len(pr_description) < 20:
        doc_issues.append({
            "type": "incomplete_description",
            "severity": "low",
            "message": "PR 描述过于简单，建议补充修改说明和测试方法"
        })

    # 检查类型注解
    if ('def ' in code or 'function ' in code) and (':' not in code.split('def ')[-1] if 'def ' in code else True):
        doc_issues.append({
            "type": "missing_types",
            "severity": "low",
            "message": "建议添加类型注解"
        })

    return {
        "issues": doc_issues,
        "doc_score": max(0, 100 - len(doc_issues) * 20),
        "has_pr_description": bool(pr_description and len(pr_description) > 0)
    }


if __name__ == "__main__":
    mcp.run()
