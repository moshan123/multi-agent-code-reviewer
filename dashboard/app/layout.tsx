import React from 'react'
import ReactDOM from 'react-dom/client'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <head>
        <title>Multi-Agent 代码审查助手</title>
        <meta name="description" content="基于 MCP 的多 Agent 协作代码审查系统" />
      </head>
      <body>{children}</body>
    </html>
  )
}
