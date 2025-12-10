"""
Voice of Customer (VOC) Statistics

This module computes statistics from comments and reviews to extract
customer insights, usage scenarios, and unmet needs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from .comments_tiktok import categorize_comments
from .reviews_amazon import (
    extract_must_have_factors,
    extract_critical_pitfalls,
    extract_usage_scenarios as extract_review_usage_scenarios,
    extract_unmet_needs,
)


def compute_comment_statistics(comments_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute statistics from user comments (TikTok + Reddit).
    
    Args:
        comments_df: Combined DataFrame of processed comments
        
    Returns:
        Dictionary with comment-based insights
    """
    if comments_df.empty:
        return {
            'potential_reasons_to_buy': [],
            'potential_reasons_not_to_buy': [],
            'usage_scenarios': [],
            'user_segments': [],
        }
    
    # Categorize comments
    categories = categorize_comments(comments_df)
    
    # Format for JSON output
    result = {
        'total_comments': len(comments_df),
        'tiktok_comments': len(comments_df[comments_df['source'] == 'tiktok']),
        'reddit_comments': len(comments_df[comments_df['source'] == 'reddit']),
    }
    
    # Extract top reasons to buy
    result['potential_reasons_to_buy'] = [
        {
            'reason': item['text'][:150],
            'engagement_score': int(item['likes']),
        }
        for item in categories.get('reasons_to_buy', [])[:5]
    ]
    
    # Extract top reasons not to buy
    result['potential_reasons_not_to_buy'] = [
        {
            'reason': item['text'][:150],
            'engagement_score': int(item['likes']),
        }
        for item in categories.get('reasons_not_to_buy', [])[:5]
    ]
    
    # Extract usage scenarios
    result['usage_scenarios'] = [
        {
            'scenario': item['text'][:150],
            'engagement_score': int(item['likes']),
        }
        for item in categories.get('usage_scenarios', [])[:5]
    ]
    
    # Extract user segments
    segments_by_type = {}
    for item in categories.get('user_segments', []):
        segment = item['segment']
        if segment not in segments_by_type:
            segments_by_type[segment] = {
                'segment': segment,
                'mention_count': 0,
                'examples': []
            }
        segments_by_type[segment]['mention_count'] += 1
        if len(segments_by_type[segment]['examples']) < 2:
            segments_by_type[segment]['examples'].append(item['text'][:100])
    
    result['user_segments'] = sorted(
        list(segments_by_type.values()),
        key=lambda x: x['mention_count'],
        reverse=True
    )[:5]
    
    return result


def compute_review_statistics(reviews_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute statistics from product reviews (Amazon + TikTok Shop).
    
    Args:
        reviews_df: Combined DataFrame of processed reviews
        
    Returns:
        Dictionary with review-based insights
    """
    if reviews_df.empty:
        return {
            'must_have_factors': [],
            'critical_pitfalls': [],
            'usage_scenarios': [],
            'unmet_needs': [],
        }
    
    result = {
        'total_reviews': len(reviews_df),
        'amazon_reviews': len(reviews_df[reviews_df['platform'] == 'amazon']),
        'tiktok_reviews': len(reviews_df[reviews_df['platform'] == 'tiktok']),
        'avg_rating': float(reviews_df['rating'].mean()),
    }
    
    # Extract must-have factors
    must_haves = extract_must_have_factors(reviews_df)
    result['must_have_factors'] = [
        {
            'factor': item['factor'],
            'mention_count': item['mention_count'],
            'top_examples': [ex['text'] for ex in item['examples'][:2]],
        }
        for item in must_haves
    ]
    
    # Extract critical pitfalls
    pitfalls = extract_critical_pitfalls(reviews_df)
    result['critical_pitfalls'] = [
        {
            'pitfall': item['pitfall'],
            'mention_count': item['mention_count'],
            'top_examples': [ex['text'] for ex in item['examples'][:2]],
        }
        for item in pitfalls
    ]
    
    # Extract usage scenarios
    scenarios = extract_review_usage_scenarios(reviews_df)
    result['usage_scenarios'] = [
        {
            'scenario': item['scenario'],
            'mention_count': item['mention_count'],
            'avg_rating': float(item['avg_rating']),
        }
        for item in scenarios
    ]
    
    # Extract unmet needs
    unmet = extract_unmet_needs(reviews_df)
    result['unmet_needs'] = [
        {
            'need': item['need'],
            'mention_count': item['mention_count'],
        }
        for item in unmet
    ]
    
    return result


def compare_platforms(reviews_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare review patterns between Amazon and TikTok Shop.
    
    Args:
        reviews_df: Combined DataFrame of processed reviews
        
    Returns:
        Dictionary with platform comparison insights
    """
    if reviews_df.empty:
        return {}
    
    amazon_reviews = reviews_df[reviews_df['platform'] == 'amazon']
    tiktok_reviews = reviews_df[reviews_df['platform'] == 'tiktok']
    
    comparison = {}
    
    if not amazon_reviews.empty and not tiktok_reviews.empty:
        # Rating comparison
        comparison['rating_comparison'] = {
            'amazon_avg': float(amazon_reviews['rating'].mean()),
            'tiktok_avg': float(tiktok_reviews['rating'].mean()),
            'difference': float(amazon_reviews['rating'].mean() - tiktok_reviews['rating'].mean()),
        }
        
        # Sentiment distribution
        comparison['sentiment_distribution'] = {
            'amazon': {
                'positive': len(amazon_reviews[amazon_reviews['rating'] >= 4]),
                'neutral': len(amazon_reviews[(amazon_reviews['rating'] >= 3) & (amazon_reviews['rating'] < 4)]),
                'negative': len(amazon_reviews[amazon_reviews['rating'] < 3]),
            },
            'tiktok': {
                'positive': len(tiktok_reviews[tiktok_reviews['rating'] >= 4]),
                'neutral': len(tiktok_reviews[(tiktok_reviews['rating'] >= 3) & (tiktok_reviews['rating'] < 4)]),
                'negative': len(tiktok_reviews[tiktok_reviews['rating'] < 3]),
            }
        }
        
        # Extract platform-specific factors
        amazon_factors = extract_must_have_factors(amazon_reviews)
        tiktok_factors = extract_must_have_factors(tiktok_reviews)
        
        amazon_factor_names = {f['factor'] for f in amazon_factors}
        tiktok_factor_names = {f['factor'] for f in tiktok_factors}
        
        comparison['key_differences'] = {
            'unique_to_amazon': list(amazon_factor_names - tiktok_factor_names)[:3],
            'unique_to_tiktok': list(tiktok_factor_names - amazon_factor_names)[:3],
            'common_factors': list(amazon_factor_names & tiktok_factor_names)[:3],
        }
    
    return comparison


def compute_voc_statistics(
    comments_df: Optional[pd.DataFrame] = None,
    reviews_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Compute comprehensive Voice of Customer statistics.
    
    Args:
        comments_df: Combined DataFrame of processed comments (TikTok + Reddit)
        reviews_df: Combined DataFrame of processed reviews (Amazon + TikTok)
        
    Returns:
        Complete VOC statistics JSON structure
    """
    statistics = {
        'timestamp': pd.Timestamp.now().isoformat(),
    }
    
    # Stage 2: Comments-based insights
    if comments_df is not None and not comments_df.empty:
        statistics['stage2_comments'] = compute_comment_statistics(comments_df)
    else:
        statistics['stage2_comments'] = {
            'potential_reasons_to_buy': [],
            'potential_reasons_not_to_buy': [],
            'usage_scenarios': [],
            'user_segments': [],
        }
    
    # Stage 3: Reviews-based insights
    if reviews_df is not None and not reviews_df.empty:
        statistics['stage3_reviews'] = compute_review_statistics(reviews_df)
        statistics['stage3_reviews']['platform_comparison'] = compare_platforms(reviews_df)
    else:
        statistics['stage3_reviews'] = {
            'must_have_factors': [],
            'critical_pitfalls': [],
            'usage_scenarios': [],
            'unmet_needs': [],
            'platform_comparison': {},
        }
    
    return statistics
