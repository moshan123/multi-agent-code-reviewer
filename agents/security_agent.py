"""
Security Agent - 安全检查专用 Agent
"""
import asyncio
import json
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.mcp_config import MCPConfig
from shared.utils import timestamp, format_issues_report, severity_icon


class SecurityAgent:
    """
    安全检查 Agent

    负责:
    - 检测敏感信息泄露
    - SQL 注入风险
    - XSS 漏洞
    - 命令注入
    - 路径遍历
    """

    SECURITY_PATTERNS = {
        "sql_injection": {
            "patterns": ["execute(", "raw(", "executeQuery(", "createStatement("],
            "safe_patterns": ["prepared", "parameterized", "?", ":"],
            "severity": "high",
            "message": "可能存在 SQL 注入风险"
        },
        "xss": {
            "patterns": ["innerHTML", "dangerouslySetInnerHTML", "document.write", "eval("],
            "safe_patterns": ["sanitize", "escape", "encode"],
            "severity": "high",
            "message": "可能存在 XSS 风险"
        },
        "command_injection": {
            "patterns": ["os.system(", "subprocess.call(", "subprocess.run(", "exec(", "shell=True"],
            "safe_patterns": ["shlex", "quote"],
            "severity": "high",
            "message": "可能存在命令注入风险"
        },
        "path_traversal": {
            "patterns": ["open(", "read_file(", "write_file("],
            "safe_patterns": ["safe_join", "base_path", "resolve"],
            "severity": "medium",
            "message": "可能存在路径遍历风险"
        },
        "hardcoded_secret": {
            "patterns": ["password=", "api_key=", "secret=", "token=", "credential="],
            "safe_patterns": ["env", "config", "process.env", "os.getenv"],
            "severity": "high",
            "message": "可能存在硬编码敏感信息"
        },
        "weak_crypto": {
            "patterns": ["md5(", "sha1(", "des(", "rc4("],
            "safe_patterns": ["sha256", "sha512", "bcrypt", "argon2"],
            "severity": "medium",
            "message": "可能使用了弱加密算法"
        }
    }

    def analyze(self, code: str, filename: str = "") -> dict:
        """分析代码安全问题"""
        issues = []
        suggestions = []
        code_lower = code.lower()

        for vuln_type, config in self.SECURITY_PATTERNS.items():
            for pattern in config["patterns"]:
                if pattern.lower() in code_lower:
                    # 检查是否有防护措施
                    has_protection = any(
                        safe.lower() in code_lower for safe in config["safe_patterns"]
                    )

                    if not has_protection:
                        issues.append({
                            "type": vuln_type,
                            "severity": config["severity"],
                            "message": config["message"],
                            "filename": filename,
                            "pattern": pattern
                        })

                        # 添加建议
                        suggestions.append(self._get_suggestion(vuln_type))

        # 去重
        unique_suggestions = list(dict.fromkeys(suggestions))

        return {
            "issues": issues,
            "suggestions": unique_suggestions,
            "risk_level": self._calculate_risk_level(issues),
            "checked_patterns": len(self.SECURITY_PATTERNS)
        }

    def _get_suggestion(self, vuln_type: str) -> str:
        """获取修复建议"""
        suggestions = {
            "sql_injection": "✅ 使用参数化查询或 ORM 框架",
            "xss": "✅ 对用户输入进行 HTML 转义，使用 CSP",
            "command_injection": "✅ 避免使用 shell=True，使用 shlex.quote()",
            "path_traversal": "✅ 使用安全的路径拼接方法，验证文件路径",
            "hardcoded_secret": "✅ 使用环境变量或密钥管理服务",
            "weak_crypto": "✅ 使用 SHA-256 或更强的加密算法"
        }
        return suggestions.get(vuln_type, "请审查相关代码")

    def _calculate_risk_level(self, issues: list) -> str:
        """计算风险等级"""
        if any(i["severity"] == "high" for i in issues):
            return "high"
        elif issues:
            return "medium"
        return "low"


async def main():
    parser = argparse.ArgumentParser(description="Security Agent - 代码安全检查")
    parser.add_argument("--file", type=str, help="要检查的文件路径")
    parser.add_argument("--code", type=str, help="要检查的代码内容")
    parser.add_argument("--repo", type=str, help="仓库全名")
    parser.add_argument("--pr", type=int, help="PR 编号")
    parser.add_argument("--output", type=str, default="security_report.json")

    args = parser.parse_args()

    agent = SecurityAgent()

    code = args.code
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()

    if not code:
        print("❌ 请提供 --file 或 --code 参数")
        return

    print(f"[{timestamp()}] 🔒 开始安全检查...")
    result = agent.analyze(code)

    # 输出结果
    print(f"\n{format_issues_report(result['issues'], '安全问题')}")
    print(f"\n风险等级：{result['risk_level']}")
    print(f"\n💡 建议:")
    for suggestion in result["suggestions"]:
        print(f"  • {suggestion}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n📄 报告已保存到：{args.output}")


if __name__ == "__main__":
    asyncio.run(main())
