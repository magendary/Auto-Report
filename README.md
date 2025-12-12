# Auto-Report - 跨境电商市场分析系统

Cross-border e-commerce market analysis workflow application.

## 概述 / Overview

这是一个跨境电商数据分析系统，使用Python后端进行数据清洗，TypeScript前端提供数据可视化和报告生成功能。

This is a cross-border e-commerce data analysis system that uses a Python backend for data cleaning and a TypeScript frontend for data visualization and report generation.

## 功能特性 / Features

- ✅ **数据清洗** / Data Cleaning: 自动清洗5个数据源（Amazon销售、TikTok销售、视频评论、产品评论）
- 📊 **数据可视化** / Data Visualization: 使用Recharts展示销售和评论数据
- 📄 **PDF报告生成** / PDF Report Generation: 自动生成专业的分析报告
- 🎨 **现代UI界面** / Modern UI: 基于React和TypeScript的响应式界面
- 🔄 **REST API** / REST API: Flask后端提供数据访问接口

## 系统架构 / System Architecture

```
Auto-Report/
├── backend/                 # Python后端 / Python Backend
│   ├── data_cleaner.py     # 数据清洗模块 / Data cleaning module
│   ├── report_generator.py # 报告生成模块 / Report generation module
│   ├── app.py              # Flask API服务 / Flask API server
│   └── requirements.txt    # Python依赖 / Python dependencies
│
├── frontend/               # TypeScript前端 / TypeScript Frontend
│   ├── src/
│   │   ├── App.tsx        # 主应用组件 / Main app component
│   │   ├── api.ts         # API客户端 / API client
│   │   ├── main.tsx       # 应用入口 / App entry
│   │   └── index.css      # 样式文件 / Styles
│   ├── package.json       # NPM依赖 / NPM dependencies
│   └── vite.config.ts     # Vite配置 / Vite config
│
└── data files/            # 数据文件 / Data files
    ├── 1. amazon销售.xlsx
    ├── 1. tk销售.xlsx
    ├── 2. tk视频评论.csv
    ├── 3. amazon商品评论.xlsx
    └── 3.tiktok店铺评论.xlsx
```

## 安装和使用 / Installation and Usage

### 后端安装 / Backend Setup

```bash
# 进入后端目录 / Navigate to backend directory
cd backend

# 安装Python依赖 / Install Python dependencies
pip install -r requirements.txt

# 启动Flask服务器 / Start Flask server
python app.py
```

后端服务将在 `http://localhost:5000` 运行
Backend server will run at `http://localhost:5000`

### 前端安装 / Frontend Setup

```bash
# 进入前端目录 / Navigate to frontend directory
cd frontend

# 安装依赖 / Install dependencies
npm install

# 启动开发服务器 / Start development server
npm run dev
```

前端应用将在 `http://localhost:3000` 运行
Frontend app will run at `http://localhost:3000`

## API端点 / API Endpoints

- `GET /api/health` - 健康检查 / Health check
- `GET /api/data/summary` - 获取数据摘要 / Get data summary
- `GET /api/data/amazon-sales` - 获取Amazon销售数据 / Get Amazon sales data
- `GET /api/data/tiktok-sales` - 获取TikTok销售数据 / Get TikTok sales data
- `GET /api/data/amazon-reviews` - 获取Amazon评论数据 / Get Amazon reviews
- `GET /api/data/tiktok-reviews` - 获取TikTok评论数据 / Get TikTok reviews
- `GET /api/data/video-comments` - 获取视频评论数据 / Get video comments
- `POST /api/report/generate` - 生成PDF报告 / Generate PDF report
- `GET /api/report/download/<filename>` - 下载报告 / Download report
- `GET /api/report/list` - 列出所有报告 / List all reports

## 数据源 / Data Sources

系统处理以下5个数据文件：
The system processes the following 5 data files:

1. **Amazon销售数据** / Amazon Sales Data (`1. amazon销售.xlsx`)
   - 包含100个产品的销售信息、评分、价格等
   - Contains sales info, ratings, prices for 100 products

2. **TikTok销售数据** / TikTok Sales Data (`1. tk销售.xlsx`)
   - 包含500个产品的TikTok销售信息
   - Contains TikTok sales info for 500 products

3. **TikTok视频评论** / TikTok Video Comments (`2. tk视频评论.csv`)
   - 包含1224条视频评论和互动数据
   - Contains 1224 video comments and engagement data

4. **Amazon产品评论** / Amazon Product Reviews (`3. amazon商品评论.xlsx`)
   - 包含1634条产品评论
   - Contains 1634 product reviews

5. **TikTok店铺评论** / TikTok Shop Reviews (`3.tiktok店铺评论.xlsx`)
   - 包含8915条店铺评论
   - Contains 8915 shop reviews

## 报告内容 / Report Contents

生成的PDF报告包含以下部分：
The generated PDF report includes:

- 📋 执行摘要 / Executive Summary
- 📊 Amazon销售数据分析 / Amazon Sales Analysis
- 🛍️ TikTok销售数据分析 / TikTok Sales Analysis
- ⭐ 产品评价分析 / Product Reviews Analysis
- 💬 用户互动分析 / User Engagement Analysis
- 📈 数据可视化图表 / Data Visualization Charts
- 💡 结论与建议 / Conclusions and Recommendations

## 技术栈 / Tech Stack

### 后端 / Backend
- Python 3.12
- Flask (Web框架 / Web framework)
- Pandas (数据处理 / Data processing)
- ReportLab (PDF生成 / PDF generation)
- Matplotlib (图表生成 / Chart generation)

### 前端 / Frontend
- TypeScript
- React 18
- Vite (构建工具 / Build tool)
- Recharts (数据可视化 / Data visualization)
- Axios (HTTP客户端 / HTTP client)

## 开发者 / Developers

本项目由Auto-Report团队开发维护。
This project is developed and maintained by the Auto-Report team.

## 许可证 / License

ISC