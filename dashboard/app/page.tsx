'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  AlertCircle,
  CheckCircle,
  Shield,
  FileCode,
  BookOpen,
  ArrowRight,
  Loader2,
  Cpu,
  Zap,
  GitBranch,
  Terminal,
  Sparkles,
  Activity
} from 'lucide-react'

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
  const [agents, setAgents] = useState([
    { name: 'Security', status: 'idle', color: 'cyan' },
    { name: 'Quality', status: 'idle', color: 'purple' },
    { name: 'Docs', status: 'idle', color: 'green' }
  ])

  // 粒子效果
  useEffect(() => {
    const container = document.body
    for (let i = 0; i < 20; i++) {
      const particle = document.createElement('div')
      particle.className = 'particle'
      particle.style.left = Math.random() * 100 + 'vw'
      particle.style.animationDelay = Math.random() * 15 + 's'
      particle.style.animationDuration = (15 + Math.random() * 10) + 's'
      container.appendChild(particle)
    }
    return () => {
      document.querySelectorAll('.particle').forEach(p => p.remove())
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    // 模拟 Agent 启动效果
    setAgents(agents.map(a => ({ ...a, status: 'running' })))

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
      setAgents(agents.map(a => ({ ...a, status: 'complete' })))
    } catch (err) {
      setError(err instanceof Error ? err.message : '发生未知错误')
      setAgents(agents.map(a => ({ ...a, status: 'error' })))
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-[#0aff0a]'
    if (score >= 80) return 'text-[#00f0ff]'
    if (score >= 70) return 'text-[#fff01f]'
    if (score >= 60) return 'text-[#ff8800]'
    return 'text-[#ff003c]'
  }

  const getScoreGradient = (score: number) => {
    if (score >= 90) return 'from-[#0aff0a] to-[#00ff88]'
    if (score >= 80) return 'from-[#00f0ff] to-[#00ff88]'
    if (score >= 70) return 'from-[#fff01f] to-[#ff8800]'
    return 'from-[#ff003c] to-[#ff8800]'
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
      case 'critical': return 'bg-[#ff003c]'
      case 'high': return 'bg-[#ff4444]'
      case 'medium': return 'bg-[#fff01f]'
      case 'low': return 'bg-[#0aff0a]'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="relative min-h-screen">
      {/* 背景效果 */}
      <div className="cyber-grid" />
      <div className="cyber-glow" />

      <main className="relative z-10 p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header - 科技感标题 */}
          <div className="text-center space-y-6 py-8">
            <div className="inline-flex items-center gap-3 mb-4">
              <div className="relative">
                <Cpu className="w-16 h-16 text-[#6366f1] neon-text" />
                <div className="absolute inset-0 animate-ping">
                  <Cpu className="w-16 h-16 text-[#6366f1] opacity-20" />
                </div>
              </div>
            </div>

            <h1 className="text-6xl font-bold gradient-text neon-text">
              Multi-Agent 代码审查助手
            </h1>

            <div className="flex items-center justify-center gap-4 text-[#6b6b8d]">
              <span className="flex items-center gap-2">
                <Terminal className="w-4 h-4" />
                基于 MCP 协议
              </span>
              <span className="text-[#2a2a3e]">●</span>
              <span className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                多 Agent 协作
              </span>
              <span className="text-[#2a2a3e]">●</span>
              <span className="flex items-center gap-2">
                <Activity className="w-4 h-4" />
                实时审查
              </span>
            </div>
          </div>

          {/* Agent 状态指示器 */}
          <div className="flex justify-center gap-4">
            {agents.map((agent) => (
              <div
                key={agent.name}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#1a1a25] border border-[#2a2a3e]"
              >
                <div className={`status-indicator ${
                  agent.status === 'running' ? 'running' :
                  agent.status === 'complete' ? 'running' :
                  agent.status === 'error' ? 'error' : ''
                }`} />
                <span className="text-sm text-[#a0a0c0]">{agent.name} Agent</span>
              </div>
            ))}
          </div>

          {/* 输入表单 - 科技感卡片 */}
          <Card className="neon-border cyber-card bg-[#12121a]/80 backdrop-blur border-[#2a2a3e]">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-[#1a1a25] border border-[#2a2a3e]">
                  <GitBranch className="w-6 h-6 text-[#00f0ff]" />
                </div>
                <div>
                  <CardTitle className="text-[#e0e0ff] text-xl">审查 GitHub PR</CardTitle>
                  <CardDescription className="text-[#6b6b8d] mt-1">
                    输入仓库名称和 PR 编号，启动多 Agent 协作审查
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <label className="text-sm font-medium text-[#a0a0c0] flex items-center gap-2">
                      <GitBranch className="w-4 h-4 text-[#00f0ff]" />
                      仓库全名
                    </label>
                    <Input
                      placeholder="owner/repo"
                      value={repo}
                      onChange={(e) => setRepo(e.target.value)}
                      required
                      className="cyber-input bg-[#0a0a0f] border-[#2a2a3e] text-[#e0e0ff] placeholder:text-[#4a4a5e]"
                    />
                  </div>
                  <div className="space-y-3">
                    <label className="text-sm font-medium text-[#a0a0c0] flex items-center gap-2">
                      <FileCode className="w-4 h-4 text-[#bc13fe]" />
                      PR 编号
                    </label>
                    <Input
                      type="number"
                      placeholder="123"
                      value={prNumber}
                      onChange={(e) => setPrNumber(e.target.value)}
                      required
                      className="cyber-input bg-[#0a0a0f] border-[#2a2a3e] text-[#e0e0ff] placeholder:text-[#4a4a5e]"
                    />
                  </div>
                </div>
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full cyber-button h-12 text-lg bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] hover:from-[#6366f1]/90 hover:to-[#8b5cf6]/90 border-0"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      <span className="gradient-text">Multi-Agent 审查中...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-5 w-5" />
                      启动审查
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Error Display */}
          {error && (
            <Card className="neon-border bg-[#2a0a0a]/80 backdrop-blur border-[#ff003c]/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-[#ff4444]">
                  <AlertCircle className="w-5 h-5" />
                  错误
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[#ff6666]">{error}</p>
              </CardContent>
            </Card>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-8">
              {/* PR Info */}
              <Card className="neon-border cyber-card bg-[#12121a]/80 backdrop-blur border-[#2a2a3e]">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-[#e0e0ff] text-xl">{result.pr_info.title}</CardTitle>
                      <CardDescription className="flex items-center gap-3 mt-2 text-[#6b6b8d]">
                        <GitBranch className="w-4 h-4" />
                        <span>{result.pr_info.repo}</span>
                        <span className="text-[#2a2a3e]">●</span>
                        <span className="text-[#6366f1]">#{result.pr_info.number}</span>
                        <span className="text-[#2a2a3e]">●</span>
                        <span>{result.pr_info.author}</span>
                      </CardDescription>
                    </div>
                    <Badge className="bg-gradient-to-r from-[#0aff0a] to-[#00ff88] text-[#0a0a0f] font-bold border-0">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      审查完成
                    </Badge>
                  </div>
                </CardHeader>
              </Card>

              {/* Scores Overview - 霓虹评分卡 */}
              <div className="grid grid-cols-4 gap-4">
                <ScoreCard
                  icon={Shield}
                  title="安全"
                  score={result.scores.security}
                  badge={getScoreBadge(result.scores.security)}
                  color={getScoreColor(result.scores.security)}
                  gradient={getScoreGradient(result.scores.security)}
                />
                <ScoreCard
                  icon={FileCode}
                  title="质量"
                  score={result.scores.quality}
                  badge={getScoreBadge(result.scores.quality)}
                  color={getScoreColor(result.scores.quality)}
                  gradient={getScoreGradient(result.scores.quality)}
                />
                <ScoreCard
                  icon={BookOpen}
                  title="文档"
                  score={result.scores.documentation}
                  badge={getScoreBadge(result.scores.documentation)}
                  color={getScoreColor(result.scores.documentation)}
                  gradient={getScoreGradient(result.scores.documentation)}
                />
                <ScoreCard
                  icon={Cpu}
                  title="总体"
                  score={result.scores.overall}
                  badge={getScoreBadge(result.scores.overall)}
                  color={getScoreColor(result.scores.overall)}
                  gradient={getScoreGradient(result.scores.overall)}
                />
              </div>

              {/* Issues - 问题列表 */}
              <div className="grid grid-cols-3 gap-4">
                <IssuesCard
                  title="安全审查"
                  icon={Shield}
                  iconColor="text-[#00f0ff]"
                  issues={result.results.security.issues}
                  suggestions={result.results.security.suggestions}
                />
                <IssuesCard
                  title="代码质量"
                  icon={FileCode}
                  iconColor="text-[#bc13fe]"
                  issues={result.results.quality.issues}
                  suggestions={result.results.quality.suggestions}
                />
                <IssuesCard
                  title="文档规范"
                  icon={BookOpen}
                  iconColor="text-[#0aff0a]"
                  issues={result.results.documentation.issues}
                  suggestions={result.results.documentation.suggestions}
                />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

function ScoreCard({ icon: Icon, title, score, badge, color, gradient }: {
  icon: any
  title: string
  score: number
  badge: string
  color: string
  gradient: string
}) {
  return (
    <Card className="neon-border cyber-card bg-[#12121a]/80 backdrop-blur border-[#2a2a3e]">
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-[#1a1a25] border border-[#2a2a3e]">
                <Icon className={`h-5 w-5 ${color}`} />
              </div>
              <span className="text-sm font-medium text-[#a0a0c0]">{title}</span>
            </div>
            <span className="text-2xl">{badge}</span>
          </div>
          <div className={`text-4xl font-bold bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
            {score}
          </div>
          <div className="relative">
            <Progress value={score} className="h-3 progress-glow bg-[#1a1a25]" />
            <div
              className={`absolute top-0 left-0 h-full bg-gradient-to-r ${gradient} rounded-full transition-all duration-500`}
              style={{ width: `${score}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function IssuesCard({ title, icon: Icon, iconColor, issues, suggestions }: {
  title: string
  icon: any
  iconColor: string
  issues: Array<{ type: string; severity: string; message: string }>
  suggestions: string[]
}) {
  return (
    <Card className="neon-border cyber-card bg-[#12121a]/80 backdrop-blur border-[#2a2a3e] scan-line">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className={`p-2 rounded-lg bg-[#1a1a25] border border-[#2a2a3e]`}>
            <Icon className={`w-5 h-5 ${iconColor}`} />
          </div>
          <CardTitle className="text-[#e0e0ff] text-base">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {issues.length === 0 ? (
          <div className="flex items-center gap-2 text-[#0aff0a] p-3 rounded-lg bg-[#0a1a0a]/50 border border-[#0aff0a]/20">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm">未发现任何问题</span>
          </div>
        ) : (
          <div className="space-y-2">
            {issues.slice(0, 5).map((issue, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-2 rounded-lg hover:bg-[#1a1a25] transition-colors"
              >
                <span className={`w-2 h-2 rounded-full mt-1.5 ${getSeverityColor(issue.severity)}`}
                  style={{ boxShadow: `0 0 10px currentColor` }}
                />
                <span className="text-sm text-[#a0a0c0]">{issue.message}</span>
              </div>
            ))}
            {issues.length > 5 && (
              <p className="text-xs text-[#4a4a5e] text-center py-2">
                还有 {issues.length - 5} 个问题...
              </p>
            )}
          </div>
        )}
        {suggestions.length > 0 && (
          <div className="pt-3 border-t border-[#2a2a3e]">
            <div className="flex items-center gap-2 mb-2 text-[#bc13fe]">
              <Zap className="w-3 h-3" />
              <span className="text-xs font-medium">改进建议</span>
            </div>
            <ul className="space-y-1">
              {suggestions.slice(0, 3).map((s, i) => (
                <li key={i} className="text-xs text-[#6b6b8d] flex items-start gap-2">
                  <span className="text-[#bc13fe]">▹</span>
                  {s}
                </li>
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
    case 'critical': return 'bg-[#ff003c]'
    case 'high': return 'bg-[#ff4444]'
    case 'medium': return 'bg-[#fff01f]'
    case 'low': return 'bg-[#0aff0a]'
    default: return 'bg-gray-500'
  }
}
