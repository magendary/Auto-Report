#!/bin/bash

# Auto-Report 启动脚本 / Startup Script
# 这个脚本用于启动后端和前端服务

# Trap SIGINT (Ctrl+C) to clean up processes
cleanup() {
    echo ""
    echo "正在停止服务... / Stopping services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup SIGINT

echo "========================================="
echo "Auto-Report 启动中... / Starting..."
echo "========================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装 / Error: Python3 not installed"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: Node.js 未安装 / Error: Node.js not installed"
    exit 1
fi

# 启动后端
echo ""
echo "1. 启动后端服务... / Starting backend service..."
cd backend

# Set development environment variables
export FLASK_DEBUG=True
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000

python3 app.py &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID) / Backend started (PID: $BACKEND_PID)"

# 等待后端启动
sleep 5

# 启动前端
echo ""
echo "2. 启动前端服务... / Starting frontend service..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID) / Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "========================================="
echo "服务已启动! / Services started!"
echo "========================================="
echo "后端API: http://localhost:5000 / Backend API"
echo "前端界面: http://localhost:3000 / Frontend UI"
echo ""
echo "按 Ctrl+C 停止所有服务 / Press Ctrl+C to stop all services"
echo "========================================="

# 等待用户中断
wait
