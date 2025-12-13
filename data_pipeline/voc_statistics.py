"""
Voice of Customer (VOC) Statistics

This module computes statistics from comments and reviews to extract
customer insights, usage scenarios, and unmet needs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional


def compute_comment_statistics(
    tiktok_summary: Dict[str, Any],
    reddit_summary: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compute statistics from user comments (TikTok + Reddit).
    
    Args:
        tiktok_summary: Summarized TikTok comments
        reddit_summary: Summarized Reddit comments (optional)
        
    Returns:
        Dictionary with comment-based insights
    """
    result = {
        'tiktok_stats': tiktok_summary.get('basic_stats', {}),
        'top_tiktok_by_likes': tiktok_summary.get('top_by_likes', []),
        'top_tiktok_by_replies': tiktok_summary.get('top_by_replies', []),
    }
    
    if reddit_summary:
        result['reddit_stats'] = reddit_summary.get('basic_stats', {})
        result['top_reddit_by_score'] = reddit_summary.get('top_by_score', [])
    
    return result


def compute_review_statistics(
    amazon_summary: Dict[str, Any],
    tiktok_summary: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compute statistics from product reviews (Amazon + TikTok Shop).
    
    Args:
        amazon_summary: Summarized Amazon reviews
        tiktok_summary: Summarized TikTok reviews (optional)
        
    Returns:
        Dictionary with review-based insights
    """
    result = {
        'amazon_rating_distribution': amazon_summary.get('rating_distribution', {}),
        'amazon_top5_products': amazon_summary.get('top5_products', []),
        'amazon_top5_reviewers': amazon_summary.get('top5_reviewers', []),
    }
    
    if tiktok_summary:
        result['tiktok_rating_distribution'] = tiktok_summary.get('rating_distribution', {})
        result['tiktok_top5_sku'] = tiktok_summary.get('top5_sku_by_reviews', [])
    
    return result


def compute_voc_statistics(
    comments_summary: Optional[Dict[str, Any]] = None,
    reviews_summary: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compute comprehensive Voice of Customer statistics.
    
    Args:
        comments_summary: Combined comments statistics
        reviews_summary: Combined reviews statistics
        
    Returns:
        Complete VOC statistics JSON structure
    """
    statistics = {
        'timestamp': pd.Timestamp.now().isoformat(),
    }
    
    # Stage 2: Comments-based insights
    if comments_summary:
        statistics['stage2_comments'] = comments_summary
    else:
        statistics['stage2_comments'] = {
            'tiktok_stats': {},
            'reddit_stats': {},
        }
    
    # Stage 3: Reviews-based insights
    if reviews_summary:
        statistics['stage3_reviews'] = reviews_summary
    else:
        statistics['stage3_reviews'] = {
            'amazon_rating_distribution': {},
            'tiktok_rating_distribution': {},
        }
    
    return statistics
