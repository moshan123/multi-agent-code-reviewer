"""
共享工具函数
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


def format_diff_summary(files: List[Dict]) -> str:
    """格式化文件变更摘要"""
    if not files:
        return "没有文件变更"

    total_additions = sum(f.get("additions", 0) for f in files)
    total_deletions = sum(f.get("deletions", 0) for f in files)
    total_changes = sum(f.get("changes", 0) for f in files)

    summary = [
        f"📊 变更统计:",
        f"  • 文件数：{len(files)}",
        f"  • 新增行数：+{total_additions}",
        f"  • 删除行数：-{total_deletions}",
        f"  • 总变更：{total_changes} 行"
    ]

    return "\n".join(summary)


def format_file_tree(files: List[Dict]) -> str:
    """格式化文件树展示"""
    if not files:
        return "空"

    lines = ["📁 变更文件:"]
    for f in sorted(files, key=lambda x: x["filename"]):
        status_icon = {
            "added": "🆕",
            "modified": "📝",
            "deleted": "❌",
            "renamed": "🔄"
        }.get(f.get("status", "modified"), "📝")
        lines.append(f"  {status_icon} {f['filename']}")

    return "\n".join(lines)


def severity_icon(severity: str) -> str:
    """获取严重程度的图标"""
    icons = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
        "critical": "🚨"
    }
    return icons.get(severity, "⚪")


def format_issues_report(issues: List[Dict], title: str = "问题列表") -> str:
    """格式化问题报告"""
    if not issues:
        return f"✅ {title}: 未发现问题"

    # 按严重程度排序
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_issues = sorted(issues, key=lambda x: severity_order.get(x.get("severity", "low"), 4))

    lines = [f"📋 {title}:"]
    for issue in sorted_issues:
        icon = severity_icon(issue.get("severity", "low"))
        lines.append(f"  {icon} [{issue.get('severity', 'unknown').upper()}] {issue.get('message', 'Unknown issue')}")
        if "filename" in issue:
            lines.append(f"     📄 {issue['filename']}")

    return "\n".join(lines)


def format_score(score: int, label: str = "评分") -> str:
    """格式化评分显示"""
    if score >= 90:
        grade = "A"
        emoji = "🌟"
    elif score >= 80:
        grade = "B"
        emoji = "✅"
    elif score >= 70:
        grade = "C"
        emoji = "⚠️"
    elif score >= 60:
        grade = "D"
        emoji = "❗"
    else:
        grade = "F"
        emoji = "🚨"

    return f"{emoji} {label}: {score}/100 (等级：{grade})"


def generate_review_summary(
    security_result: Dict,
    quality_result: Dict,
    doc_result: Dict
) -> str:
    """生成审查总览"""
    sections = []

    # 安全评分
    security_score = 100 - len(security_result.get("issues", [])) * 15
    sections.append(format_score(max(0, security_score), "安全"))

    # 质量评分
    sections.append(format_score(quality_result.get("quality_score", 0), "质量"))

    # 文档评分
    sections.append(format_score(doc_result.get("doc_score", 0), "文档"))

    return "\n".join(sections)


def timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def json_dumps_safe(obj: Any, **kwargs) -> str:
    """安全的 JSON 序列化"""
    try:
        return json.dumps(obj, ensure_ascii=False, **kwargs)
    except (TypeError, ValueError) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
