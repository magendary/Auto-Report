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
    Supports both Chinese and English column names.
    
    Args:
        df: Raw DataFrame from uploaded TikTok comments file
        
    Returns:
        Dictionary mapping standardized field names to actual column names
    """
    col_map_candidates = {
        "video_id":    ["video_id", "视频ID"],
        "comment_id":  ["comment_id", "评论ID"],
        "user_id":     ["user_id", "用户ID"],
        "username":    ["username", "用户昵称", "昵称"],
        "text":        ["comment_text", "text", "评论内容", "内容"],
        "created_at":  ["created_at", "time", "发布时间"],
        "like_count":  ["like_count", "likes", "点赞数"],
        "reply_count": ["reply_count", "replies", "回复数量"],
    }
    
    resolved = {}
    for std_name, candidates in col_map_candidates.items():
        for c in candidates:
            if c in df.columns:
                resolved[std_name] = c
                break
    
    return resolved


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
    统一清洗 TikTok 视频评论数据。
    支持中英列名（视频ID/评论内容/点赞数等），返回标准字段：
    video_id, comment_id, user_id, username, text, created_at, like_count, reply_count, source
    
    Process and normalize TikTok video comments.
    Supports both Chinese and English column names.
    
    Args:
        df: Raw DataFrame from uploaded TikTok comments file
        
    Returns:
        Normalized DataFrame with standard fields:
        video_id, comment_id, user_id, username, text, created_at, like_count, reply_count, source
    """
    # Detect column mappings
    resolved = detect_tiktok_comment_columns(df)
    
    # 文本列是必须要有的 / Text column is required
    if "text" not in resolved:
        raise ValueError(
            f"Comment text column not found. Available columns: {list(df.columns)}"
        )
    
    # Create normalized DataFrame
    normalized = pd.DataFrame()
    
    # 按已匹配到的列进行拷贝 / Copy matched columns
    for std_name, src_col in resolved.items():
        if std_name == "text":
            # Apply text cleaning to comment text
            normalized[std_name] = df[src_col].astype(str).apply(clean_comment_text)
        else:
            normalized[std_name] = df[src_col]
    
    # 基础类型转换 / Basic type conversions
    if "created_at" in normalized.columns:
        normalized["created_at"] = pd.to_datetime(normalized["created_at"], errors="coerce")
    
    for num_col in ["like_count", "reply_count"]:
        if num_col in normalized.columns:
            normalized[num_col] = pd.to_numeric(normalized[num_col], errors="coerce").fillna(0).astype(int)
        else:
            # Add column with default value if not present
            normalized[num_col] = 0
    
    # Ensure backwards compatibility: add 'likes' column as alias for 'like_count'
    if 'like_count' in normalized.columns:
        normalized['likes'] = normalized['like_count']
    
    normalized["source"] = "tiktok"
    
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
