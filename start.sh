#!/bin/bash
# 快速启动脚本

echo "🚀 Multi-Agent 代码审查助手 - 启动脚本"
echo ""

# 检查 Python 依赖
echo "📦 检查 Python 依赖..."
if ! python3 -c "import fastmcp" 2>/dev/null; then
    echo "安装 Python 依赖..."
    pip install -r requirements.txt
fi

# 检查 Node 依赖
echo "📦 检查 Node 依赖..."
if [ ! -d "dashboard/node_modules" ]; then
    echo "安装 Dashboard 依赖..."
    cd dashboard && npm install && cd ..
fi

# 启动 Dashboard
echo ""
echo "🖥️ 启动 Dashboard..."
cd dashboard
npm run dev &
DASHBOARD_PID=$!
cd ..

# 等待 Dashboard 启动
sleep 3

echo ""
echo "✅ 启动完成!"
echo ""
echo "📌 使用方法:"
echo "1. 访问 http://localhost:3000"
echo "2. 输入仓库名称和 PR 编号"
echo "3. 点击'开始审查'"
echo ""
echo "或者使用命令行:"
echo "python agents/orchestrator.py --repo owner/repo --pr 123"
echo ""

# 等待进程
wait $DASHBOARD_PID
