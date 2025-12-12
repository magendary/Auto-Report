# 使用指南 / User Guide

## 快速开始 / Quick Start

### 1. 安装依赖 / Install Dependencies

#### 后端 / Backend
```bash
cd backend
pip install -r requirements.txt
```

#### 前端 / Frontend
```bash
cd frontend
npm install
```

### 2. 启动服务 / Start Services

#### 方法1: 使用启动脚本 / Method 1: Using Startup Script
```bash
./start.sh
```

#### 方法2: 手动启动 / Method 2: Manual Startup

**启动后端 / Start Backend:**
```bash
cd backend
python app.py
```

**启动前端 / Start Frontend:**
```bash
cd frontend
npm run dev
```

### 3. 访问应用 / Access Application

- 前端界面 / Frontend UI: http://localhost:3000
- 后端API / Backend API: http://localhost:5000

## 功能说明 / Features

### 数据清洗 / Data Cleaning

系统会自动清洗以下5个数据源：
The system automatically cleans the following 5 data sources:

1. **Amazon销售数据** - 100条产品记录
2. **TikTok销售数据** - 500条产品记录
3. **TikTok视频评论** - 1,224条评论
4. **Amazon产品评论** - 1,634条评论
5. **TikTok店铺评论** - 8,915条评论

数据清洗包括：
Data cleaning includes:
- 处理缺失值 / Handle missing values
- 数据类型转换 / Data type conversion
- 异常值过滤 / Filter outliers
- 标准化数据格式 / Standardize data format

### 数据可视化 / Data Visualization

前端提供以下可视化图表：
Frontend provides the following visualizations:

- **柱状图** / Bar Charts: 显示热门类目分布
- **饼图** / Pie Charts: 展示评分分布
- **统计卡片** / Stat Cards: 关键指标概览

### PDF报告生成 / PDF Report Generation

点击"生成PDF报告"按钮，系统将：
Click "Generate PDF Report" button, the system will:

1. 整合所有清洗后的数据 / Consolidate all cleaned data
2. 生成数据可视化图表 / Generate data visualization charts
3. 创建专业的PDF报告 / Create professional PDF report
4. 提供下载链接 / Provide download link

报告包含以下章节：
Report includes the following sections:

- 执行摘要 / Executive Summary
- Amazon销售分析 / Amazon Sales Analysis
- TikTok销售分析 / TikTok Sales Analysis
- 产品评价分析 / Product Reviews Analysis
- 用户互动分析 / User Engagement Analysis
- 结论与建议 / Conclusions and Recommendations

## API使用 / API Usage

### 获取数据摘要 / Get Data Summary
```bash
curl http://localhost:5000/api/data/summary
```

### 生成报告 / Generate Report
```bash
curl -X POST http://localhost:5000/api/report/generate
```

### 下载报告 / Download Report
```bash
curl http://localhost:5000/api/report/download/<filename> -o report.pdf
```

## 技术架构 / Technical Architecture

### 后端架构 / Backend Architecture

```
Backend (Python)
├── data_cleaner.py      # 数据清洗核心逻辑
│   ├── DataCleaner      # 主清洗类
│   ├── clean_amazon_sales()
│   ├── clean_tiktok_sales()
│   ├── clean_reviews()
│   └── get_summary_statistics()
│
├── report_generator.py  # PDF报告生成
│   ├── ReportGenerator  # 报告生成类
│   ├── generate_report()
│   └── _create_chart()
│
└── app.py              # Flask REST API
    ├── /api/data/*     # 数据端点
    └── /api/report/*   # 报告端点
```

### 前端架构 / Frontend Architecture

```
Frontend (TypeScript + React)
├── App.tsx             # 主应用组件
│   ├── Dashboard       # 数据仪表盘
│   ├── Charts          # 图表可视化
│   └── ReportActions   # 报告操作
│
├── api.ts              # API客户端
│   ├── getSummary()
│   ├── generateReport()
│   └── downloadReport()
│
└── index.css           # 样式定义
```

## 常见问题 / FAQ

### Q: 如何更换数据源？
**A:** 将新的数据文件替换项目根目录下的对应文件，确保文件名和格式一致。

### Q: 报告生成失败怎么办？
**A:** 检查后端日志，确保所有数据文件都存在且格式正确。

### Q: 如何自定义报告格式？
**A:** 修改 `backend/report_generator.py` 中的 `generate_report()` 方法。

### Q: 前端无法连接后端？
**A:** 确保后端运行在 http://localhost:5000，或修改 `frontend/src/api.ts` 中的 API_BASE_URL。

## 扩展功能 / Extended Features

### 添加AI辅助分析 / Add AI-Assisted Analysis

在前端可以集成：
Can be integrated in frontend:
- OpenAI API 进行文本分析 / OpenAI API for text analysis
- 自然语言处理评论情感分析 / NLP sentiment analysis for reviews
- 自动生成市场洞察 / Auto-generate market insights

### 数据库集成 / Database Integration

可以添加数据库存储：
Can add database storage:
- PostgreSQL 存储历史数据 / PostgreSQL for historical data
- Redis 缓存API响应 / Redis for API response caching
- MongoDB 存储非结构化数据 / MongoDB for unstructured data

## 贡献指南 / Contributing

欢迎贡献代码和提出建议！
Contributions and suggestions are welcome!

1. Fork 项目 / Fork the project
2. 创建特性分支 / Create feature branch
3. 提交更改 / Commit changes
4. 推送到分支 / Push to branch
5. 创建 Pull Request / Create Pull Request

## 许可证 / License

ISC License
