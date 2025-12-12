import { useState, useEffect } from 'react';
import { api, SummaryData } from './api';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];
const MAX_CATEGORY_NAME_LENGTH = 20;
const MAX_TIKTOK_CATEGORY_NAME_LENGTH = 30;

function App() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [reportFilename, setReportFilename] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getSummary();
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setGenerating(true);
      setError(null);
      setSuccessMessage(null);
      const filename = await api.generateReport();
      setReportFilename(filename);
      setSuccessMessage('报告生成成功！Report generated successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadReport = () => {
    if (reportFilename) {
      api.downloadReport(reportFilename);
    }
  };

  if (loading) {
    return <div className="loading">加载数据中... Loading data...</div>;
  }

  if (error && !summary) {
    return (
      <div className="container">
        <div className="error">
          <h2>错误 / Error</h2>
          <p>{error}</p>
          <button className="button" onClick={loadData} style={{ marginTop: '10px' }}>
            重试 / Retry
          </button>
        </div>
      </div>
    );
  }

  if (!summary) {
    return <div className="loading">无数据 / No data available</div>;
  }

  // Prepare chart data
  const amazonCategoriesData = summary.amazon_sales?.top_categories
    ? Object.entries(summary.amazon_sales.top_categories).map(([name, value]) => ({
        name: name.substring(0, MAX_CATEGORY_NAME_LENGTH) + (name.length > MAX_CATEGORY_NAME_LENGTH ? '...' : ''),
        value
      }))
    : [];

  const tiktokCategoriesData = summary.tiktok_sales?.top_categories
    ? Object.entries(summary.tiktok_sales.top_categories).map(([name, value]) => ({
        name: name.substring(0, MAX_TIKTOK_CATEGORY_NAME_LENGTH) + (name.length > MAX_TIKTOK_CATEGORY_NAME_LENGTH ? '...' : ''),
        value
      }))
    : [];

  const amazonRatingData = summary.amazon_reviews?.rating_distribution
    ? Object.entries(summary.amazon_reviews.rating_distribution).map(([rating, count]) => ({
        rating: `${rating}星`,
        count
      }))
    : [];

  const tiktokRatingData = summary.tiktok_shop_reviews?.rating_distribution
    ? Object.entries(summary.tiktok_shop_reviews.rating_distribution).map(([rating, count]) => ({
        rating: `${rating}星`,
        count
      }))
    : [];

  return (
    <div className="container">
      <div className="header">
        <h1>🚀 Auto-Report 跨境电商分析系统</h1>
        <p>Cross-Border E-Commerce Market Analysis System</p>
      </div>

      {error && (
        <div className="error">
          <strong>错误 / Error:</strong> {error}
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          <span>{successMessage}</span>
          {reportFilename && (
            <button className="button" onClick={handleDownloadReport}>
              下载报告 / Download Report
            </button>
          )}
        </div>
      )}

      <div className="stats-grid">
        {summary.amazon_sales && (
          <>
            <div className="stat-card">
              <h3>Amazon 产品数量</h3>
              <div className="value">{summary.amazon_sales.total_products}</div>
              <div className="label">Total Products</div>
            </div>
            <div className="stat-card">
              <h3>Amazon 月销量</h3>
              <div className="value">{summary.amazon_sales.total_monthly_sales.toLocaleString()}</div>
              <div className="label">Monthly Sales</div>
            </div>
            <div className="stat-card">
              <h3>Amazon 月销售额</h3>
              <div className="value">${summary.amazon_sales.total_monthly_revenue.toLocaleString()}</div>
              <div className="label">Monthly Revenue</div>
            </div>
            <div className="stat-card">
              <h3>Amazon 平均评分</h3>
              <div className="value">{summary.amazon_sales.avg_rating.toFixed(2)}</div>
              <div className="label">Average Rating</div>
            </div>
          </>
        )}
        {summary.tiktok_sales && (
          <>
            <div className="stat-card">
              <h3>TikTok 产品数量</h3>
              <div className="value">{summary.tiktok_sales.total_products}</div>
              <div className="label">Total Products</div>
            </div>
            <div className="stat-card">
              <h3>TikTok 总销量</h3>
              <div className="value">{summary.tiktok_sales.total_sales_volume.toLocaleString()}</div>
              <div className="label">Total Sales Volume</div>
            </div>
            <div className="stat-card">
              <h3>TikTok 总销售额</h3>
              <div className="value">${summary.tiktok_sales.total_revenue.toLocaleString()}</div>
              <div className="label">Total Revenue</div>
            </div>
          </>
        )}
        {summary.amazon_reviews && (
          <div className="stat-card">
            <h3>Amazon 评论数</h3>
            <div className="value">{summary.amazon_reviews.total_reviews.toLocaleString()}</div>
            <div className="label">Total Reviews</div>
          </div>
        )}
        {summary.tiktok_shop_reviews && (
          <div className="stat-card">
            <h3>TikTok 评论数</h3>
            <div className="value">{summary.tiktok_shop_reviews.total_reviews.toLocaleString()}</div>
            <div className="label">Total Reviews</div>
          </div>
        )}
        {summary.tiktok_video_comments && (
          <div className="stat-card">
            <h3>视频评论数</h3>
            <div className="value">{summary.tiktok_video_comments.total_comments.toLocaleString()}</div>
            <div className="label">Video Comments</div>
          </div>
        )}
      </div>

      {amazonCategoriesData.length > 0 && (
        <div className="chart-section">
          <h2>📊 Amazon 热门类目分布 / Top Categories</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={amazonCategoriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#667eea" name="产品数量 / Products" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {tiktokCategoriesData.length > 0 && (
        <div className="chart-section">
          <h2>📊 TikTok 热门类目分布 / Top Categories</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={tiktokCategoriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={120} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#764ba2" name="产品数量 / Products" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {amazonRatingData.length > 0 && (
        <div className="chart-section">
          <h2>⭐ Amazon 评分分布 / Rating Distribution</h2>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={amazonRatingData}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ rating, count }) => `${rating}: ${count}`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="count"
              >
                {amazonRatingData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {tiktokRatingData.length > 0 && (
        <div className="chart-section">
          <h2>⭐ TikTok 评分分布 / Rating Distribution</h2>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={tiktokRatingData}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ rating, count }) => `${rating}: ${count}`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="count"
              >
                {tiktokRatingData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="actions">
        <button
          className="button"
          onClick={handleGenerateReport}
          disabled={generating}
        >
          {generating ? '生成中... Generating...' : '📄 生成PDF报告 / Generate PDF Report'}
        </button>
        <button className="button" onClick={loadData}>
          🔄 刷新数据 / Refresh Data
        </button>
      </div>
    </div>
  );
}

export default App;
