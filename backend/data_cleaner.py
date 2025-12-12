"""
Data cleaning module for Auto-Report system
Processes sales and review data from multiple sources
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import os


class DataCleaner:
    """Main class for cleaning e-commerce data from multiple sources"""
    
    def __init__(self, data_dir: str = ".."):
        # Use absolute path for security
        if os.path.isabs(data_dir):
            self.data_dir = data_dir
        else:
            self.data_dir = os.path.abspath(data_dir)
        self.cleaned_data = {}
    
    def clean_amazon_sales(self) -> pd.DataFrame:
        """
        Clean Amazon sales data
        Returns: DataFrame with cleaned Amazon sales data
        """
        file_path = os.path.join(self.data_dir, "1. amazon销售.xlsx")
        df = pd.read_excel(file_path)
        
        # Select key columns for analysis
        key_columns = [
            'ASIN', '品牌', '商品标题', '大类目', '小类目', '大类BSR', 
            '月销量', '月销售额($)', '价格($)', '评分数', '评分', 
            '上架时间', '配送方式', '卖家数'
        ]
        
        # Filter existing columns
        existing_columns = [col for col in key_columns if col in df.columns]
        df_cleaned = df[existing_columns].copy()
        
        # Handle missing values
        df_cleaned['评分'] = df_cleaned['评分'].fillna(0)
        df_cleaned['月销量'] = df_cleaned['月销量'].fillna(0)
        df_cleaned['月销售额($)'] = df_cleaned['月销售额($)'].fillna(0)
        
        # Convert numeric columns
        df_cleaned['月销量'] = pd.to_numeric(df_cleaned['月销量'], errors='coerce').fillna(0)
        df_cleaned['月销售额($)'] = pd.to_numeric(df_cleaned['月销售额($)'], errors='coerce').fillna(0)
        df_cleaned['价格($)'] = pd.to_numeric(df_cleaned['价格($)'], errors='coerce').fillna(0)
        
        self.cleaned_data['amazon_sales'] = df_cleaned
        return df_cleaned
    
    def clean_tiktok_sales(self) -> pd.DataFrame:
        """
        Clean TikTok sales data
        Returns: DataFrame with cleaned TikTok sales data
        """
        file_path = os.path.join(self.data_dir, "1. tk销售.xlsx")
        df = pd.read_excel(file_path)
        
        # Select key columns
        key_columns = [
            '商品名称', '店铺名', '商品售价', '国家/地区', '商品分类',
            '销量', '总销量', '总销售额', '销售额', '店铺总销量', '商品状态'
        ]
        
        existing_columns = [col for col in key_columns if col in df.columns]
        df_cleaned = df[existing_columns].copy()
        
        # Handle missing values
        df_cleaned['销量'] = pd.to_numeric(df_cleaned['销量'], errors='coerce').fillna(0)
        df_cleaned['总销量'] = pd.to_numeric(df_cleaned['总销量'], errors='coerce').fillna(0)
        df_cleaned['总销售额'] = pd.to_numeric(df_cleaned['总销售额'], errors='coerce').fillna(0)
        df_cleaned['销售额'] = pd.to_numeric(df_cleaned['销售额'], errors='coerce').fillna(0)
        
        # Clean price column if it exists
        if '商品售价' in df_cleaned.columns:
            df_cleaned['商品售价'] = pd.to_numeric(df_cleaned['商品售价'], errors='coerce').fillna(0)
        
        self.cleaned_data['tiktok_sales'] = df_cleaned
        return df_cleaned
    
    def clean_tiktok_video_comments(self) -> pd.DataFrame:
        """
        Clean TikTok video comments data
        Returns: DataFrame with cleaned video comments
        """
        file_path = os.path.join(self.data_dir, "2. tk视频评论.csv")
        df = pd.read_csv(file_path)
        
        # Select key columns
        key_columns = [
            '视频ID', '评论ID', '用户昵称', '评论内容', 
            '发布时间', '点赞数', '回复数量'
        ]
        
        existing_columns = [col for col in key_columns if col in df.columns]
        df_cleaned = df[existing_columns].copy()
        
        # Handle missing values
        df_cleaned['评论内容'] = df_cleaned['评论内容'].fillna('')
        df_cleaned['点赞数'] = pd.to_numeric(df_cleaned['点赞数'], errors='coerce').fillna(0)
        df_cleaned['回复数量'] = pd.to_numeric(df_cleaned['回复数量'], errors='coerce').fillna(0)
        
        # Remove empty comments
        df_cleaned = df_cleaned[df_cleaned['评论内容'].str.strip() != '']
        
        self.cleaned_data['tiktok_video_comments'] = df_cleaned
        return df_cleaned
    
    def clean_amazon_reviews(self) -> pd.DataFrame:
        """
        Clean Amazon product reviews data
        Returns: DataFrame with cleaned Amazon reviews
        """
        file_path = os.path.join(self.data_dir, "3. amazon商品评论.xlsx")
        df = pd.read_excel(file_path)
        
        # Select key columns
        key_columns = [
            '型号', '标题', '内容', '内容(翻译)', '星级', 
            '赞同数', '评论时间', 'VP评论'
        ]
        
        existing_columns = [col for col in key_columns if col in df.columns]
        df_cleaned = df[existing_columns].copy()
        
        # Handle missing values
        df_cleaned['内容'] = df_cleaned['内容'].fillna('')
        df_cleaned['星级'] = pd.to_numeric(df_cleaned['星级'], errors='coerce').fillna(0)
        df_cleaned['赞同数'] = pd.to_numeric(df_cleaned['赞同数'], errors='coerce').fillna(0)
        
        self.cleaned_data['amazon_reviews'] = df_cleaned
        return df_cleaned
    
    def clean_tiktok_shop_reviews(self) -> pd.DataFrame:
        """
        Clean TikTok shop reviews data
        Returns: DataFrame with cleaned TikTok shop reviews
        """
        file_path = os.path.join(self.data_dir, "3.tiktok店铺评论.xlsx")
        df = pd.read_excel(file_path)
        
        # Select key columns (handling unnamed columns)
        df_cleaned = df.copy()
        
        # Rename columns for clarity
        df_cleaned.columns = ['ID1', 'ID2', '评分', '评论', '日期', '验证购买', 'SKU', '国家']
        
        # Select relevant columns
        df_cleaned = df_cleaned[['评分', '评论', '日期', 'SKU', '国家']].copy()
        
        # Handle missing values
        df_cleaned['评论'] = df_cleaned['评论'].fillna('')
        df_cleaned['评分'] = pd.to_numeric(df_cleaned['评分'], errors='coerce').fillna(0)
        
        # Filter valid ratings (1-5)
        df_cleaned = df_cleaned[(df_cleaned['评分'] >= 1) & (df_cleaned['评分'] <= 5)]
        
        self.cleaned_data['tiktok_shop_reviews'] = df_cleaned
        return df_cleaned
    
    def clean_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Clean all data sources
        Returns: Dictionary with all cleaned DataFrames
        """
        print("Cleaning Amazon sales data...")
        self.clean_amazon_sales()
        
        print("Cleaning TikTok sales data...")
        self.clean_tiktok_sales()
        
        print("Cleaning TikTok video comments...")
        self.clean_tiktok_video_comments()
        
        print("Cleaning Amazon reviews...")
        self.clean_amazon_reviews()
        
        print("Cleaning TikTok shop reviews...")
        self.clean_tiktok_shop_reviews()
        
        print("All data cleaned successfully!")
        return self.cleaned_data
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Generate summary statistics from cleaned data
        Returns: Dictionary with summary statistics
        """
        if not self.cleaned_data:
            self.clean_all_data()
        
        summary = {}
        
        # Amazon sales summary
        if 'amazon_sales' in self.cleaned_data:
            df = self.cleaned_data['amazon_sales']
            summary['amazon_sales'] = {
                'total_products': len(df),
                'total_monthly_sales': float(df['月销量'].sum()),
                'total_monthly_revenue': float(df['月销售额($)'].sum()),
                'avg_price': float(df['价格($)'].mean()),
                'avg_rating': float(df['评分'].mean()),
                'top_categories': df['大类目'].value_counts().head(5).to_dict()
            }
        
        # TikTok sales summary
        if 'tiktok_sales' in self.cleaned_data:
            df = self.cleaned_data['tiktok_sales']
            avg_price = 0
            if '商品售价' in df.columns:
                avg_price = float(df[df['商品售价'] > 0]['商品售价'].mean()) if len(df[df['商品售价'] > 0]) > 0 else 0
            
            summary['tiktok_sales'] = {
                'total_products': len(df),
                'total_sales_volume': float(df['总销量'].sum()),
                'total_revenue': float(df['总销售额'].sum()),
                'avg_price': avg_price,
                'top_categories': df['商品分类'].value_counts().head(5).to_dict()
            }
        
        # Amazon reviews summary
        if 'amazon_reviews' in self.cleaned_data:
            df = self.cleaned_data['amazon_reviews']
            summary['amazon_reviews'] = {
                'total_reviews': len(df),
                'avg_rating': float(df['星级'].mean()),
                'rating_distribution': df['星级'].value_counts().sort_index().to_dict()
            }
        
        # TikTok shop reviews summary
        if 'tiktok_shop_reviews' in self.cleaned_data:
            df = self.cleaned_data['tiktok_shop_reviews']
            summary['tiktok_shop_reviews'] = {
                'total_reviews': len(df),
                'avg_rating': float(df['评分'].mean()),
                'rating_distribution': df['评分'].value_counts().sort_index().to_dict()
            }
        
        # TikTok video comments summary
        if 'tiktok_video_comments' in self.cleaned_data:
            df = self.cleaned_data['tiktok_video_comments']
            summary['tiktok_video_comments'] = {
                'total_comments': len(df),
                'total_likes': int(df['点赞数'].sum()),
                'avg_likes': float(df['点赞数'].mean())
            }
        
        return summary


if __name__ == "__main__":
    # Test the data cleaner
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data()
    
    print("\n" + "="*50)
    print("Data Cleaning Summary")
    print("="*50)
    
    for source, df in cleaned_data.items():
        print(f"\n{source}: {len(df)} records")
        print(f"Columns: {list(df.columns)}")
    
    print("\n" + "="*50)
    print("Summary Statistics")
    print("="*50)
    
    summary = cleaner.get_summary_statistics()
    import json
    print(json.dumps(summary, indent=2, ensure_ascii=False))
