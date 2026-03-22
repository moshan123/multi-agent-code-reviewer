"""
Performance Agent - 性能检查专用 Agent

负责检查代码中的性能问题：
- 循环中的数据库查询
- 未缓存的重复计算
- 低效的字符串拼接
- 大列表的低效遍历
- 内存泄漏风险
"""
import asyncio
import json
import argparse
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.utils import timestamp, format_issues_report, format_score


class PerformanceAgent:
    """
    性能检查 Agent

    负责:
    - 检测 N+1 查询问题
    - 检查重复计算
    - 字符串拼接优化
    - 循环优化建议
    - 内存使用分析
    """

    def analyze(self, code: str, language: str = "python") -> dict:
        """分析代码性能"""
        issues = []
        suggestions = []

        lines = code.split("\n")

        # 1. 检测 N+1 查询问题（循环中的数据库操作）
        n_plus_one_patterns = [
            (r'for\s+\w+\s+in\s+\w+:.*?(?:execute|query|fetch|select|insert|update|delete)', 'N+1 查询问题'),
            (r'for\s+\w+\s+in\s+\w+:.*?(?:\.save\(|\.create\(|\.delete\()', 'N+1 数据库写入'),
            (r'for.*?:.*?db\.', '循环中的数据库操作'),
            (r'for.*?:.*?cursor\.execute', '循环中的 SQL 执行'),
        ]

        for pattern, message in n_plus_one_patterns:
            if re.search(pattern, code, re.DOTALL | re.IGNORECASE):
                issues.append({
                    "type": "n_plus_one",
                    "severity": "high",
                    "message": f"检测到{message}，建议批量操作"
                })
                suggestions.append("使用批量查询 (如 IN 语句) 替代循环中的单个查询")

        # 2. 检测低效的字符串拼接
        if re.search(r'for.*?:.*?\+\s*["\']', code, re.DOTALL):
            issues.append({
                "type": "string_concat",
                "severity": "medium",
                "message": "循环中使用字符串拼接，效率低下"
            })
            suggestions.append("使用 join() 方法或列表推导式替代字符串拼接")

        # 3. 检测重复计算
        expensive_patterns = [
            (r'for.*?:.*?len\(', 'len() 函数'),
            (r'for.*?:.*?sorted\(', 'sorted() 函数'),
            (r'for.*?:.*?set\(', 'set() 转换'),
            (r'for.*?:.*?list\(\w+\)', 'list() 转换'),
        ]

        for pattern, message in expensive_patterns:
            if re.search(pattern, code, re.DOTALL):
                issues.append({
                    "type": "redundant_calc",
                    "severity": "low",
                    "message": f"循环中可能重复调用{message}"
                })
                suggestions.append(f"将{message}移至循环外，避免重复计算")

        # 4. 检测大列表的低效操作
        if re.search(r'for.*?:.*?\w+\.index\(', code, re.DOTALL):
            issues.append({
                "type": "inefficient_lookup",
                "severity": "medium",
                "message": "循环中使用 index() 方法，时间复杂度 O(n)"
            })
            suggestions.append("使用 enumerate() 或字典查找替代 index()")

        # 5. 检测内存泄漏风险
        memory_patterns = [
            (r'\w+\s*=\s*\[\].*?for.*?append', '列表无限增长风险'),
            (r'\w+\s*=\s*\{\}.*?for.*?\[\w+\]\s*=', '字典无限增长风险'),
        ]

        for pattern, message in memory_patterns:
            if re.search(pattern, code, re.DOTALL):
                issues.append({
                    "type": "memory_leak",
                    "severity": "medium",
                    "message": f"检测到{message}"
                })
                suggestions.append("考虑使用生成器或限制集合大小")

        # 6. 检测未使用的变量
        assigned_vars = set(re.findall(r'^\s*(\w+)\s*=', code, re.MULTILINE))
        used_vars = set(re.findall(r'\b(\w+)\b', code))
        unused_vars = assigned_vars - used_vars - {'def', 'for', 'if', 'in', 'return'}

        if len(unused_vars) > 3:
            issues.append({
                "type": "unused_vars",
                "severity": "low",
                "message": f"发现 {len(unused_vars)} 个可能未使用的变量"
            })
            suggestions.append("清理未使用的变量，减少内存占用")

        # 7. 检查是否可以使用的优化
        if 'for i in range(len(' in code:
            issues.append({
                "type": "unpythonic",
                "severity": "low",
                "message": "使用 range(len()) 而不是 enumerate()"
            })
            suggestions.append("使用 enumerate() 更符合 Python 风格")

        if '.append(' in code and 'list' in code.lower():
            suggestions.append("考虑使用列表推导式替代 append 循环")

        # 计算性能评分
        score = self._calculate_score(issues)

        return {
            "issues": issues,
            "suggestions": suggestions,
            "performance_score": score,
            "grade": self._get_grade(score)
        }

    def _calculate_score(self, issues: list) -> int:
        """计算性能评分"""
        score = 100

        deductions = {
            "n_plus_one": 25,
            "string_concat": 15,
            "redundant_calc": 10,
            "inefficient_lookup": 15,
            "memory_leak": 20,
            "unused_vars": 5,
            "unpythonic": 5
        }

        for issue in issues:
            score -= deductions.get(issue["type"], 10)

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
    parser = argparse.ArgumentParser(description="Performance Agent - 性能检查")
    parser.add_argument("--file", type=str, help="要检查的文件路径")
    parser.add_argument("--code", type=str, help="要检查的代码内容")
    parser.add_argument("--language", type=str, default="python", help="编程语言")
    parser.add_argument("--output", type=str, default="performance_report.json")

    args = parser.parse_args()

    agent = PerformanceAgent()

    code = args.code
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()

    if not code:
        print("❌ 请提供 --file 或 --code 参数")
        return

    print(f"[{timestamp()}] ⚡ 开始性能检查...")
    result = agent.analyze(code, args.language)

    print(f"\n{format_score(result['performance_score'], '性能评分')} (等级：{result['grade']})")
    print(f"\n{format_issues_report(result['issues'], '性能问题')}")

    if result["suggestions"]:
        print(f"\n💡 建议:")
        for suggestion in result["suggestions"]:
            print(f"  • {suggestion}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n📄 报告已保存到：{args.output}")


if __name__ == "__main__":
    asyncio.run(main())
