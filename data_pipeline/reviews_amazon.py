"""
Amazon Product Reviews Processing

This module processes Amazon product reviews to extract post-purchase feedback,
must-have factors, critical pitfalls, and unmet needs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from collections import Counter
import re


def detect_amazon_review_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect Amazon review columns by matching common patterns.
    
    Args:
        df: Raw DataFrame from uploaded Amazon reviews file
        
    Returns:
        Dictionary mapping standardized field names to actual column names
    """
    column_mapping = {}
    
    patterns = {
        'product_id': ['asin', 'product_id', 'product id'],
        'text': ['text', 'review_text', 'review', 'body', 'comment'],
        'rating': ['rating', 'star_rating', 'stars', 'score'],
        'helpful': ['helpful', 'helpful_count', 'helpful_votes', 'upvotes'],
        'date': ['date', 'review_date', 'created_at', 'timestamp'],
        'country': ['country', 'location', 'marketplace'],
        'title': ['title', 'review_title', 'summary'],
        'verified': ['verified', 'verified_purchase'],
    }
    
    df_columns_lower = {col.lower(): col for col in df.columns}
    
    for field, keywords in patterns.items():
        for keyword in keywords:
            if keyword in df_columns_lower:
                column_mapping[field] = df_columns_lower[keyword]
                break
    
    return column_mapping


def process_amazon_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process and normalize Amazon product reviews.
    
    Args:
        df: Raw DataFrame from uploaded Amazon reviews file
        
    Returns:
        Normalized DataFrame with processed reviews
    """
    # Detect column mappings
    column_mapping = detect_amazon_review_columns(df)
    
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
    
    if 'title' in column_mapping:
        normalized['title'] = df[column_mapping['title']].astype(str)
    
    if 'verified' in column_mapping:
        normalized['verified'] = df[column_mapping['verified']].astype(bool)
    else:
        # Assume all are verified if not specified
        normalized['verified'] = True
    
    # Add platform identifier
    normalized['platform'] = 'amazon'
    
    # Filter valid reviews (with text)
    normalized = normalized[normalized['text'].str.len() >= 10]
    
    return normalized


def clean_review_text(text: str) -> str:
    """
    Clean review text.
    
    Args:
        text: Raw review text
        
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'([!?.]){3,}', r'\1\1', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def extract_must_have_factors(reviews: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Extract must-have factors from positive reviews (4-5 stars).
    
    Args:
        reviews: DataFrame of processed reviews
        
    Returns:
        List of must-have factors with supporting evidence
    """
    # Filter positive reviews
    positive_reviews = reviews[reviews['rating'] >= 4].copy()
    
    if positive_reviews.empty:
        return []
    
    # Keywords indicating key factors
    factor_keywords = {
        'quality': ['quality', 'well made', 'durable', 'sturdy', 'solid'],
        'price_value': ['worth', 'value', 'price', 'affordable', 'reasonable'],
        'easy_use': ['easy', 'simple', 'convenient', 'straightforward', 'user-friendly'],
        'performance': ['works', 'performs', 'effective', 'efficient', 'reliable'],
        'appearance': ['looks', 'beautiful', 'attractive', 'gorgeous', 'pretty'],
        'comfort': ['comfortable', 'soft', 'cozy', 'fit', 'smooth'],
        'fast_shipping': ['fast', 'quick', 'arrived', 'delivery', 'shipping'],
    }
    
    factors = []
    for factor_name, keywords in factor_keywords.items():
        mentions = []
        for _, review in positive_reviews.iterrows():
            text_lower = review['text'].lower()
            if any(kw in text_lower for kw in keywords):
                mentions.append({
                    'text': review['text'][:200],  # First 200 chars
                    'rating': review['rating'],
                    'helpful': review.get('helpful', 0),
                })
        
        if mentions:
            # Sort by helpful votes and rating
            mentions = sorted(
                mentions,
                key=lambda x: (x['helpful'], x['rating']),
                reverse=True
            )[:3]
            
            factors.append({
                'factor': factor_name,
                'mention_count': len(mentions),
                'examples': mentions,
            })
    
    # Sort factors by mention count
    factors = sorted(factors, key=lambda x: x['mention_count'], reverse=True)
    
    return factors[:5]


def extract_critical_pitfalls(reviews: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Extract critical pitfalls from negative reviews (1-2 stars).
    
    Args:
        reviews: DataFrame of processed reviews
        
    Returns:
        List of critical pitfalls with examples
    """
    # Filter negative reviews
    negative_reviews = reviews[reviews['rating'] <= 2].copy()
    
    if negative_reviews.empty:
        return []
    
    # Keywords indicating problems
    pitfall_keywords = {
        'poor_quality': ['poor quality', 'cheap', 'broke', 'broken', 'fall apart', 'defective'],
        'not_as_described': ['not as described', 'misleading', 'different', 'wrong', 'not what'],
        'bad_fit': ['doesn\'t fit', 'too small', 'too large', 'wrong size', 'uncomfortable'],
        'delivery_issues': ['late', 'damaged', 'never arrived', 'shipping', 'package'],
        'overpriced': ['overpriced', 'too expensive', 'not worth', 'waste of money'],
        'difficult_use': ['difficult', 'hard to use', 'complicated', 'confusing'],
        'bad_smell': ['smell', 'odor', 'stink', 'chemical'],
    }
    
    pitfalls = []
    for pitfall_name, keywords in pitfall_keywords.items():
        mentions = []
        for _, review in negative_reviews.iterrows():
            text_lower = review['text'].lower()
            if any(kw in text_lower for kw in keywords):
                mentions.append({
                    'text': review['text'][:200],
                    'rating': review['rating'],
                    'helpful': review.get('helpful', 0),
                })
        
        if mentions:
            mentions = sorted(
                mentions,
                key=lambda x: (x['helpful'], -x['rating']),
                reverse=True
            )[:3]
            
            pitfalls.append({
                'pitfall': pitfall_name,
                'mention_count': len(mentions),
                'examples': mentions,
            })
    
    # Sort by mention count
    pitfalls = sorted(pitfalls, key=lambda x: x['mention_count'], reverse=True)
    
    return pitfalls[:5]


def extract_usage_scenarios(reviews: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Extract usage scenarios from reviews.
    
    Args:
        reviews: DataFrame of processed reviews
        
    Returns:
        List of usage scenarios
    """
    usage_keywords = {
        'daily_use': ['daily', 'everyday', 'regular', 'routine'],
        'special_occasions': ['wedding', 'party', 'event', 'occasion', 'celebration'],
        'professional': ['work', 'office', 'professional', 'business', 'meeting'],
        'outdoor': ['outdoor', 'outside', 'hiking', 'camping', 'travel'],
        'home': ['home', 'house', 'indoor', 'bedroom', 'living room'],
    }
    
    scenarios = []
    for scenario_name, keywords in usage_keywords.items():
        mentions = []
        for _, review in reviews.iterrows():
            text_lower = review['text'].lower()
            if any(kw in text_lower for kw in keywords):
                mentions.append({
                    'text': review['text'][:200],
                    'rating': review['rating'],
                })
        
        if mentions:
            scenarios.append({
                'scenario': scenario_name,
                'mention_count': len(mentions),
                'avg_rating': np.mean([m['rating'] for m in mentions]),
            })
    
    scenarios = sorted(scenarios, key=lambda x: x['mention_count'], reverse=True)
    
    return scenarios[:5]


def extract_unmet_needs(reviews: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Extract unmet needs and feature requests from reviews.
    
    Args:
        reviews: DataFrame of processed reviews
        
    Returns:
        List of unmet needs
    """
    # Keywords indicating unmet needs
    need_patterns = [
        r'wish (?:it|there) (?:was|were|had)',
        r'would be (?:better|nice|great) if',
        r'should have',
        r'needs? (?:to|more)',
        r'missing',
        r'lacking',
        r'could use',
    ]
    
    unmet_needs = []
    for _, review in reviews.iterrows():
        text = review['text']
        for pattern in need_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                # Extract sentence containing the match
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                snippet = text[start:end].strip()
                
                unmet_needs.append({
                    'text': snippet,
                    'rating': review['rating'],
                })
    
    # Group similar needs (simplified)
    if not unmet_needs:
        return []
    
    # Return top unmet needs by frequency
    need_texts = [need['text'] for need in unmet_needs]
    common_needs = Counter(need_texts).most_common(5)
    
    result = []
    for text, count in common_needs:
        result.append({
            'need': text,
            'mention_count': count,
        })
    
    return result
