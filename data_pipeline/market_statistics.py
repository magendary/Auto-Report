"""
Market Statistics Computation

This module computes comprehensive market statistics from sales data,
producing structured JSON for LLM analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter
from .clean_amazon_sales import extract_features_from_title


def compute_market_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute basic market overview statistics.
    
    Args:
        df: Normalized sales DataFrame
        
    Returns:
        Dictionary with market overview metrics
    """
    return {
        'total_products': len(df),
        'total_sales': int(df['sales'].sum()) if 'sales' in df.columns else 0,
        'total_revenue': float(df['revenue'].sum()) if 'revenue' in df.columns else 0,
        'avg_price': float(df['price'].mean()) if 'price' in df.columns else 0,
        'median_price': float(df['price'].median()) if 'price' in df.columns else 0,
        'avg_rating': float(df['rating'].mean()) if 'rating' in df.columns else 0,
        'price_range': {
            'min': float(df['price'].min()) if 'price' in df.columns else 0,
            'max': float(df['price'].max()) if 'price' in df.columns else 0,
        }
    }


def compute_competition_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute competition and market concentration metrics.
    
    Args:
        df: Normalized sales DataFrame
        
    Returns:
        Dictionary with competition metrics
    """
    if df.empty or 'sales' not in df.columns:
        return {}
    
    # Sort by sales
    df_sorted = df.sort_values('sales', ascending=False)
    total_sales = df['sales'].sum()
    
    # Top 10 and top 20 concentration
    top10_sales = df_sorted.head(10)['sales'].sum()
    top20_sales = df_sorted.head(20)['sales'].sum()
    
    # Seller/shop concentration
    seller_col = 'seller' if 'seller' in df.columns else 'shop' if 'shop' in df.columns else None
    seller_concentration = {}
    
    if seller_col and seller_col in df.columns:
        seller_sales = df.groupby(seller_col)['sales'].sum().sort_values(ascending=False)
        top_sellers = seller_sales.head(10)
        seller_concentration = {
            'top10_seller_share': float(top_sellers.sum() / total_sales) if total_sales > 0 else 0,
            'unique_sellers': int(df[seller_col].nunique()),
            'avg_sales_per_seller': float(seller_sales.mean()),
        }
    
    # Long tail index (products below average sales)
    avg_sales = df['sales'].mean()
    long_tail_count = len(df[df['sales'] < avg_sales])
    long_tail_index = long_tail_count / len(df) if len(df) > 0 else 0
    
    return {
        'top10_share': float(top10_sales / total_sales) if total_sales > 0 else 0,
        'top20_share': float(top20_sales / total_sales) if total_sales > 0 else 0,
        'long_tail_index': float(long_tail_index),
        **seller_concentration,
    }


def compute_price_bands(df: pd.DataFrame, num_bands: int = 5) -> List[Dict[str, Any]]:
    """
    Divide products into price bands and compute metrics for each.
    
    Args:
        df: Normalized sales DataFrame
        num_bands: Number of price bands to create
        
    Returns:
        List of price band statistics
    """
    if df.empty or 'price' not in df.columns:
        return []
    
    # Create price bands
    df['price_band'] = pd.qcut(df['price'], q=num_bands, labels=False, duplicates='drop')
    
    bands = []
    for band_id in sorted(df['price_band'].unique()):
        band_df = df[df['price_band'] == band_id]
        
        bands.append({
            'band': int(band_id),
            'price_range': {
                'min': float(band_df['price'].min()),
                'max': float(band_df['price'].max()),
            },
            'product_count': len(band_df),
            'total_sales': int(band_df['sales'].sum()) if 'sales' in band_df.columns else 0,
            'total_revenue': float(band_df['revenue'].sum()) if 'revenue' in band_df.columns else 0,
            'avg_rating': float(band_df['rating'].mean()) if 'rating' in band_df.columns else 0,
        })
    
    return bands


def compute_price_vs_sales_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute price vs sales correlation and identify sweet spots.
    
    Args:
        df: Normalized sales DataFrame
        
    Returns:
        Dictionary with correlation metrics
    """
    if df.empty or 'price' not in df.columns or 'sales' not in df.columns:
        return {}
    
    # Correlation coefficient
    correlation = df['price'].corr(df['sales'])
    
    # Find sweet spot (price range with highest sales)
    df['price_bucket'] = pd.cut(df['price'], bins=10)
    sweet_spots = df.groupby('price_bucket')['sales'].sum().sort_values(ascending=False).head(3)
    
    sweet_spot_ranges = []
    for bucket in sweet_spots.index:
        sweet_spot_ranges.append({
            'price_range': f"{bucket.left:.2f} - {bucket.right:.2f}",
            'total_sales': int(sweet_spots[bucket]),
        })
    
    return {
        'correlation': float(correlation),
        'relationship': 'positive' if correlation > 0.3 else 'negative' if correlation < -0.3 else 'weak',
        'sweet_spots': sweet_spot_ranges,
    }


def extract_feature_performance(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Extract and analyze product features from titles.
    
    Args:
        df: Normalized sales DataFrame
        
    Returns:
        List of feature performance metrics
    """
    if df.empty or 'title' not in df.columns:
        return []
    
    # Extract features from all products
    all_features = []
    for _, row in df.iterrows():
        features = extract_features_from_title(row['title'])
        for key, value in features.items():
            all_features.append({
                'feature_type': key,
                'feature_value': value,
                'sales': row.get('sales', 0),
                'price': row.get('price', 0),
                'rating': row.get('rating', 0),
            })
    
    if not all_features:
        return []
    
    # Aggregate by feature
    features_df = pd.DataFrame(all_features)
    feature_stats = []
    
    for feature_type in features_df['feature_type'].unique():
        feature_data = features_df[features_df['feature_type'] == feature_type]
        
        # Group by feature value
        for value in feature_data['feature_value'].unique():
            value_data = feature_data[feature_data['feature_value'] == value]
            
            feature_stats.append({
                'feature': f"{feature_type}={value}",
                'product_count': len(value_data),
                'total_sales': int(value_data['sales'].sum()),
                'avg_price': float(value_data['price'].mean()),
                'avg_rating': float(value_data['rating'].mean()),
            })
    
    # Sort by sales
    feature_stats = sorted(feature_stats, key=lambda x: x['total_sales'], reverse=True)
    
    return feature_stats[:20]


def compute_launch_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze product launch dates and growth patterns.
    
    Args:
        df: Normalized sales DataFrame
        
    Returns:
        Dictionary with launch profile metrics
    """
    if df.empty or 'days_since_launch' not in df.columns:
        return {}
    
    # Filter out invalid dates
    valid_df = df[df['days_since_launch'] > 0].copy()
    
    if valid_df.empty:
        return {}
    
    # Categorize by launch age
    valid_df['age_category'] = pd.cut(
        valid_df['days_since_launch'],
        bins=[0, 30, 90, 180, 365, float('inf')],
        labels=['<1mo', '1-3mo', '3-6mo', '6-12mo', '>12mo']
    )
    
    age_distribution = []
    for category in valid_df['age_category'].cat.categories:
        cat_df = valid_df[valid_df['age_category'] == category]
        if not cat_df.empty:
            age_distribution.append({
                'age': str(category),
                'product_count': len(cat_df),
                'total_sales': int(cat_df['sales'].sum()) if 'sales' in cat_df.columns else 0,
                'avg_rating': float(cat_df['rating'].mean()) if 'rating' in cat_df.columns else 0,
            })
    
    return {
        'age_distribution': age_distribution,
        'avg_days_since_launch': float(valid_df['days_since_launch'].mean()),
        'median_days_since_launch': float(valid_df['days_since_launch'].median()),
    }


def compute_rating_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze rating distribution and patterns.
    
    Args:
        df: Normalized sales DataFrame
        
    Returns:
        Dictionary with rating profile metrics
    """
    if df.empty or 'rating' not in df.columns:
        return {}
    
    # Rating distribution
    rating_bins = [0, 2, 3, 4, 5]
    rating_labels = ['1-2 stars', '2-3 stars', '3-4 stars', '4-5 stars']
    
    df['rating_category'] = pd.cut(df['rating'], bins=rating_bins, labels=rating_labels, include_lowest=True)
    
    rating_dist = []
    for category in rating_labels:
        cat_df = df[df['rating_category'] == category]
        if not cat_df.empty:
            rating_dist.append({
                'category': category,
                'product_count': len(cat_df),
                'sales_share': float(cat_df['sales'].sum() / df['sales'].sum()) if 'sales' in df.columns else 0,
            })
    
    # Review to sales ratio
    review_to_sales = 0
    if 'reviews' in df.columns and 'sales' in df.columns:
        total_reviews = df['reviews'].sum()
        total_sales = df['sales'].sum()
        review_to_sales = float(total_reviews / total_sales) if total_sales > 0 else 0
    
    return {
        'rating_distribution': rating_dist,
        'avg_rating': float(df['rating'].mean()),
        'median_rating': float(df['rating'].median()),
        'review_to_sales_ratio': review_to_sales,
    }


def compute_market_statistics(
    amazon_df: Optional[pd.DataFrame] = None,
    tiktok_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Compute comprehensive market statistics from sales data.
    
    Args:
        amazon_df: Normalized Amazon sales DataFrame
        tiktok_df: Normalized TikTok sales DataFrame
        
    Returns:
        Complete market statistics JSON structure
    """
    statistics = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'platforms': {},
    }
    
    # Process each platform separately
    for platform_name, df in [('amazon', amazon_df), ('tiktok', tiktok_df)]:
        if df is None or df.empty:
            continue
        
        statistics['platforms'][platform_name] = {
            'market_overview': compute_market_overview(df),
            'competition': compute_competition_metrics(df),
            'price_bands': compute_price_bands(df),
            'price_vs_sales': compute_price_vs_sales_correlation(df),
            'feature_performance': extract_feature_performance(df),
            'launch_profile': compute_launch_profile(df),
            'rating_profile': compute_rating_profile(df),
        }
    
    # Cross-platform comparison
    if amazon_df is not None and tiktok_df is not None and not amazon_df.empty and not tiktok_df.empty:
        statistics['cross_platform'] = {
            'volume_comparison': {
                'amazon_products': len(amazon_df),
                'tiktok_products': len(tiktok_df),
                'amazon_sales': int(amazon_df['sales'].sum()) if 'sales' in amazon_df.columns else 0,
                'tiktok_sales': int(tiktok_df['sales'].sum()) if 'sales' in tiktok_df.columns else 0,
            },
            'price_comparison': {
                'amazon_avg': float(amazon_df['price'].mean()) if 'price' in amazon_df.columns else 0,
                'tiktok_avg': float(tiktok_df['price'].mean()) if 'price' in tiktok_df.columns else 0,
            },
            'rating_comparison': {
                'amazon_avg': float(amazon_df['rating'].mean()) if 'rating' in amazon_df.columns else 0,
                'tiktok_avg': float(tiktok_df['rating'].mean()) if 'rating' in tiktok_df.columns else 0,
            }
        }
    
    return statistics
