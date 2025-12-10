"""
Reddit Comments Fetching and Processing

This module fetches and processes Reddit threads and comments
to extract user insights and opinions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import os
from datetime import datetime
import re


def fetch_reddit_comments(
    keywords: List[str],
    subreddits: Optional[List[str]] = None,
    limit: int = 100
) -> pd.DataFrame:
    """
    Fetch Reddit comments based on keywords.
    
    Args:
        keywords: List of keywords to search for
        subreddits: List of subreddits to search in (optional)
        limit: Maximum number of comments to fetch
        
    Returns:
        DataFrame with Reddit comments
        
    Note:
        Requires Reddit API credentials set in environment variables:
        - REDDIT_CLIENT_ID
        - REDDIT_CLIENT_SECRET
        - REDDIT_USER_AGENT
    """
    comments_data = []
    
    try:
        import praw
        
        # Initialize Reddit API client
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID', ''),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET', ''),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'AutoReport/1.0')
        )
        
        # Default subreddits if none provided
        if not subreddits:
            subreddits = ['all']
        
        for keyword in keywords:
            for subreddit_name in subreddits:
                subreddit = reddit.subreddit(subreddit_name)
                
                # Search for posts containing the keyword
                for submission in subreddit.search(keyword, limit=limit // len(keywords) // len(subreddits)):
                    # Get top-level comments
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list()[:20]:
                        if isinstance(comment, praw.models.Comment):
                            comments_data.append({
                                'text': comment.body,
                                'upvotes': comment.score,
                                'created_at': datetime.fromtimestamp(comment.created_utc),
                                'user_id': str(comment.author) if comment.author else 'deleted',
                                'subreddit': subreddit_name,
                                'post_title': submission.title,
                            })
    
    except ImportError:
        print("Warning: praw library not installed. Reddit fetching disabled.")
        print("Install with: pip install praw")
    except Exception as e:
        print(f"Error fetching Reddit comments: {e}")
        print("Make sure REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT are set.")
    
    if not comments_data:
        # Return empty DataFrame with expected structure
        return pd.DataFrame(columns=['text', 'upvotes', 'created_at', 'user_id', 'source'])
    
    df = pd.DataFrame(comments_data)
    df['source'] = 'reddit'
    
    return df


def process_reddit_comments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process and clean Reddit comments.
    
    Args:
        df: Raw DataFrame with Reddit comments
        
    Returns:
        Normalized DataFrame with cleaned comments
    """
    if df.empty:
        return pd.DataFrame(columns=['text', 'likes', 'created_at', 'source'])
    
    # Normalize structure to match TikTok comments
    normalized = pd.DataFrame()
    
    normalized['text'] = df['text'].astype(str).apply(clean_reddit_text)
    normalized['likes'] = df.get('upvotes', 0)
    
    if 'created_at' in df.columns:
        normalized['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    
    normalized['source'] = 'reddit'
    
    # Filter valid comments
    normalized = normalized[normalized['text'].str.len() >= 5]
    
    return normalized


def clean_reddit_text(text: str) -> str:
    """
    Clean Reddit comment text.
    
    Args:
        text: Raw comment text
        
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove Reddit-specific formatting
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Remove markdown links
    text = re.sub(r'/u/\w+', '', text)  # Remove user mentions
    text = re.sub(r'/r/\w+', '', text)  # Remove subreddit mentions
    text = re.sub(r'\*\*?', '', text)  # Remove bold markers
    text = re.sub(r'~~', '', text)  # Remove strikethrough
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def combine_comments(tiktok_df: pd.DataFrame, reddit_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine TikTok and Reddit comments into a single DataFrame.
    
    Args:
        tiktok_df: Processed TikTok comments
        reddit_df: Processed Reddit comments
        
    Returns:
        Combined DataFrame
    """
    # Ensure both DataFrames have the same columns
    required_cols = ['text', 'likes', 'source']
    
    for df in [tiktok_df, reddit_df]:
        for col in required_cols:
            if col not in df.columns:
                if col == 'likes':
                    df[col] = 0
                else:
                    df[col] = ''
    
    combined = pd.concat([tiktok_df, reddit_df], ignore_index=True)
    
    return combined
