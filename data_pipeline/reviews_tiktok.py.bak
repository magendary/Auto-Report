"""
TikTok Shop Product Reviews Processing

This module processes TikTok Shop product reviews to extract post-purchase feedback
and insights.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re


def detect_tiktok_review_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect TikTok Shop review columns by matching common patterns.
    
    Args:
        df: Raw DataFrame from uploaded TikTok reviews file
        
    Returns:
        Dictionary mapping standardized field names to actual column names
    """
    column_mapping = {}
    
    patterns = {
        'product_id': ['product_id', 'product id', 'id', 'sku'],
        'text': ['text', 'review_text', 'review', 'content', 'comment'],
        'rating': ['rating', 'star_rating', 'stars', 'score'],
        'helpful': ['helpful', 'helpful_count', 'likes', 'thumbs_up'],
        'date': ['date', 'review_date', 'created_at', 'create_time'],
        'country': ['country', 'location', 'region'],
        'user_id': ['user_id', 'user', 'reviewer'],
    }
    
    df_columns_lower = {col.lower(): col for col in df.columns}
    
    for field, keywords in patterns.items():
        for keyword in keywords:
            if keyword in df_columns_lower:
                column_mapping[field] = df_columns_lower[keyword]
                break
    
    return column_mapping


def process_tiktok_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process and normalize TikTok Shop product reviews.
    
    Args:
        df: Raw DataFrame from uploaded TikTok reviews file
        
    Returns:
        Normalized DataFrame with processed reviews
    """
    # Detect column mappings
    column_mapping = detect_tiktok_review_columns(df)
    
    # Create normalized DataFrame
    normalized = pd.DataFrame()
    
    if 'product_id' in column_mapping:
        normalized['product_id'] = df[column_mapping['product_id']].astype(str)
    
    if 'text' in column_mapping:
        normalized['text'] = df[column_mapping['text']].astype(str).apply(clean_review_text)
    else:
        raise ValueError("Review text column not found in the uploaded file")
    
    if 'rating' in column_mapping:
        normalized['rating'] = pd.to_numeric(df[column_mapping['rating']], errors='coerce')
        # Normalize to 5-point scale if needed
        if normalized['rating'].max() > 5:
            normalized['rating'] = normalized['rating'] / normalized['rating'].max() * 5
    else:
        normalized['rating'] = 0
    
    if 'helpful' in column_mapping:
        normalized['helpful'] = pd.to_numeric(df[column_mapping['helpful']], errors='coerce').fillna(0)
    else:
        normalized['helpful'] = 0
    
    if 'date' in column_mapping:
        normalized['date'] = pd.to_datetime(df[column_mapping['date']], errors='coerce')
    
    if 'country' in column_mapping:
        normalized['country'] = df[column_mapping['country']].astype(str)
    
    # All TikTok Shop reviews are from verified purchases
    normalized['verified'] = True
    
    # Add platform identifier
    normalized['platform'] = 'tiktok'
    
    # Filter valid reviews
    normalized = normalized[normalized['text'].str.len() >= 10]
    
    return normalized


def clean_review_text(text: str) -> str:
    """
    Clean TikTok review text.
    
    Args:
        text: Raw review text
        
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove emojis
    text = re.sub(r'[\U00010000-\U0010ffff]+', ' ', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'([!?.]){3,}', r'\1\1', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def combine_reviews(amazon_df: pd.DataFrame, tiktok_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine Amazon and TikTok reviews into a single DataFrame.
    
    Args:
        amazon_df: Processed Amazon reviews
        tiktok_df: Processed TikTok reviews
        
    Returns:
        Combined DataFrame with all reviews
    """
    # Ensure both DataFrames have the same columns
    required_cols = ['text', 'rating', 'helpful', 'platform', 'verified']
    
    for df in [amazon_df, tiktok_df]:
        for col in required_cols:
            if col not in df.columns:
                if col == 'rating':
                    df[col] = 0
                elif col == 'helpful':
                    df[col] = 0
                elif col == 'verified':
                    df[col] = True
                else:
                    df[col] = ''
    
    combined = pd.concat([amazon_df, tiktok_df], ignore_index=True)
    
    return combined
