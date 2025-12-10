"""
Auto-Report: Cross-Border E-Commerce Market Analysis

Main Streamlit application providing a 4-stage workflow for market analysis
with multi-LLM debate for final report generation.
"""

import streamlit as st
import pandas as pd
import json
import os
from typing import Optional, Dict, Any

# Import data pipeline modules
from data_pipeline.clean_amazon_sales import clean_amazon_sales
from data_pipeline.clean_tiktok_sales import clean_tiktok_sales
from data_pipeline.comments_tiktok import process_tiktok_comments
from data_pipeline.comments_reddit import fetch_reddit_comments, process_reddit_comments, combine_comments
from data_pipeline.reviews_amazon import process_amazon_reviews
from data_pipeline.reviews_tiktok import process_tiktok_reviews, combine_reviews
from data_pipeline.market_statistics import compute_market_statistics
from data_pipeline.voc_statistics import compute_voc_statistics

# Import AI modules
from ai.debate_orchestrator import DebateOrchestrator, create_master_summary
from ai.llm_clients import get_llm_client

# Import visualization
from visualization.charts import (
    plot_price_distribution,
    plot_sales_by_price_band,
    plot_rating_distribution,
    plot_competition_metrics,
    plot_feature_performance,
    plot_platform_comparison,
    plot_voc_summary,
)


# Page configuration
st.set_page_config(
    page_title="Auto-Report: Market Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 1
if 'amazon_sales_df' not in st.session_state:
    st.session_state.amazon_sales_df = None
if 'tiktok_sales_df' not in st.session_state:
    st.session_state.tiktok_sales_df = None
if 'comments_df' not in st.session_state:
    st.session_state.comments_df = None
if 'reviews_df' not in st.session_state:
    st.session_state.reviews_df = None
if 'market_stats' not in st.session_state:
    st.session_state.market_stats = None
if 'voc_stats' not in st.session_state:
    st.session_state.voc_stats = None
if 'debate_results' not in st.session_state:
    st.session_state.debate_results = None


def load_data_file(uploaded_file) -> Optional[pd.DataFrame]:
    """Load CSV or XLSX file into DataFrame."""
    if uploaded_file is None:
        return None
    
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file format: {uploaded_file.name}")
            return None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def stage1_market_landscape():
    """Stage 1: Market Landscape (Sales Data)"""
    st.header("📈 Stage 1: Market Landscape")
    st.markdown("""
    Upload Amazon and/or TikTok Shop sales data to analyze market size, competition,
    price distribution, and product features.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Amazon Sales Data")
        amazon_file = st.file_uploader(
            "Upload Amazon sales CSV/XLSX",
            type=['csv', 'xlsx', 'xls'],
            key='amazon_sales'
        )
        
        if amazon_file:
            with st.spinner("Processing Amazon data..."):
                raw_df = load_data_file(amazon_file)
                if raw_df is not None:
                    st.session_state.amazon_sales_df = clean_amazon_sales(raw_df)
                    st.success(f"✅ Loaded {len(st.session_state.amazon_sales_df)} Amazon products")
                    with st.expander("Preview data"):
                        st.dataframe(st.session_state.amazon_sales_df.head())
    
    with col2:
        st.subheader("TikTok Shop Sales Data")
        tiktok_file = st.file_uploader(
            "Upload TikTok Shop sales CSV/XLSX",
            type=['csv', 'xlsx', 'xls'],
            key='tiktok_sales'
        )
        
        if tiktok_file:
            with st.spinner("Processing TikTok data..."):
                raw_df = load_data_file(tiktok_file)
                if raw_df is not None:
                    st.session_state.tiktok_sales_df = clean_tiktok_sales(raw_df)
                    st.success(f"✅ Loaded {len(st.session_state.tiktok_sales_df)} TikTok products")
                    with st.expander("Preview data"):
                        st.dataframe(st.session_state.tiktok_sales_df.head())
    
    # Compute statistics button
    if st.session_state.amazon_sales_df is not None or st.session_state.tiktok_sales_df is not None:
        if st.button("🔬 Compute Market Statistics", type="primary"):
            with st.spinner("Computing market statistics..."):
                st.session_state.market_stats = compute_market_statistics(
                    amazon_df=st.session_state.amazon_sales_df,
                    tiktok_df=st.session_state.tiktok_sales_df
                )
                st.success("✅ Market statistics computed!")
                st.session_state.stage = 2
                st.rerun()


def stage2_comments_analysis():
    """Stage 2: Comments Analysis (TikTok + Reddit)"""
    st.header("💬 Stage 2: User Comments Analysis")
    st.markdown("""
    Upload TikTok video comments and optionally fetch Reddit comments to understand
    user opinions, reasons to buy/not buy, and usage scenarios.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("TikTok Comments")
        tiktok_comments_file = st.file_uploader(
            "Upload TikTok comments CSV/XLSX",
            type=['csv', 'xlsx', 'xls'],
            key='tiktok_comments'
        )
        
        tiktok_df = None
        if tiktok_comments_file:
            with st.spinner("Processing TikTok comments..."):
                raw_df = load_data_file(tiktok_comments_file)
                if raw_df is not None:
                    tiktok_df = process_tiktok_comments(raw_df)
                    st.success(f"✅ Loaded {len(tiktok_df)} TikTok comments")
    
    with col2:
        st.subheader("Reddit Comments (Optional)")
        
        with st.expander("Fetch from Reddit API"):
            st.info("Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT in environment")
            
            keywords = st.text_input("Keywords (comma-separated)", "")
            subreddits = st.text_input("Subreddits (comma-separated, or leave empty for all)", "")
            
            if st.button("Fetch Reddit Comments"):
                if keywords:
                    keyword_list = [k.strip() for k in keywords.split(',')]
                    subreddit_list = [s.strip() for s in subreddits.split(',')] if subreddits else None
                    
                    with st.spinner("Fetching Reddit comments..."):
                        reddit_raw = fetch_reddit_comments(keyword_list, subreddit_list)
                        if not reddit_raw.empty:
                            reddit_df = process_reddit_comments(reddit_raw)
                            st.success(f"✅ Fetched {len(reddit_df)} Reddit comments")
                        else:
                            st.warning("No Reddit comments fetched. Check API credentials.")
                            reddit_df = pd.DataFrame()
                else:
                    st.warning("Please enter keywords")
                    reddit_df = pd.DataFrame()
        
        reddit_file = st.file_uploader(
            "Or upload Reddit comments CSV/XLSX",
            type=['csv', 'xlsx', 'xls'],
            key='reddit_comments'
        )
        
        reddit_df = None
        if reddit_file:
            with st.spinner("Processing Reddit comments..."):
                raw_df = load_data_file(reddit_file)
                if raw_df is not None:
                    reddit_df = process_reddit_comments(raw_df)
                    st.success(f"✅ Loaded {len(reddit_df)} Reddit comments")
    
    # Combine and proceed
    if tiktok_df is not None:
        if reddit_df is not None and not reddit_df.empty:
            st.session_state.comments_df = combine_comments(tiktok_df, reddit_df)
        else:
            st.session_state.comments_df = tiktok_df
        
        st.info(f"Total comments: {len(st.session_state.comments_df)}")
        
        if st.button("Next: Product Reviews", type="primary"):
            st.session_state.stage = 3
            st.rerun()


def stage3_reviews_analysis():
    """Stage 3: Product Reviews Analysis"""
    st.header("⭐ Stage 3: Product Reviews Analysis")
    st.markdown("""
    Upload Amazon and/or TikTok Shop product reviews to extract must-have factors,
    critical pitfalls, and unmet needs.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Amazon Reviews")
        amazon_reviews_file = st.file_uploader(
            "Upload Amazon reviews CSV/XLSX",
            type=['csv', 'xlsx', 'xls'],
            key='amazon_reviews'
        )
        
        amazon_reviews_df = None
        if amazon_reviews_file:
            with st.spinner("Processing Amazon reviews..."):
                raw_df = load_data_file(amazon_reviews_file)
                if raw_df is not None:
                    amazon_reviews_df = process_amazon_reviews(raw_df)
                    st.success(f"✅ Loaded {len(amazon_reviews_df)} Amazon reviews")
    
    with col2:
        st.subheader("TikTok Shop Reviews")
        tiktok_reviews_file = st.file_uploader(
            "Upload TikTok reviews CSV/XLSX",
            type=['csv', 'xlsx', 'xls'],
            key='tiktok_reviews'
        )
        
        tiktok_reviews_df = None
        if tiktok_reviews_file:
            with st.spinner("Processing TikTok reviews..."):
                raw_df = load_data_file(tiktok_reviews_file)
                if raw_df is not None:
                    tiktok_reviews_df = process_tiktok_reviews(raw_df)
                    st.success(f"✅ Loaded {len(tiktok_reviews_df)} TikTok reviews")
    
    # Combine reviews
    if amazon_reviews_df is not None or tiktok_reviews_df is not None:
        if amazon_reviews_df is not None and tiktok_reviews_df is not None:
            st.session_state.reviews_df = combine_reviews(amazon_reviews_df, tiktok_reviews_df)
        elif amazon_reviews_df is not None:
            st.session_state.reviews_df = amazon_reviews_df
        else:
            st.session_state.reviews_df = tiktok_reviews_df
        
        st.info(f"Total reviews: {len(st.session_state.reviews_df)}")
        
        if st.button("🔬 Compute VOC Statistics", type="primary"):
            with st.spinner("Computing VOC statistics..."):
                st.session_state.voc_stats = compute_voc_statistics(
                    comments_df=st.session_state.comments_df,
                    reviews_df=st.session_state.reviews_df
                )
                st.success("✅ VOC statistics computed!")
                st.session_state.stage = 4
                st.rerun()


def stage4_debate_report():
    """Stage 4: Multi-Model Debate & Final Report"""
    st.header("🤖 Stage 4: Multi-Model Debate & Report Generation")
    st.markdown("""
    Two different LLM models will independently analyze all data, then a judge model
    will synthesize their insights into a final report in Chinese.
    """)
    
    # Check if we have data
    if st.session_state.market_stats is None and st.session_state.voc_stats is None:
        st.warning("⚠️ No data available. Please complete Stages 1-3 first.")
        return
    
    # LLM Configuration
    st.subheader("🔧 Configure LLM Providers")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analyst1_provider = st.selectbox(
            "Analyst 1 Provider",
            options=['openai', 'gemini', 'deepseek'],
            key='analyst1'
        )
        analyst1_key = st.text_input(
            f"{analyst1_provider.upper()} API Key (Analyst 1)",
            type='password',
            key='analyst1_key',
            help=f"Or set {analyst1_provider.upper()}_API_KEY environment variable"
        )
    
    with col2:
        analyst2_provider = st.selectbox(
            "Analyst 2 Provider",
            options=['openai', 'gemini', 'deepseek'],
            index=1,
            key='analyst2'
        )
        analyst2_key = st.text_input(
            f"{analyst2_provider.upper()} API Key (Analyst 2)",
            type='password',
            key='analyst2_key',
            help=f"Or set {analyst2_provider.upper()}_API_KEY environment variable"
        )
    
    with col3:
        judge_provider = st.selectbox(
            "Judge Provider",
            options=['same as analyst 1', 'openai', 'gemini', 'deepseek'],
            key='judge'
        )
        
        if judge_provider != 'same as analyst 1':
            judge_key = st.text_input(
                f"{judge_provider.upper()} API Key (Judge)",
                type='password',
                key='judge_key',
                help=f"Or set {judge_provider.upper()}_API_KEY environment variable"
            )
        else:
            judge_key = None
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input("Max Tokens", 1000, 8000, 4000, 500)
    
    # Run debate button
    if st.button("🚀 Run Multi-Model Debate", type="primary"):
        try:
            # Create master summary
            with st.spinner("Preparing data summary..."):
                master_summary = create_master_summary(
                    market_stats=st.session_state.market_stats,
                    voc_stats=st.session_state.voc_stats
                )
            
            # Initialize orchestrator
            with st.spinner("Initializing debate orchestrator..."):
                orchestrator = DebateOrchestrator(
                    analyst1_provider=analyst1_provider,
                    analyst2_provider=analyst2_provider,
                    judge_provider=None if judge_provider == 'same as analyst 1' else judge_provider,
                    analyst1_api_key=analyst1_key if analyst1_key else None,
                    analyst2_api_key=analyst2_key if analyst2_key else None,
                    judge_api_key=judge_key if judge_provider != 'same as analyst 1' and judge_key else None,
                )
            
            # Run debate
            st.session_state.debate_results = orchestrator.run_debate(
                data_summary=master_summary,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            st.success("✅ Debate completed!")
            st.rerun()
        
        except Exception as e:
            st.error(f"Error during debate: {str(e)}")
            st.error("Make sure API keys are correctly set in environment variables or input fields.")


def show_results():
    """Display analysis results and reports"""
    st.header("📊 Analysis Results")
    
    tabs = st.tabs([
        "📈 Market Overview",
        "💬 VOC Insights",
        "📊 Visualizations",
        "🤖 LLM Reports"
    ])
    
    # Tab 1: Market Overview
    with tabs[0]:
        if st.session_state.market_stats:
            st.subheader("Market Statistics")
            
            # Display market overview
            stats = st.session_state.market_stats
            
            if 'platforms' in stats:
                for platform, data in stats['platforms'].items():
                    with st.expander(f"{platform.upper()} Platform", expanded=True):
                        if 'market_overview' in data:
                            overview = data['market_overview']
                            
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Products", f"{overview.get('total_products', 0):,}")
                            col2.metric("Total Sales", f"{overview.get('total_sales', 0):,}")
                            col3.metric("Avg Price", f"${overview.get('avg_price', 0):.2f}")
                            col4.metric("Avg Rating", f"{overview.get('avg_rating', 0):.2f}⭐")
                        
                        # Show price bands
                        if 'price_bands' in data and data['price_bands']:
                            st.plotly_chart(
                                plot_sales_by_price_band(data['price_bands']),
                                use_container_width=True
                            )
            
            # Show JSON
            with st.expander("📄 View Raw JSON"):
                st.json(stats)
        else:
            st.info("No market statistics available. Complete Stage 1 first.")
    
    # Tab 2: VOC Insights
    with tabs[1]:
        if st.session_state.voc_stats:
            st.subheader("Voice of Customer Statistics")
            
            voc = st.session_state.voc_stats
            
            # Stage 2: Comments
            if 'stage2_comments' in voc:
                st.markdown("### 💬 Comments Analysis")
                comments = voc['stage2_comments']
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Comments", comments.get('total_comments', 0))
                col2.metric("TikTok", comments.get('tiktok_comments', 0))
                col3.metric("Reddit", comments.get('reddit_comments', 0))
                
                # Show top reasons
                if comments.get('potential_reasons_to_buy'):
                    st.markdown("**Top Reasons to Buy:**")
                    for i, reason in enumerate(comments['potential_reasons_to_buy'][:5], 1):
                        st.write(f"{i}. {reason['reason']} (👍 {reason['engagement_score']})")
            
            # Stage 3: Reviews
            if 'stage3_reviews' in voc:
                st.markdown("### ⭐ Reviews Analysis")
                reviews = voc['stage3_reviews']
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Reviews", reviews.get('total_reviews', 0))
                col2.metric("Amazon", reviews.get('amazon_reviews', 0))
                col3.metric("TikTok", reviews.get('tiktok_reviews', 0))
                
                # Show must-have factors
                if reviews.get('must_have_factors'):
                    st.markdown("**Must-Have Factors:**")
                    for factor in reviews['must_have_factors']:
                        st.write(f"- **{factor['factor']}** ({factor['mention_count']} mentions)")
            
            # Show JSON
            with st.expander("📄 View Raw JSON"):
                st.json(voc)
        else:
            st.info("No VOC statistics available. Complete Stages 2-3 first.")
    
    # Tab 3: Visualizations
    with tabs[2]:
        st.subheader("Data Visualizations")
        
        if st.session_state.market_stats and 'platforms' in st.session_state.market_stats:
            platforms = st.session_state.market_stats['platforms']
            
            # Platform comparison
            if 'cross_platform' in st.session_state.market_stats:
                st.plotly_chart(
                    plot_platform_comparison(st.session_state.market_stats['cross_platform']),
                    use_container_width=True
                )
            
            # Individual platform charts
            for platform, data in platforms.items():
                st.markdown(f"### {platform.upper()} Platform")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'rating_profile' in data:
                        st.plotly_chart(
                            plot_rating_distribution(data['rating_profile']),
                            use_container_width=True
                        )
                
                with col2:
                    if 'competition' in data:
                        st.plotly_chart(
                            plot_competition_metrics(data['competition']),
                            use_container_width=True
                        )
                
                if 'feature_performance' in data and data['feature_performance']:
                    st.plotly_chart(
                        plot_feature_performance(data['feature_performance']),
                        use_container_width=True
                    )
        
        if st.session_state.voc_stats:
            st.plotly_chart(
                plot_voc_summary(st.session_state.voc_stats),
                use_container_width=True
            )
    
    # Tab 4: LLM Reports
    with tabs[3]:
        if st.session_state.debate_results:
            st.subheader("Multi-Model Analysis Reports")
            
            results = st.session_state.debate_results
            metadata = results['metadata']
            reports = results['reports']
            
            # Show metadata
            col1, col2, col3 = st.columns(3)
            col1.info(f"**Analyst 1:** {metadata['analyst1']}")
            col2.info(f"**Analyst 2:** {metadata['analyst2']}")
            col3.info(f"**Judge:** {metadata['judge']}")
            
            # Show reports
            report_tabs = st.tabs(["📝 Final Report", "📊 Analyst 1", "📊 Analyst 2"])
            
            with report_tabs[0]:
                st.markdown("### 🏆 Final Synthesized Report")
                st.markdown(reports['final'])
                
                # Download button
                st.download_button(
                    label="📥 Download Final Report",
                    data=reports['final'],
                    file_name="market_analysis_report.md",
                    mime="text/markdown"
                )
            
            with report_tabs[1]:
                st.markdown(f"### Report from {metadata['analyst1']}")
                st.markdown(reports['analyst1'])
            
            with report_tabs[2]:
                st.markdown(f"### Report from {metadata['analyst2']}")
                st.markdown(reports['analyst2'])
            
            # Download all
            with st.expander("📥 Download All Results"):
                # Create comprehensive JSON
                full_results = {
                    'market_statistics': st.session_state.market_stats,
                    'voc_statistics': st.session_state.voc_stats,
                    'debate_results': results
                }
                
                st.download_button(
                    label="Download Complete Analysis (JSON)",
                    data=json.dumps(full_results, ensure_ascii=False, indent=2),
                    file_name="complete_analysis.json",
                    mime="application/json"
                )
        else:
            st.info("No LLM reports yet. Complete Stage 4 to generate reports.")


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.title("🚀 Auto-Report")
        st.markdown("**Cross-Border E-Commerce Market Analysis**")
        
        st.markdown("---")
        
        st.markdown("### 📋 Workflow Stages")
        
        stages = [
            "1️⃣ Market Landscape",
            "2️⃣ Comments Analysis",
            "3️⃣ Reviews Analysis",
            "4️⃣ Multi-Model Debate"
        ]
        
        for i, stage_name in enumerate(stages, 1):
            if i == st.session_state.stage:
                st.markdown(f"**{stage_name}** ✅")
            elif i < st.session_state.stage:
                st.markdown(f"~~{stage_name}~~ ✅")
            else:
                st.markdown(f"{stage_name}")
        
        st.markdown("---")
        
        # Stage navigation
        st.markdown("### 🔀 Navigation")
        selected_stage = st.selectbox(
            "Jump to stage:",
            options=[1, 2, 3, 4],
            index=st.session_state.stage - 1,
            format_func=lambda x: f"Stage {x}"
        )
        
        if selected_stage != st.session_state.stage:
            st.session_state.stage = selected_stage
            st.rerun()
        
        # View results button
        if st.button("📊 View Results", use_container_width=True):
            st.session_state.stage = 'results'
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        This app analyzes niche markets for cross-border e-commerce using:
        - Python for data processing
        - Multiple LLMs for analysis
        - Multi-model debate for insights
        """)
    
    # Main content
    if st.session_state.stage == 'results':
        show_results()
    elif st.session_state.stage == 1:
        stage1_market_landscape()
    elif st.session_state.stage == 2:
        stage2_comments_analysis()
    elif st.session_state.stage == 3:
        stage3_reviews_analysis()
    elif st.session_state.stage == 4:
        stage4_debate_report()


if __name__ == "__main__":
    main()
