"""
Quality Agent - 代码质量检查专用 Agent
"""
import asyncio
import json
import argparse
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.utils import timestamp, format_issues_report, format_score


class QualityAgent:
    """
    代码质量 Agent

    负责:
    - 代码风格检查
    - 复杂度分析
    - 重复代码检测
    - 最佳实践检查
    """

    def analyze(self, code: str, language: str = "python") -> dict:
        """分析代码质量"""
        issues = []
        suggestions = []

        # 基础指标
        lines = code.split("\n")
        metrics = {
            "total_lines": len(lines),
            "code_lines": sum(1 for l in lines if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("//")),
            "comment_lines": sum(1 for l in lines if l.strip().startswith("#") or l.strip().startswith("//")),
            "blank_lines": sum(1 for l in lines if not l.strip()),
            "functions": code.count("def ") + code.count("function "),
            "classes": code.count("class ")
        }

        # 1. 检查长行
        long_lines = [i for i, l in enumerate(lines, 1) if len(l) > 120]
        if long_lines:
            issues.append({
                "type": "long_lines",
                "severity": "low",
                "message": f"{len(long_lines)} 行代码超过 120 字符",
                "lines": long_lines[:5]  # 只显示前 5 个
            })
            suggestions.append("将长行拆分为多行，提高可读性")

        # 2. 检查长函数
        function_lengths = self._analyze_function_lengths(code)
        long_functions = [(name, length) for name, length in function_lengths if length > 50]
        if long_functions:
            issues.append({
                "type": "long_functions",
                "severity": "medium",
                "message": f"{len(long_functions)} 个函数超过 50 行",
                "details": long_functions[:3]
            })
            suggestions.append("将长函数拆分为多个小函数，每个函数只做一件事")

        # 3. 检查循环复杂度
        complexity = self._calculate_complexity(code)
        if complexity > 10:
            issues.append({
                "type": "high_complexity",
                "severity": "medium",
                "message": f"循环复杂度为 {complexity}，建议降低到 10 以下"
            })
            suggestions.append("减少嵌套和条件分支，提取复杂逻辑为独立函数")

        # 4. 检查 TODO/FIXME
        todos = re.findall(r"(TODO|FIXME|XXX|HACK)[:\s]*(.*)", code, re.IGNORECASE)
        if todos:
            issues.append({
                "type": "todo_comments",
                "severity": "low",
                "message": f"发现 {len(todos)} 个待办注释",
                "details": [{"tag": t[0], "content": t[1][:50]} for t in todos[:5]]
            })

        # 5. 检查调试代码
        debug_patterns = ["console.log", "print(", "debugger;", "logging.debug", "pdb.set_trace"]
        debug_found = [p for p in debug_patterns if p in code.lower()]
        if debug_found:
            issues.append({
                "type": "debug_code",
                "severity": "medium",
                "message": f"发现调试代码：{', '.join(debug_found)}"
            })
            suggestions.append("移除生产代码中的调试语句")

        # 6. 检查魔法数字
        magic_numbers = re.findall(r'(?<!["\'\w])(\d{2,})(?!["\'\w])', code)
        if len(magic_numbers) > 3:
            issues.append({
                "type": "magic_numbers",
                "severity": "low",
                "message": f"发现 {len(magic_numbers)} 个魔法数字"
            })
            suggestions.append("使用具名常量代替魔法数字")

        # 7. 检查文档字符串
        if (metrics["functions"] > 0 or metrics["classes"] > 0):
            has_docstring = '"""' in code or "'''" in code or "/**" in code
            if not has_docstring:
                issues.append({
                    "type": "missing_docs",
                    "severity": "low",
                    "message": "函数/类缺少文档字符串"
                })
                suggestions.append("为公共 API 添加文档字符串")

        # 计算质量评分
        score = self._calculate_score(issues, metrics)

        return {
            "metrics": metrics,
            "issues": issues,
            "suggestions": suggestions,
            "quality_score": score,
            "grade": self._get_grade(score)
        }

    def _analyze_function_lengths(self, code: str) -> list:
        """分析函数长度"""
        functions = []
        lines = code.split("\n")

        in_function = False
        current_function = ""
        indent_level = 0

        for i, line in enumerate(lines):
            if re.match(r'^\s*(def|function)\s+\w+', line):
                if in_function and current_function:
                    functions.append((current_function, len(current_function.split("\n"))))
                in_function = True
                current_function = line
                indent_level = len(line) - len(line.lstrip())
            elif in_function:
                if line.strip() and len(line) - len(line.lstrip()) <= indent_level and not line.strip().startswith("#"):
                    functions.append((current_function, len(current_function.split("\n"))))
                    in_function = False
                    current_function = ""
                else:
                    current_function += "\n" + line

        if in_function and current_function:
            functions.append((current_function, len(current_function.split("\n"))))

        return functions

    def _calculate_complexity(self, code: str) -> int:
        """计算循环复杂度"""
        complexity = 1  # 基础复杂度

        # 关键字增加复杂度
        keywords = ["if ", "elif ", "else:", "for ", "while ", "case ", "catch ", "?", "&&", "||"]
        for kw in keywords:
            complexity += code.count(kw)

        return complexity

    def _calculate_score(self, issues: list, metrics: dict) -> int:
        """计算质量评分"""
        score = 100

        # 扣分项
        deductions = {
            "long_lines": 5,
            "long_functions": 15,
            "high_complexity": 20,
            "todo_comments": 2,
            "debug_code": 10,
            "magic_numbers": 5,
            "missing_docs": 10
        }

        for issue in issues:
            score -= deductions.get(issue["type"], 5)

        # 注释率奖励
        if metrics["total_lines"] > 0:
            comment_ratio = metrics["comment_lines"] / metrics["total_lines"]
            if comment_ratio > 0.2:
                score += 5

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
    parser = argparse.ArgumentParser(description="Quality Agent - 代码质量检查")
    parser.add_argument("--file", type=str, help="要检查的文件路径")
    parser.add_argument("--code", type=str, help="要检查的代码内容")
    parser.add_argument("--language", type=str, default="python", help="编程语言")
    parser.add_argument("--output", type=str, default="quality_report.json")

    args = parser.parse_args()

    agent = QualityAgent()

    code = args.code
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()

    if not code:
        print("❌ 请提供 --file 或 --code 参数")
        return

    print(f"[{timestamp()}] 💎 开始质量检查...")
    result = agent.analyze(code, args.language)

    print(f"\n{format_score(result['quality_score'], '质量评分')} (等级：{result['grade']})")
    print(f"\n📊 指标:")
    for key, value in result["metrics"].items():
        print(f"  • {key}: {value}")

    print(f"\n{format_issues_report(result['issues'], '质量问题')}")

    if result["suggestions"]:
        print(f"\n💡 建议:")
        for suggestion in result["suggestions"]:
            print(f"  • {suggestion}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n📄 报告已保存到：{args.output}")


if __name__ == "__main__":
    asyncio.run(main())
