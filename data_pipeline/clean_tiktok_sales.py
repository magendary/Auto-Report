"""
TikTok Shop Sales Data Cleaning and Normalization

This module handles the cleaning and normalization of TikTok Shop sales data
into a standardized schema for further analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime
import re


def detect_tiktok_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect TikTok Shop sales data columns by matching common patterns.
    
    Args:
        df: Raw DataFrame from uploaded TikTok Shop sales file
        
    Returns:
        Dictionary mapping standardized field names to actual column names
    """
    column_mapping = {}
    
    # Common TikTok Shop column patterns
    patterns = {
        'product_id': ['product_id', 'product id', 'id', 'sku'],
        'title': ['title', 'product_title', 'product name', 'name', 'product_name'],
        'price': ['price', 'unit_price', 'selling_price', 'sale_price'],
        'sales': ['sales', 'units_sold', 'quantity_sold', 'qty', 'sold'],
        'revenue': ['revenue', 'total_revenue', 'gmv', 'sales_amount'],
        'rating': ['rating', 'avg_rating', 'average_rating', 'score'],
        'reviews': ['reviews', 'review_count', 'number_of_reviews'],
        'launch_date': ['launch_date', 'created_at', 'publish_date'],
        'category': ['category', 'product_category', 'category_name'],
        'shop': ['shop', 'shop_name', 'store', 'store_name', 'seller'],
        'size': ['size', 'product_size'],
        'weight': ['weight', 'product_weight'],
    }
    
    # Match patterns to actual columns (case-insensitive)
    df_columns_lower = {col.lower(): col for col in df.columns}
    
    for field, keywords in patterns.items():
        for keyword in keywords:
            if keyword in df_columns_lower:
                column_mapping[field] = df_columns_lower[keyword]
                break
    
    return column_mapping


def clean_tiktok_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize TikTok Shop sales data.
    
    Args:
        df: Raw DataFrame from uploaded TikTok Shop sales file
        
    Returns:
        Normalized DataFrame with standardized schema
    """
    # Detect column mappings
    column_mapping = detect_tiktok_columns(df)
    
    # Create normalized DataFrame
    normalized = pd.DataFrame()
    
    # Map and clean each field
    if 'product_id' in column_mapping:
        normalized['product_id'] = df[column_mapping['product_id']].astype(str)
    else:
        # Generate IDs if not present
        normalized['product_id'] = [f'TT_{i}' for i in range(len(df))]
    
    if 'title' in column_mapping:
        normalized['title'] = df[column_mapping['title']].astype(str).str.strip()
    
    if 'price' in column_mapping:
        normalized['price'] = pd.to_numeric(
            df[column_mapping['price']].astype(str).str.replace('[$,]', '', regex=True),
            errors='coerce'
        )
    
    if 'sales' in column_mapping:
        normalized['sales'] = pd.to_numeric(df[column_mapping['sales']], errors='coerce')
    
    if 'revenue' in column_mapping:
        normalized['revenue'] = pd.to_numeric(df[column_mapping['revenue']], errors='coerce')
    elif 'price' in normalized.columns and 'sales' in normalized.columns:
        # Calculate revenue if not provided
        normalized['revenue'] = normalized['price'] * normalized['sales']
    
    if 'rating' in column_mapping:
        normalized['rating'] = pd.to_numeric(df[column_mapping['rating']], errors='coerce')
        # Normalize ratings to 5-point scale if needed
        if normalized['rating'].max() > 5:
            normalized['rating'] = normalized['rating'] / normalized['rating'].max() * 5
    
    if 'reviews' in column_mapping:
        normalized['reviews'] = pd.to_numeric(df[column_mapping['reviews']], errors='coerce')
    
    if 'launch_date' in column_mapping:
        normalized['launch_date'] = pd.to_datetime(df[column_mapping['launch_date']], errors='coerce')
        normalized['days_since_launch'] = (datetime.now() - normalized['launch_date']).dt.days
    
    if 'category' in column_mapping:
        normalized['category'] = df[column_mapping['category']].astype(str)
    
    if 'shop' in column_mapping:
        normalized['shop'] = df[column_mapping['shop']].astype(str)
    
    if 'size' in column_mapping:
        normalized['size'] = df[column_mapping['size']].astype(str)
    
    if 'weight' in column_mapping:
        normalized['weight'] = pd.to_numeric(
            df[column_mapping['weight']].astype(str).str.extract(r'(\d+\.?\d*)')[0],
            errors='coerce'
        )
    
    # Add platform identifier
    normalized['platform'] = 'tiktok'
    
    # Drop rows with critical missing data
    critical_columns = ['product_id', 'title']
    existing_critical = [col for col in critical_columns if col in normalized.columns]
    normalized = normalized.dropna(subset=existing_critical)
    
    # Fill NaN values
    if 'price' in normalized.columns:
        normalized['price'] = normalized['price'].fillna(0)
    if 'sales' in normalized.columns:
        normalized['sales'] = normalized['sales'].fillna(0)
    if 'revenue' in normalized.columns:
        normalized['revenue'] = normalized['revenue'].fillna(0)
    if 'rating' in normalized.columns:
        normalized['rating'] = normalized['rating'].fillna(0)
    
    return normalized
