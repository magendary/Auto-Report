"""
TikTok Video Comments Processing

This module processes TikTok video comments to extract insights about
user opinions, reasons to buy/not buy, and usage scenarios.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from collections import Counter
import re


def detect_tiktok_comment_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect TikTok comment columns by matching common patterns.
    
    Args:
        df: Raw DataFrame from uploaded TikTok comments file
        
    Returns:
        Dictionary mapping standardized field names to actual column names
    """
    column_mapping = {}
    
    patterns = {
        'text': ['text', 'comment', 'comment_text', 'content'],
        'likes': ['likes', 'like_count', 'digg_count', 'thumbs_up'],
        'created_at': ['created_at', 'create_time', 'timestamp', 'date'],
        'user_id': ['user_id', 'user', 'username', 'author'],
    }
    
    df_columns_lower = {col.lower(): col for col in df.columns}
    
    for field, keywords in patterns.items():
        for keyword in keywords:
            if keyword in df_columns_lower:
                column_mapping[field] = df_columns_lower[keyword]
                break
    
    return column_mapping


def clean_comment_text(text: str) -> str:
    """
    Clean and normalize comment text.
    
    Args:
        text: Raw comment text
        
    Returns:
        Cleaned comment text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove excessive emojis and special characters
    text = re.sub(r'[\U00010000-\U0010ffff]+', ' ', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove @mentions
    text = re.sub(r'@\w+', '', text)
    
    # Remove hashtags but keep the text
    text = re.sub(r'#(\w+)', r'\1', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def is_valid_comment(text: str, min_length: int = 5) -> bool:
    """
    Check if a comment is valid for analysis.
    
    Args:
        text: Comment text
        min_length: Minimum character length
        
    Returns:
        True if comment is valid, False otherwise
    """
    if not text or len(text) < min_length:
        return False
    
    # Filter out pure emoji or special character comments
    if not any(c.isalnum() for c in text):
        return False
    
    # Filter out spam patterns
    spam_patterns = ['follow me', 'check out my', 'click link', 'dm me']
    text_lower = text.lower()
    if any(pattern in text_lower for pattern in spam_patterns):
        return False
    
    return True


def process_tiktok_comments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process and normalize TikTok video comments.
    
    Args:
        df: Raw DataFrame from uploaded TikTok comments file
        
    Returns:
        Normalized DataFrame with cleaned comments
    """
    # Detect column mappings
    column_mapping = detect_tiktok_comment_columns(df)
    
    # Create normalized DataFrame
    normalized = pd.DataFrame()
    
    if 'text' in column_mapping:
        normalized['text'] = df[column_mapping['text']].astype(str).apply(clean_comment_text)
    else:
        raise ValueError("Comment text column not found in the uploaded file")
    
    if 'likes' in column_mapping:
        normalized['likes'] = pd.to_numeric(df[column_mapping['likes']], errors='coerce').fillna(0)
    else:
        normalized['likes'] = 0
    
    if 'created_at' in column_mapping:
        normalized['created_at'] = pd.to_datetime(df[column_mapping['created_at']], errors='coerce')
    
    if 'user_id' in column_mapping:
        normalized['user_id'] = df[column_mapping['user_id']].astype(str)
    
    # Add source identifier
    normalized['source'] = 'tiktok'
    
    # Filter valid comments
    normalized['is_valid'] = normalized['text'].apply(is_valid_comment)
    normalized = normalized[normalized['is_valid']].drop('is_valid', axis=1)
    
    return normalized


def categorize_comments(comments: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize comments into different groups using heuristics.
    
    Args:
        comments: DataFrame of processed comments
        
    Returns:
        Dictionary with categorized comments
    """
    categories = {
        'reasons_to_buy': [],
        'reasons_not_to_buy': [],
        'usage_scenarios': [],
        'user_segments': [],
    }
    
    # Keywords for different categories
    positive_keywords = [
        'love', 'amazing', 'perfect', 'great', 'best', 'beautiful',
        'recommend', 'worth', 'buy', 'purchased', 'happy'
    ]
    
    negative_keywords = [
        'bad', 'terrible', 'worst', 'poor', 'disappointed', 'waste',
        'don\'t buy', 'regret', 'cheap', 'fake', 'scam'
    ]
    
    usage_keywords = [
        'use', 'wear', 'tried', 'works', 'applying', 'installed',
        'occasion', 'event', 'party', 'daily', 'everyday'
    ]
    
    segment_keywords = {
        'beginners': ['first time', 'beginner', 'new to', 'starting'],
        'professionals': ['professional', 'expert', 'experienced', 'pro'],
        'budget_conscious': ['cheap', 'affordable', 'budget', 'price'],
        'quality_seekers': ['quality', 'premium', 'high-end', 'luxury'],
    }
    
    for _, comment in comments.iterrows():
        text_lower = comment['text'].lower()
        
        # Categorize by sentiment
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        
        if positive_count > negative_count:
            categories['reasons_to_buy'].append({
                'text': comment['text'],
                'likes': comment.get('likes', 0),
                'score': positive_count
            })
        elif negative_count > positive_count:
            categories['reasons_not_to_buy'].append({
                'text': comment['text'],
                'likes': comment.get('likes', 0),
                'score': negative_count
            })
        
        # Usage scenarios
        if any(kw in text_lower for kw in usage_keywords):
            categories['usage_scenarios'].append({
                'text': comment['text'],
                'likes': comment.get('likes', 0),
            })
        
        # User segments
        for segment, keywords in segment_keywords.items():
            if any(kw in text_lower for kw in keywords):
                categories['user_segments'].append({
                    'segment': segment,
                    'text': comment['text'],
                    'likes': comment.get('likes', 0),
                })
    
    # Sort by likes and score
    for key in ['reasons_to_buy', 'reasons_not_to_buy']:
        categories[key] = sorted(
            categories[key],
            key=lambda x: (x['score'], x['likes']),
            reverse=True
        )[:10]
    
    categories['usage_scenarios'] = sorted(
        categories['usage_scenarios'],
        key=lambda x: x['likes'],
        reverse=True
    )[:10]
    
    return categories
