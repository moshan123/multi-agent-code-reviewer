'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { AlertCircle, CheckCircle, Shield, FileCode, BookOpen, ArrowRight, Loader2 } from 'lucide-react'

interface ReviewResult {
  pr_info: {
    repo: string
    number: number
    title: string
    author: string
  }
  scores: {
    security: number
    quality: number
    documentation: number
    overall: number
  }
  results: {
    security: {
      issues: Array<{ type: string; severity: string; message: string }>
      suggestions: string[]
    }
    quality: {
      issues: Array<{ type: string; severity: string; message: string }>
      suggestions: string[]
    }
    documentation: {
      issues: Array<{ type: string; severity: string; message: string }>
      suggestions: string[]
    }
  }
  summary: string
}

export default function Home() {
  const [repo, setRepo] = useState('')
  const [prNumber, setPrNumber] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ReviewResult | null>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('/api/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo, pr_number: parseInt(prNumber) })
      })

      if (!response.ok) {
        throw new Error('审查失败')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '发生未知错误')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 80) return 'text-emerald-600'
    if (score >= 70) return 'text-yellow-600'
    if (score >= 60) return 'text-orange-600'
    return 'text-red-600'
  }

  const getScoreBadge = (score: number) => {
    if (score >= 90) return '🌟'
    if (score >= 80) return '✅'
    if (score >= 70) return '⚠️'
    if (score >= 60) return '❗'
    return '🚨'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-600'
      case 'high': return 'bg-red-500'
      case 'medium': return 'bg-yellow-500'
      case 'low': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">
            🤖 Multi-Agent 代码审查助手
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            基于 MCP 的多 Agent 协作系统，自动化代码审查和质量管理
          </p>
        </div>

        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>审查 GitHub PR</CardTitle>
            <CardDescription>
              输入仓库名称和 PR 编号，启动多 Agent 协作审查
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">仓库全名</label>
                  <Input
                    placeholder="owner/repo"
                    value={repo}
                    onChange={(e) => setRepo(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">PR 编号</label>
                  <Input
                    type="number"
                    placeholder="123"
                    value={prNumber}
                    onChange={(e) => setPrNumber(e.target.value)}
                    required
                  />
                </div>
              </div>
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    正在审查...
                  </>
                ) : (
                  <>
                    开始审查
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Card className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950">
            <CardHeader>
              <CardTitle className="flex items-center text-red-600 dark:text-red-400">
                <AlertCircle className="mr-2 h-5 w-5" />
                错误
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* PR Info */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{result.pr_info.title}</CardTitle>
                    <CardDescription className="flex items-center gap-2 mt-1">
                      <span>{result.pr_info.repo}</span>
                      <span>•</span>
                      <span>PR #{result.pr_info.number}</span>
                      <span>•</span>
                      <span>作者：{result.pr_info.author}</span>
                    </CardDescription>
                  </div>
                  <Badge variant="secondary">审查完成</Badge>
                </div>
              </CardHeader>
            </Card>

            {/* Scores Overview */}
            <div className="grid grid-cols-4 gap-4">
              <ScoreCard
                icon={Shield}
                title="安全"
                score={result.scores.security}
                badge={getScoreBadge(result.scores.security)}
                color={getScoreColor(result.scores.security)}
              />
              <ScoreCard
                icon={FileCode}
                title="质量"
                score={result.scores.quality}
                badge={getScoreBadge(result.scores.quality)}
                color={getScoreColor(result.scores.quality)}
              />
              <ScoreCard
                icon={BookOpen}
                title="文档"
                score={result.scores.documentation}
                badge={getScoreBadge(result.scores.documentation)}
                color={getScoreColor(result.scores.documentation)}
              />
              <ScoreCard
                icon={CheckCircle}
                title="总体"
                score={result.scores.overall}
                badge={getScoreBadge(result.scores.overall)}
                color={getScoreColor(result.scores.overall)}
              />
            </div>

            {/* Issues */}
            <div className="grid grid-cols-3 gap-4">
              <IssuesCard
                title="🔒 安全问题"
                issues={result.results.security.issues}
                suggestions={result.results.security.suggestions}
              />
              <IssuesCard
                title="💎 代码质量"
                issues={result.results.quality.issues}
                suggestions={result.results.quality.suggestions}
              />
              <IssuesCard
                title="📖 文档"
                issues={result.results.documentation.issues}
                suggestions={result.results.documentation.suggestions}
              />
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

function ScoreCard({ icon: Icon, title, score, badge, color }: {
  icon: any
  title: string
  score: number
  badge: string
  color: string
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon className="h-5 w-5 text-gray-500" />
              <span className="text-sm font-medium">{title}</span>
            </div>
            <span className="text-2xl">{badge}</span>
          </div>
          <div className={`text-3xl font-bold ${color}`}>
            {score}
          </div>
          <Progress value={score} className="h-2" />
        </div>
      </CardContent>
    </Card>
  )
}

function IssuesCard({ title, issues, suggestions }: {
  title: string
  issues: Array<{ type: string; severity: string; message: string }>
  suggestions: string[]
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {issues.length === 0 ? (
          <p className="text-sm text-green-600">✅ 未发现问题</p>
        ) : (
          <div className="space-y-2">
            {issues.slice(0, 5).map((issue, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className={`w-2 h-2 rounded-full mt-1.5 ${getSeverityColor(issue.severity)}`} />
                <span className="text-gray-700 dark:text-gray-300">{issue.message}</span>
              </div>
            ))}
            {issues.length > 5 && (
              <p className="text-xs text-gray-500">还有 {issues.length - 5} 个问题...</p>
            )}
          </div>
        )}
        {suggestions.length > 0 && (
          <div className="pt-3 border-t">
            <p className="text-xs font-medium text-gray-500 mb-2">💡 建议</p>
            <ul className="space-y-1">
              {suggestions.slice(0, 3).map((s, i) => (
                <li key={i} className="text-xs text-gray-600 dark:text-gray-400">• {s}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function getSeverityColor(severity: string) {
  switch (severity) {
    case 'critical': return 'bg-red-600'
    case 'high': return 'bg-red-500'
    case 'medium': return 'bg-yellow-500'
    case 'low': return 'bg-green-500'
    default: return 'bg-gray-500'
  }
}
