"""
Amazon Sales Data Cleaning and Normalization

This module handles the cleaning and normalization of Amazon sales data
into a standardized schema for further analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import re


def detect_amazon_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect Amazon sales data columns by matching common patterns.
    
    Args:
        df: Raw DataFrame from uploaded Amazon sales file
        
    Returns:
        Dictionary mapping standardized field names to actual column names
    """
    column_mapping = {}
    
    # Common Amazon column patterns
    patterns = {
        'product_id': ['asin', 'product_id', 'product id', 'id'],
        'title': ['title', 'product_title', 'product name', 'name'],
        'price': ['price', 'unit_price', 'list_price'],
        'sales': ['sales', 'units_sold', 'quantity', 'qty'],
        'revenue': ['revenue', 'total_revenue', 'sales_amount'],
        'rating': ['rating', 'avg_rating', 'average_rating', 'star_rating'],
        'reviews': ['reviews', 'review_count', 'number_of_reviews'],
        'launch_date': ['launch_date', 'release_date', 'available_date'],
        'category': ['category', 'product_category', 'department'],
        'seller': ['seller', 'seller_name', 'merchant'],
        'size': ['size', 'product_size', 'dimensions'],
        'weight': ['weight', 'product_weight', 'shipping_weight'],
    }
    
    # Match patterns to actual columns (case-insensitive)
    df_columns_lower = {col.lower(): col for col in df.columns}
    
    for field, keywords in patterns.items():
        for keyword in keywords:
            if keyword in df_columns_lower:
                column_mapping[field] = df_columns_lower[keyword]
                break
    
    return column_mapping


def clean_amazon_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize Amazon sales data.
    
    Args:
        df: Raw DataFrame from uploaded Amazon sales file
        
    Returns:
        Normalized DataFrame with standardized schema
    """
    # Detect column mappings
    column_mapping = detect_amazon_columns(df)
    
    # Create normalized DataFrame
    normalized = pd.DataFrame()
    
    # Map and clean each field
    if 'product_id' in column_mapping:
        normalized['product_id'] = df[column_mapping['product_id']].astype(str)
    else:
        # Generate IDs if not present
        normalized['product_id'] = [f'AMZ_{i}' for i in range(len(df))]
    
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
        # Ensure ratings are between 0 and 5
        normalized.loc[normalized['rating'] > 5, 'rating'] = normalized.loc[normalized['rating'] > 5, 'rating'] / 10
    
    if 'reviews' in column_mapping:
        normalized['reviews'] = pd.to_numeric(df[column_mapping['reviews']], errors='coerce')
    
    if 'launch_date' in column_mapping:
        normalized['launch_date'] = pd.to_datetime(df[column_mapping['launch_date']], errors='coerce')
        normalized['days_since_launch'] = (datetime.now() - normalized['launch_date']).dt.days
    
    if 'category' in column_mapping:
        normalized['category'] = df[column_mapping['category']].astype(str)
    
    if 'seller' in column_mapping:
        normalized['seller'] = df[column_mapping['seller']].astype(str)
    
    if 'size' in column_mapping:
        normalized['size'] = df[column_mapping['size']].astype(str)
    
    if 'weight' in column_mapping:
        normalized['weight'] = pd.to_numeric(
            df[column_mapping['weight']].astype(str).str.extract(r'(\d+\.?\d*)')[0],
            errors='coerce'
        )
    
    # Add platform identifier
    normalized['platform'] = 'amazon'
    
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


def extract_features_from_title(title: str) -> Dict[str, Any]:
    """
    Extract product features from title using heuristics.
    
    Args:
        title: Product title string
        
    Returns:
        Dictionary of extracted features
    """
    title_lower = title.lower()
    features = {}
    
    # Common hair/wig features (example for wig niche)
    if 'lace' in title_lower:
        if 'front' in title_lower:
            features['lace_type'] = 'lace_front'
        elif '360' in title_lower:
            features['lace_type'] = '360_lace'
        elif 'closure' in title_lower:
            features['lace_type'] = 'lace_closure'
        else:
            features['lace_type'] = 'lace'
    
    if 'glueless' in title_lower:
        features['glueless'] = True
    
    if 'body wave' in title_lower:
        features['texture'] = 'body_wave'
    elif 'straight' in title_lower:
        features['texture'] = 'straight'
    elif 'curly' in title_lower:
        features['texture'] = 'curly'
    elif 'kinky' in title_lower:
        features['texture'] = 'kinky'
    
    # Extract length (e.g., "20 inch", "22\"")
    length_match = re.search(r'(\d+)\s*(inch|in|")', title_lower)
    if length_match:
        features['length'] = int(length_match.group(1))
    
    # Color detection
    color_keywords = ['black', 'brown', 'blonde', 'burgundy', 'red', 'ombre', 'highlight']
    for color in color_keywords:
        if color in title_lower:
            features['color'] = color
            break
    
    return features
