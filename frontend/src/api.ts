import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export interface SummaryData {
  amazon_sales?: {
    total_products: number;
    total_monthly_sales: number;
    total_monthly_revenue: number;
    avg_price: number;
    avg_rating: number;
    top_categories: Record<string, number>;
  };
  tiktok_sales?: {
    total_products: number;
    total_sales_volume: number;
    total_revenue: number;
    avg_price: number;
    top_categories: Record<string, number>;
  };
  amazon_reviews?: {
    total_reviews: number;
    avg_rating: number;
    rating_distribution: Record<string, number>;
  };
  tiktok_shop_reviews?: {
    total_reviews: number;
    avg_rating: number;
    rating_distribution: Record<string, number>;
  };
  tiktok_video_comments?: {
    total_comments: number;
    total_likes: number;
    avg_likes: number;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export const api = {
  async getSummary(): Promise<SummaryData> {
    const response = await axios.get<ApiResponse<SummaryData>>(`${API_BASE_URL}/data/summary`);
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error || 'Failed to fetch summary');
  },

  async generateReport(): Promise<string> {
    const response = await axios.post<ApiResponse<{ filename: string }>>(`${API_BASE_URL}/report/generate`);
    if (response.data.success && response.data.data) {
      return response.data.data.filename;
    }
    throw new Error(response.data.error || 'Failed to generate report');
  },

  async downloadReport(filename: string): Promise<void> {
    window.open(`${API_BASE_URL}/report/download/${filename}`, '_blank');
  },

  getDownloadUrl(filename: string): string {
    return `${API_BASE_URL}/report/download/${filename}`;
  }
};
