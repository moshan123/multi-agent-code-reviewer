import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { repo, pr_number } = body

    if (!repo || !pr_number) {
      return NextResponse.json(
        { error: '缺少必需参数' },
        { status: 400 }
      )
    }

    // 调用 Python Agent 进行审查
    const { spawn } = require('child_process')
    const path = require('path')

    const agentPath = path.join(process.cwd(), '../agents/orchestrator.py')

    // 模拟审查结果（实际应该调用 Python 脚本）
    // 这里为了演示返回模拟数据
    const mockResult = generateMockResult(repo, pr_number)

    return NextResponse.json(mockResult)

  } catch (error) {
    console.error('Review error:', error)
    return NextResponse.json(
      { error: '审查失败：' + (error as Error).message },
      { status: 500 }
    )
  }
}

function generateMockResult(repo: string, prNumber: number) {
  return {
    pr_info: {
      repo: repo,
      number: prNumber,
      title: `Demo PR #${prNumber}`,
      author: 'developer'
    },
    scores: {
      security: 85,
      quality: 78,
      documentation: 92,
      overall: 85
    },
    results: {
      security: {
        issues: [
          {
            type: 'potential_secret',
            severity: 'high',
            message: '可能包含敏感信息'
          }
        ],
        suggestions: ['使用环境变量管理敏感信息']
      },
      quality: {
        issues: [
          {
            type: 'long_lines',
            severity: 'low',
            message: '3 行代码超过 120 字符'
          },
          {
            type: 'debug_code',
            severity: 'medium',
            message: '发现调试代码：console.log'
          }
        ],
        suggestions: ['移除调试代码后再提交', '将长行拆分为多行']
      },
      documentation: {
        issues: [],
        suggestions: []
      }
    },
    summary: '## 📋 代码审查报告\n\n整体质量良好，注意修复安全问题。'
  }
}
