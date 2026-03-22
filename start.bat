@echo off
REM 快速启动脚本 (Windows)

echo 🚀 Multi-Agent 代码审查助手 - 启动脚本
echo.

REM 检查 Python 依赖
echo 📦 检查 Python 依赖...
python -c "import fastmcp" 2>nul
if errorlevel 1 (
    echo 安装 Python 依赖...
    pip install -r requirements.txt
)

REM 检查 Node 依赖
echo 📦 检查 Node 依赖...
if not exist "dashboard\node_modules" (
    echo 安装 Dashboard 依赖...
    cd dashboard
    call npm install
    cd ..
)

REM 启动 Dashboard
echo.
echo 🖥️ 启动 Dashboard...
cd dashboard
start cmd /k "npm run dev"
cd ..

echo.
echo ✅ 启动完成!
echo.
echo 📌 使用方法:
echo 1. 访问 http://localhost:3000
echo 2. 输入仓库名称和 PR 编号
echo 3. 点击'开始审查'
echo.
echo 或者使用命令行:
echo python agents\orchestrator.py --repo owner/repo --pr 123
echo.
