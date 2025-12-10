"""
Chart Generation Utilities

This module provides functions to generate various charts for data visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def plot_price_distribution(df: pd.DataFrame, platform: str = "") -> go.Figure:
    """
    Plot price distribution histogram.
    
    Args:
        df: DataFrame with 'price' column
        platform: Platform name for title
        
    Returns:
        Plotly figure
    """
    if df.empty or 'price' not in df.columns:
        return go.Figure()
    
    fig = px.histogram(
        df,
        x='price',
        nbins=30,
        title=f'Price Distribution{" - " + platform if platform else ""}',
        labels={'price': 'Price ($)', 'count': 'Number of Products'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_title='Price ($)',
        yaxis_title='Number of Products',
    )
    
    return fig


def plot_sales_by_price_band(price_bands: List[Dict[str, Any]]) -> go.Figure:
    """
    Plot sales by price band.
    
    Args:
        price_bands: List of price band dictionaries
        
    Returns:
        Plotly figure
    """
    if not price_bands:
        return go.Figure()
    
    # Extract data
    labels = [f"${band['price_range']['min']:.0f}-${band['price_range']['max']:.0f}" 
              for band in price_bands]
    sales = [band['total_sales'] for band in price_bands]
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=sales,
            marker_color='#2ca02c'
        )
    ])
    
    fig.update_layout(
        title='Sales by Price Band',
        xaxis_title='Price Range',
        yaxis_title='Total Sales',
        showlegend=False,
    )
    
    return fig


def plot_rating_distribution(rating_profile: Dict[str, Any]) -> go.Figure:
    """
    Plot rating distribution.
    
    Args:
        rating_profile: Rating profile dictionary
        
    Returns:
        Plotly figure
    """
    if not rating_profile or 'rating_distribution' not in rating_profile:
        return go.Figure()
    
    dist = rating_profile['rating_distribution']
    
    categories = [item['category'] for item in dist]
    counts = [item['product_count'] for item in dist]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=counts,
            marker_color='#ff7f0e'
        )
    ])
    
    fig.update_layout(
        title='Rating Distribution',
        xaxis_title='Rating Category',
        yaxis_title='Number of Products',
        showlegend=False,
    )
    
    return fig


def plot_competition_metrics(competition: Dict[str, Any]) -> go.Figure:
    """
    Plot competition metrics (market concentration).
    
    Args:
        competition: Competition metrics dictionary
        
    Returns:
        Plotly figure
    """
    if not competition:
        return go.Figure()
    
    metrics = []
    values = []
    
    if 'top10_share' in competition:
        metrics.append('Top 10 Products')
        values.append(competition['top10_share'] * 100)
    
    if 'top20_share' in competition:
        metrics.append('Top 20 Products')
        values.append(competition['top20_share'] * 100)
    
    if 'long_tail_index' in competition:
        metrics.append('Long Tail')
        values.append(competition['long_tail_index'] * 100)
    
    if not metrics:
        return go.Figure()
    
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            marker_color=['#d62728', '#9467bd', '#8c564b']
        )
    ])
    
    fig.update_layout(
        title='Market Concentration',
        xaxis_title='Metric',
        yaxis_title='Percentage (%)',
        showlegend=False,
    )
    
    return fig


def plot_feature_performance(features: List[Dict[str, Any]], top_n: int = 10) -> go.Figure:
    """
    Plot top features by sales.
    
    Args:
        features: List of feature performance dictionaries
        top_n: Number of top features to show
        
    Returns:
        Plotly figure
    """
    if not features:
        return go.Figure()
    
    # Get top N features
    top_features = features[:top_n]
    
    feature_names = [f['feature'] for f in top_features]
    sales = [f['total_sales'] for f in top_features]
    
    fig = go.Figure(data=[
        go.Bar(
            y=feature_names[::-1],  # Reverse for better readability
            x=sales[::-1],
            orientation='h',
            marker_color='#17becf'
        )
    ])
    
    fig.update_layout(
        title=f'Top {top_n} Features by Sales',
        xaxis_title='Total Sales',
        yaxis_title='Feature',
        height=max(400, top_n * 40),
        showlegend=False,
    )
    
    return fig


def plot_platform_comparison(cross_platform: Dict[str, Any]) -> go.Figure:
    """
    Plot cross-platform comparison.
    
    Args:
        cross_platform: Cross-platform comparison dictionary
        
    Returns:
        Plotly figure with subplots
    """
    if not cross_platform:
        return go.Figure()
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Product Count', 'Total Sales',
            'Average Price', 'Average Rating'
        ),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    platforms = ['Amazon', 'TikTok']
    colors = ['#1f77b4', '#ff7f0e']
    
    # Product count
    if 'volume_comparison' in cross_platform:
        vol = cross_platform['volume_comparison']
        fig.add_trace(
            go.Bar(
                x=platforms,
                y=[vol.get('amazon_products', 0), vol.get('tiktok_products', 0)],
                marker_color=colors,
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Total sales
        fig.add_trace(
            go.Bar(
                x=platforms,
                y=[vol.get('amazon_sales', 0), vol.get('tiktok_sales', 0)],
                marker_color=colors,
                showlegend=False
            ),
            row=1, col=2
        )
    
    # Average price
    if 'price_comparison' in cross_platform:
        price = cross_platform['price_comparison']
        fig.add_trace(
            go.Bar(
                x=platforms,
                y=[price.get('amazon_avg', 0), price.get('tiktok_avg', 0)],
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )
    
    # Average rating
    if 'rating_comparison' in cross_platform:
        rating = cross_platform['rating_comparison']
        fig.add_trace(
            go.Bar(
                x=platforms,
                y=[rating.get('amazon_avg', 0), rating.get('tiktok_avg', 0)],
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        title_text='Platform Comparison',
        height=600,
        showlegend=False
    )
    
    return fig


def plot_voc_summary(voc_stats: Dict[str, Any]) -> go.Figure:
    """
    Plot Voice of Customer summary statistics.
    
    Args:
        voc_stats: VOC statistics dictionary
        
    Returns:
        Plotly figure
    """
    if not voc_stats:
        return go.Figure()
    
    # Create summary metrics
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Comment Sources', 'Review Sentiment'),
        specs=[[{'type': 'pie'}, {'type': 'pie'}]]
    )
    
    # Comments pie chart
    if 'stage2_comments' in voc_stats:
        comments = voc_stats['stage2_comments']
        fig.add_trace(
            go.Pie(
                labels=['TikTok', 'Reddit'],
                values=[
                    comments.get('tiktok_comments', 0),
                    comments.get('reddit_comments', 0)
                ],
                marker_colors=['#ff6b6b', '#4ecdc4']
            ),
            row=1, col=1
        )
    
    # Reviews pie chart
    if 'stage3_reviews' in voc_stats:
        reviews = voc_stats['stage3_reviews']
        fig.add_trace(
            go.Pie(
                labels=['Amazon', 'TikTok'],
                values=[
                    reviews.get('amazon_reviews', 0),
                    reviews.get('tiktok_reviews', 0)
                ],
                marker_colors=['#ff9f1c', '#2ec4b6']
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title_text='Voice of Customer Overview',
        height=400,
    )
    
    return fig
