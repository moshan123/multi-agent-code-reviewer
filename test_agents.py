#!/usr/bin/env python3
"""
测试脚本 - 验证 Multi-Agent 代码审查系统
"""
import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from shared.utils import timestamp, format_score, format_issues_report
from agents.security_agent import SecurityAgent
from agents.quality_agent import QualityAgent
from agents.docs_agent import DocumentationAgent


# 测试代码样本
TEST_CODE = '''
def calculate_total(items):
    """计算商品总价"""
    total = 0
    for item in items:
        # TODO: 处理折扣
        if item['price'] > 100:
            total += item['price'] * 0.9
        else:
            total += item['price']

    # FIXME: 需要处理税费
    print(f"Total: {total}")  # 调试输出
    return total


def process_order(order_id, user_id, items):
    # 长函数示例 - 超过 50 行
    order = {}
    order['id'] = order_id
    order['user_id'] = user_id
    order['items'] = items
    order['status'] = 'pending'

    # 计算总价
    total = 0
    for item in items:
        total += item.get('price', 0)

    order['total'] = total

    # 应用折扣
    if total > 1000:
        discount = total * 0.1
    elif total > 500:
        discount = total * 0.05
    else:
        discount = 0

    order['discount'] = discount
    order['final_total'] = total - discount

    # 计算税费
    tax_rate = 0.08
    tax = (total - discount) * tax_rate
    order['tax'] = tax
    order['grand_total'] = total - discount + tax

    # 保存订单
    # db.save(order)

    # 发送确认邮件
    # send_email(user_id, order)

    # 更新库存
    # for item in items:
    #     update_stock(item['id'])

    return order


# 敏感信息示例
API_KEY = "sk-1234567890"
password = "admin123"


def execute_query(sql):
    # SQL 注入风险
    query = f"SELECT * FROM users WHERE id = {sql}"
    return query


class UserManager:
    def get_user(self, user_id):
        # 缺少文档字符串
        return {"id": user_id, "name": "Test"}
'''

TEST_PR_DESCRIPTION = """
这个 PR 修改了订单处理逻辑。
主要变更:
- 优化了折扣计算
- 添加了税费计算

测试方法:
- 运行单元测试
- 手动测试不同金额的场景
"""


def test_security_agent():
    """测试 Security Agent"""
    print(f"\n{'='*60}")
    print(f"[{timestamp()}] 🔒 测试 Security Agent")
    print('='*60)

    agent = SecurityAgent()
    result = agent.analyze(TEST_CODE, "test.py")

    print(f"\n风险等级：{result['risk_level']}")
    print(f"\n{format_issues_report(result['issues'], '安全问题')}")

    if result['suggestions']:
        print(f"\n💡 建议:")
        for s in result['suggestions']:
            print(f"  • {s}")

    print(f"\n✅ Security Agent 测试完成")
    return result


def test_quality_agent():
    """测试 Quality Agent"""
    print(f"\n{'='*60}")
    print(f"[{timestamp()}] 💎 测试 Quality Agent")
    print('='*60)

    agent = QualityAgent()
    result = agent.analyze(TEST_CODE, "python")

    print(f"\n{format_score(result['quality_score'], '质量评分')} (等级：{result['grade']})")

    print(f"\n📊 指标:")
    for key, value in result['metrics'].items():
        print(f"  • {key}: {value}")

    print(f"\n{format_issues_report(result['issues'], '质量问题')}")

    if result['suggestions']:
        print(f"\n💡 建议:")
        for s in result['suggestions']:
            print(f"  • {s}")

    print(f"\n✅ Quality Agent 测试完成")
    return result


def test_docs_agent():
    """测试 Documentation Agent"""
    print(f"\n{'='*60}")
    print(f"[{timestamp()}] 📖 测试 Documentation Agent")
    print('='*60)

    agent = DocumentationAgent()
    result = agent.analyze(TEST_CODE, TEST_PR_DESCRIPTION, "test.py")

    print(f"\n{format_score(result['doc_score'], '文档评分')} (等级：{result['grade']})")
    print(f"\n{format_issues_report(result['issues'], '文档问题')}")

    if result['suggestions']:
        print(f"\n💡 建议:")
        for s in result['suggestions']:
            print(f"  • {s}")

    print(f"\n✅ Documentation Agent 测试完成")
    return result


def main():
    """主测试函数"""
    print(f"\n{'#'*60}")
    print(f"#[{timestamp()}] 🚀 Multi-Agent 代码审查系统 - 测试")
    print(f"{'#'*60}")

    # 测试所有 Agent
    security_result = test_security_agent()
    quality_result = test_quality_agent()
    docs_result = test_docs_agent()

    # 汇总报告
    print(f"\n{'='*60}")
    print(f"[{timestamp()}] 📊 测试汇总")
    print('='*60)

    print(f"\n🔒 安全：{security_result['risk_level']}风险 - {len(security_result['issues'])} 个问题")
    print(f"💎 质量：{format_score(quality_result['quality_score'])} ({quality_result['grade']}) - {len(quality_result['issues'])} 个问题")
    print(f"📖 文档：{format_score(docs_result['doc_score'])} ({docs_result['grade']}) - {len(docs_result['issues'])} 个问题")

    overall_score = (
        max(0, 100 - len(security_result['issues']) * 15) +
        quality_result['quality_score'] +
        docs_result['doc_score']
    ) // 3

    print(f"\n🎯 总体评分：{format_score(overall_score)}")

    print(f"\n{'='*60}")
    print(f"[{timestamp()}] ✅ 所有测试完成!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
