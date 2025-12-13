"""
Data Pipeline Module

This module handles all data processing tasks including:
- Platform data cleaning and normalization
- Statistical computations
- Voice of Customer (VOC) analysis
- Market landscape analysis

All data processing is deterministic and done in Python.
LLMs only receive structured JSON outputs from these modules.
"""

from .clean_amazon_sales import clean_amazon_sales
from .clean_tiktok_sales import clean_tiktok_sales
from .comments_tiktok import clean_tiktok_comments, summarize_tiktok_comments
from .comments_reddit import clean_reddit_comments, summarize_reddit_comments
from .reviews_amazon import clean_amazon_reviews, summarize_amazon_reviews
from .reviews_tiktok import clean_tiktok_reviews, summarize_tiktok_reviews
from .market_statistics import compute_market_statistics
from .voc_statistics import (
    compute_voc_statistics,
    compute_comment_statistics,
    compute_review_statistics
)

__all__ = [
    'clean_amazon_sales',
    'clean_tiktok_sales',
    'clean_tiktok_comments',
    'summarize_tiktok_comments',
    'clean_reddit_comments',
    'summarize_reddit_comments',
    'clean_amazon_reviews',
    'summarize_amazon_reviews',
    'clean_tiktok_reviews',
    'summarize_tiktok_reviews',
    'compute_market_statistics',
    'compute_voc_statistics',
    'compute_comment_statistics',
    'compute_review_statistics',
]
