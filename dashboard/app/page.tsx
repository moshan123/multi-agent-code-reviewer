'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Cpu,
  Zap,
  GitBranch,
  Terminal,
  Sparkles,
  Activity,
  Shield,
  FileCode,
  BookOpen,
  ArrowRight,
  Loader2,
  CheckCircle,
  AlertTriangle,
  Bug,
  TrendingUp,
  Code2,
  Eye,
  Clock,
  ChevronRight
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
    performance: number
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
    performance: {
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
  const [scanPhase, setScanPhase] = useState<'idle' | 'scanning' | 'complete'>('idle')
  const [activeAgents, setActiveAgents] = useState<string[]>([])

  // 粒子效果
  useEffect(() => {
    const container = document.querySelector('.cyber-bg__particles')
    if (!container) return

    for (let i = 0; i < 30; i++) {
      const particle = document.createElement('div')
      particle.className = 'particle'
      particle.style.left = Math.random() * 100 + '%'
      particle.style.animationDelay = Math.random() * 15 + 's'
      particle.style.animationDuration = (15 + Math.random() * 10) + 's'
      container.appendChild(particle)
    }
    return () => {
      container.querySelectorAll('.particle').forEach(p => p.remove())
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    setScanPhase('scanning')

    // 模拟 Agent 启动序列
    const agentSequence = ['Security', 'Quality', 'Docs', 'Performance']
    for (let i = 0; i < agentSequence.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 300))
      setActiveAgents(prev => [...prev, agentSequence[i]])
    }

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
      setScanPhase('complete')
    } catch (err) {
      setError(err instanceof Error ? err.message : '系统错误')
      setScanPhase('idle')
    } finally {
      setLoading(false)
      setActiveAgents([])
    }
  }

  const getScoreGradient = (score: number) => {
    if (score >= 90) return 'cyber-progress__fill--high'
    if (score >= 70) return 'cyber-progress__fill--medium'
    return 'cyber-progress__fill--low'
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-[#39ff14]'
    if (score >= 80) return 'text-[#00f5ff]'
    if (score >= 70) return 'text-[#fff01f]'
    return 'text-[#ff003c]'
  }

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: '#ff003c',
      high: '#ff4444',
      medium: '#fff01f',
      low: '#39ff14'
    }
    return colors[severity] || '#666'
  }

  return (
    <div className="relative min-h-screen">
      {/* 背景层 */}
      <div className="cyber-bg">
        <div className="cyber-bg__grid" />
        <div className="cyber-bg__particles" />
        <div className="cyber-bg__glow cyber-bg__glow--right" />
        <div className="cyber-bg__glow cyber-bg__glow--left" />
        <div className="cyber-bg__scanlines" />
      </div>

      {/* 主内容 */}
      <main className="relative z-10 flex items-center justify-center min-h-screen p-6 md:p-12">
        <div className="w-full max-w-5xl mx-auto space-y-8">
          {/* 头部 - HUD 风格 */}
          <header className="text-center space-y-6 py-8 animate-fade-in">
            <div className="inline-flex items-center gap-2 mb-4 cyber-badge">
              <Terminal className="w-4 h-4" />
              <span>SYSTEM ONLINE</span>
            </div>

            <h1 className="neon-title animate-slide-up">
              CODE REVIEW
              <br />
              COMMAND CENTER
            </h1>

            <p className="neon-subtitle animate-slide-up animate-delay-1">
              Multi-Agent AI-Powered Analysis
            </p>

            {/* Agent 状态指示器 */}
            <div className="flex flex-wrap justify-center gap-3 mt-8 animate-slide-up animate-delay-2">
              {['Security', 'Quality', 'Docs', 'Performance'].map((agent) => (
                <div
                  key={agent}
                  className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-all duration-500 ${
                    activeAgents.includes(agent)
                      ? 'bg-[#00f5ff]/10 border-[#00f5ff] text-[#00f5ff]'
                      : 'bg-white/5 border-white/10 text-gray-500'
                  }`}
                >
                  <div className={`w-2 h-2 rounded-full ${
                    activeAgents.includes(agent)
                      ? 'bg-[#00f5ff] animate-pulse'
                      : 'bg-gray-600'
                  }`} />
                  <span className="text-xs font-mono">{agent}</span>
                </div>
              ))}
            </div>
          </header>

          {/* 输入区域 */}
          <Card className="hud-card glass animate-scale-in animate-delay-3">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-[#00f5ff]/10 border border-[#00f5ff]/30">
                  <GitBranch className="w-6 h-6 text-[#00f5ff]" />
                </div>
                <div>
                  <CardTitle className="text-white text-xl">Initialize PR Scan</CardTitle>
                  <CardDescription className="text-gray-400 mt-1">
                    Enter repository and PR number to begin analysis
                  </CardDescription>
                </div>
                <div className="ml-auto">
                  <div className="hud-card__corner hud-card__corner--tl" />
                  <div className="hud-card__corner hud-card__corner--br" />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-mono text-gray-400 uppercase tracking-wider flex items-center gap-2">
                      <GitBranch className="w-3 h-3 text-[#00f5ff]" />
                      Repository
                    </label>
                    <Input
                      placeholder="owner/repo"
                      value={repo}
                      onChange={(e) => setRepo(e.target.value)}
                      required
                      className="cyber-input w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-mono text-gray-400 uppercase tracking-wider flex items-center gap-2">
                      <Code2 className="w-3 h-3 text-[#ff00ff]" />
                      PR Number
                    </label>
                    <Input
                      type="number"
                      placeholder="123"
                      value={prNumber}
                      onChange={(e) => setPrNumber(e.target.value)}
                      required
                      className="cyber-input w-full"
                    />
                  </div>
                </div>
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full cyber-button cyber-button--primary h-14 text-base"
                >
                  {loading ? (
                    <>
                      <div className="cyber-loader" />
                      <span>Running Multi-Agent Scan...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      <span>Initialize Scan Sequence</span>
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* 错误显示 */}
          {error && (
            <Card className="hud-card glass border-[#ff003c]/30 bg-[#ff003c]/5 animate-slide-up">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3 text-[#ff003c]">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="font-mono">{error}</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 结果展示 */}
          {result && (
            <div className="space-y-6 animate-slide-up">
              {/* PR 信息卡片 */}
              <Card className="hud-card glass">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className="cyber-badge cyber-badge--success">
                          <CheckCircle className="w-3 h-3" />
                          SCAN COMPLETE
                        </Badge>
                      </div>
                      <CardTitle className="text-white text-2xl">{result.pr_info.title}</CardTitle>
                      <CardDescription className="flex items-center gap-3 mt-3 text-gray-400 font-mono text-sm">
                        <GitBranch className="w-4 h-4" />
                        <span>{result.pr_info.repo}</span>
                        <span className="text-[#00f5ff]">#{result.pr_info.number}</span>
                      </CardDescription>
                    </div>
                    <div className="text-right">
                      <div className="text-5xl font-bold bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] bg-clip-text text-transparent">
                        {result.scores.overall}
                      </div>
                      <div className="text-xs text-gray-500 uppercase tracking-wider mt-1">Overall Score</div>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* 评分仪表板 */}
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                <ScoreCard
                  icon={Shield}
                  title="Security"
                  score={result.scores.security}
                  color="#00f5ff"
                />
                <ScoreCard
                  icon={FileCode}
                  title="Quality"
                  score={result.scores.quality}
                  color="#ff00ff"
                />
                <ScoreCard
                  icon={BookOpen}
                  title="Documentation"
                  score={result.scores.documentation}
                  color="#39ff14"
                />
                <ScoreCard
                  icon={Zap}
                  title="Performance"
                  score={result.scores.performance}
                  color="#fff01f"
                />
              </div>

              {/* 问题列表 */}
              <div className="grid lg:grid-cols-3 gap-4">
                <IssuesCard
                  title="Security Issues"
                  icon={Shield}
                  iconColor="#00f5ff"
                  issues={result.results.security.issues}
                />
                <IssuesCard
                  title="Code Quality"
                  icon={FileCode}
                  iconColor="#ff00ff"
                  issues={result.results.quality.issues}
                />
                <IssuesCard
                  title="Performance"
                  icon={Zap}
                  iconColor="#fff01f"
                  issues={result.results.performance.issues}
                />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

// 评分卡片组件
function ScoreCard({ icon: Icon, title, score, color }: {
  icon: any
  title: string
  score: number
  color: string
}) {
  return (
    <Card className="hud-card glass">
      <CardContent className="pt-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="p-2.5 rounded-lg"
              style={{ background: `${color}15`, border: `1px solid ${color}40` }}
            >
              <Icon className="w-5 h-5" style={{ color }} />
            </div>
            <span className="text-sm text-gray-400 font-mono">{title}</span>
          </div>
        </div>
        <div className="space-y-2">
          <div className="text-4xl font-bold" style={{ color }}>
            {score}
          </div>
          <div className="cyber-progress">
            <div
              className={`cyber-progress__fill ${getScoreGradientClass(score)}`}
              style={{ width: `${score}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// 问题列表卡片
function IssuesCard({ title, icon: Icon, iconColor, issues }: {
  title: string
  icon: any
  iconColor: string
  issues: Array<{ type: string; severity: string; message: string }>
}) {
  return (
    <Card className="hud-card glass">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <div
            className="p-2 rounded-lg"
            style={{ background: `${iconColor}15`, border: `1px solid ${iconColor}40` }}
          >
            <Icon className="w-5 h-5" style={{ color: iconColor }} />
          </div>
          <CardTitle className="text-white text-base">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {issues.length === 0 ? (
          <div className="flex items-center gap-2 text-[#39ff14] p-3 rounded-lg bg-[#39ff14]/5">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm">No issues detected</span>
          </div>
        ) : (
          <div className="space-y-2">
            {issues.slice(0, 5).map((issue, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-2.5 rounded-lg hover:bg-white/5 transition-colors"
              >
                <div
                  className="w-2 h-2 rounded-full mt-1.5"
                  style={{
                    backgroundColor: getSeverityColor(issue.severity),
                    boxShadow: `0 0 10px ${getSeverityColor(issue.severity)}`
                  }}
                />
                <span className="text-sm text-gray-300">{issue.message}</span>
              </div>
            ))}
            {issues.length > 5 && (
              <div className="text-center py-2 text-xs text-gray-500">
                +{issues.length - 5} more issues
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function getScoreGradientClass(score: number) {
  if (score >= 90) return 'cyber-progress__fill--high'
  if (score >= 70) return 'cyber-progress__fill--medium'
  return 'cyber-progress__fill--low'
}

function getSeverityColor(severity: string) {
  const colors: Record<string, string> = {
    critical: '#ff003c',
    high: '#ff4444',
    medium: '#fff01f',
    low: '#39ff14'
  }
  return colors[severity] || '#666'
}
