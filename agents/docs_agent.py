"""
Documentation Agent - 文档检查专用 Agent
"""
import asyncio
import json
import argparse
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.utils import timestamp, format_issues_report, format_score


class DocumentationAgent:
    """
    文档检查 Agent

    负责:
    - 检查函数/类文档字符串
    - 检查 PR 描述完整性
    - 检查注释质量
    - 检查 README 更新
    """

    def analyze(self, code: str, pr_description: str = "", filename: str = "") -> dict:
        """分析文档完整性"""
        issues = []
        suggestions = []

        # 1. 检查 PR 描述
        if pr_description:
            pr_analysis = self._analyze_pr_description(pr_description)
            if not pr_analysis["has_purpose"]:
                issues.append({
                    "type": "missing_purpose",
                    "severity": "medium",
                    "message": "PR 描述缺少修改目的说明"
                })
                suggestions.append("在 PR 描述中说明本次修改的目的和背景")

            if not pr_analysis["has_testing"]:
                issues.append({
                    "type": "missing_testing",
                    "severity": "low",
                    "message": "PR 描述缺少测试方法说明"
                })
                suggestions.append("说明如何测试这些变更")

            if len(pr_description) < 50:
                issues.append({
                    "type": "short_description",
                    "severity": "low",
                    "message": "PR 描述过于简短"
                })
        else:
            issues.append({
                "type": "missing_description",
                "severity": "medium",
                "message": "缺少 PR 描述"
            })
            suggestions.append("添加 PR 描述，说明修改内容和原因")

        # 2. 检查代码文档
        doc_analysis = self._analyze_code_docs(code)

        if doc_analysis["has_functions"] and not doc_analysis["has_function_docs"]:
            issues.append({
                "type": "missing_function_docs",
                "severity": "medium",
                "message": f"{doc_analysis['function_count']} 个函数缺少文档字符串"
            })
            suggestions.append("为公共函数添加文档字符串，说明参数和返回值")

        if doc_analysis["has_classes"] and not doc_analysis["has_class_docs"]:
            issues.append({
                "type": "missing_class_docs",
                "severity": "medium",
                "message": "类缺少文档字符串"
            })
            suggestions.append("为类添加文档字符串，说明用途和用法")

        # 3. 检查注释质量
        comment_analysis = self._analyze_comments(code)
        if comment_analysis["has_todos"] and comment_analysis["todo_count"] > 3:
            issues.append({
                "type": "too_many_todos",
                "severity": "low",
                "message": f"发现 {comment_analysis['todo_count']} 个 TODO 注释"
            })

        if comment_analysis["has_magic_comments"]:
            suggestions.append("将魔法注释替换为有意义的说明")

        # 4. 检查类型注解
        if doc_analysis["has_functions"] and not doc_analysis["has_type_hints"]:
            issues.append({
                "type": "missing_type_hints",
                "severity": "low",
                "message": "函数缺少类型注解"
            })
            suggestions.append("添加类型注解提高代码可读性和 IDE 支持")

        # 计算文档评分
        score = self._calculate_score(issues)

        return {
            "issues": issues,
            "suggestions": suggestions,
            "doc_score": score,
            "grade": self._get_grade(score),
            "analysis": {
                "pr_description": pr_analysis if pr_description else {"provided": False},
                "code_docs": doc_analysis,
                "comments": comment_analysis
            }
        }

    def _analyze_pr_description(self, description: str) -> dict:
        """分析 PR 描述"""
        desc_lower = description.lower()

        keywords_purpose = ["purpose", "goal", "aim", "change", "modify", "fix", "add", "implement", "目的", "修改", "修复", "添加"]
        keywords_testing = ["test", "testing", "verify", "manual test", "automated test", "测试", "验证"]

        return {
            "has_purpose": any(kw in desc_lower for kw in keywords_purpose),
            "has_testing": any(kw in desc_lower for kw in keywords_testing),
            "word_count": len(description.split()),
            "has_code_block": "```" in description,
            "has_checklist": "- [ ]" in description or "- [x]" in description,
            "has_screenshot": "screenshot" in desc_lower or "image" in desc_lower
        }

    def _analyze_code_docs(self, code: str) -> dict:
        """分析代码文档"""
        lines = code.split("\n")

        # 检测函数
        function_pattern = r'^\s*(def|function)\s+\w+'
        functions = [i for i, line in enumerate(lines) if re.match(function_pattern, line)]

        # 检测类
        class_pattern = r'^\s*class\s+\w+'
        classes = [i for i, line in enumerate(lines) if re.match(class_pattern, line)]

        # 检测文档字符串
        has_docstring = '"""' in code or "'''" in code or "/**" in code or "///" in code

        # 检测类型注解
        has_type_hints = bool(re.search(r'def\s+\w+\s*\([^)]*:\s*\w+', code))

        # 检测函数前的文档字符串
        has_function_docs = False
        for func_line in functions:
            if func_line + 1 < len(lines):
                next_line = lines[func_line + 1].strip()
                if next_line.startswith('"""') or next_line.startswith("'''") or next_line.startswith('"""'):
                    has_function_docs = True
                    break

        # 检测类前的文档字符串
        has_class_docs = False
        for class_line in classes:
            if class_line + 1 < len(lines):
                next_line = lines[class_line + 1].strip()
                if next_line.startswith('"""') or next_line.startswith("'''"):
                    has_class_docs = True
                    break

        return {
            "has_functions": len(functions) > 0,
            "function_count": len(functions),
            "has_classes": len(classes) > 0,
            "class_count": len(classes),
            "has_function_docs": has_function_docs,
            "has_class_docs": has_class_docs,
            "has_docstring": has_docstring,
            "has_type_hints": has_type_hints
        }

    def _analyze_comments(self, code: str) -> dict:
        """分析注释"""
        lines = code.split("\n")

        todos = re.findall(r'(TODO|FIXME|XXX|HACK|NOTE)', code, re.IGNORECASE)
        magic_comments = re.findall(r'#\s*\d+', code)  # 类似 # 1, # 2 的注释

        return {
            "has_todos": len(todos) > 0,
            "todo_count": len(todos),
            "has_magic_comments": len(magic_comments) > 0,
            "comment_ratio": sum(1 for l in lines if l.strip().startswith('#') or l.strip().startswith('//')) / max(1, len(lines))
        }

    def _calculate_score(self, issues: list) -> int:
        """计算文档评分"""
        score = 100

        deductions = {
            "missing_description": 20,
            "missing_purpose": 15,
            "missing_testing": 10,
            "short_description": 5,
            "missing_function_docs": 20,
            "missing_class_docs": 15,
            "too_many_todos": 5,
            "missing_type_hints": 10
        }

        for issue in issues:
            score -= deductions.get(issue["type"], 5)

        return max(0, min(100, score))

    def _get_grade(self, score: int) -> str:
        """获取等级"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        return "F"


async def main():
    parser = argparse.ArgumentParser(description="Documentation Agent - 文档检查")
    parser.add_argument("--file", type=str, help="要检查的文件路径")
    parser.add_argument("--code", type=str, help="要检查的代码内容")
    parser.add_argument("--description", type=str, help="PR 描述")
    parser.add_argument("--output", type=str, default="docs_report.json")

    args = parser.parse_args()

    agent = DocumentationAgent()

    code = args.code
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()

    if not code:
        print("❌ 请提供 --file 或 --code 参数")
        return

    print(f"[{timestamp()}] 📖 开始文档检查...")
    result = agent.analyze(code, args.description or "")

    print(f"\n{format_score(result['doc_score'], '文档评分')} (等级：{result['grade']})")
    print(f"\n{format_issues_report(result['issues'], '文档问题')}")

    if result["suggestions"]:
        print(f"\n💡 建议:")
        for suggestion in result["suggestions"]:
            print(f"  • {suggestion}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n📄 报告已保存到：{args.output}")


if __name__ == "__main__":
    asyncio.run(main())
