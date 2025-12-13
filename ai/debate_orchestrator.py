"""
Multi-Model Debate Orchestrator

This module orchestrates the debate between multiple LLM models
to generate a comprehensive market analysis report.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
from .llm_clients import BaseLLMClient, get_llm_client
from .prompts import ANALYST_PROMPT, JUDGE_PROMPT, get_analysis_prompt, get_judge_prompt


class DebateOrchestrator:
    """
    Orchestrates multi-model debate for market analysis.
    
    The debate process:
    1. Two different models independently analyze the data
    2. A judge model (can be one of the two or a third) synthesizes the results
    """
    
    def __init__(
        self,
        analyst1_provider: str,
        analyst2_provider: str,
        judge_provider: Optional[str] = None,
        analyst1_api_key: Optional[str] = None,
        analyst2_api_key: Optional[str] = None,
        judge_api_key: Optional[str] = None,
    ):
        """
        Initialize debate orchestrator.
        
        Args:
            analyst1_provider: First analyst provider name
            analyst2_provider: Second analyst provider name
            judge_provider: Judge provider name (defaults to analyst1_provider)
            analyst1_api_key: API key for first analyst (optional)
            analyst2_api_key: API key for second analyst (optional)
            judge_api_key: API key for judge (optional)
        """
        self.analyst1 = get_llm_client(analyst1_provider, api_key=analyst1_api_key)
        self.analyst2 = get_llm_client(analyst2_provider, api_key=analyst2_api_key)
        
        # Judge can be one of the analysts or a third model
        if judge_provider is None:
            judge_provider = analyst1_provider
            judge_api_key = analyst1_api_key
        
        self.judge = get_llm_client(judge_provider, api_key=judge_api_key)
        
        self.analyst1_name = self.analyst1.get_provider_name()
        self.analyst2_name = self.analyst2.get_provider_name()
        self.judge_name = self.judge.get_provider_name()
    
    def run_debate(
        self,
        data_summary: Dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        """
        Run the complete debate process.
        
        Args:
            data_summary: Structured JSON data from all pipeline stages
            temperature: Sampling temperature for generation
            max_tokens: Maximum tokens per response
            
        Returns:
            Dictionary containing all reports and metadata
        """
        print("🤖 Starting multi-model debate...")
        
        # Step 1: Generate analysis prompt
        analysis_prompt = get_analysis_prompt(data_summary)
        
        # Step 2: Get independent analyses from two models
        print(f"📊 Analyst 1 ({self.analyst1_name}) is analyzing...")
        report1 = self.analyst1.generate(
            prompt=analysis_prompt,
            system_prompt=ANALYST_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        print(f"📊 Analyst 2 ({self.analyst2_name}) is analyzing...")
        report2 = self.analyst2.generate(
            prompt=analysis_prompt,
            system_prompt=ANALYST_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Step 3: Judge synthesizes the reports
        print(f"⚖️  Judge ({self.judge_name}) is synthesizing...")
        judge_prompt = get_judge_prompt(
            report1, self.analyst1_name,
            report2, self.analyst2_name
        )
        
        final_report = self.judge.generate(
            prompt=judge_prompt,
            system_prompt=JUDGE_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        print("✅ Debate completed!")
        
        # Return all results
        return {
            'metadata': {
                'analyst1': self.analyst1_name,
                'analyst2': self.analyst2_name,
                'judge': self.judge_name,
                'temperature': temperature,
                'max_tokens': max_tokens,
            },
            'reports': {
                'analyst1': report1,
                'analyst2': report2,
                'final': final_report,
            },
            'data_summary': data_summary,
        }
    
    def get_summary_statistics(self, data_summary: Dict[str, Any]) -> str:
        """
        Generate a text summary of key statistics for display.
        
        Args:
            data_summary: Structured JSON data
            
        Returns:
            Formatted text summary
        """
        summary = []
        
        # Stage 1: Market statistics
        if 'stage1_market' in data_summary:
            market = data_summary['stage1_market']
            
            if 'platforms' in market:
                for platform, data in market['platforms'].items():
                    if 'market_overview' in data:
                        overview = data['market_overview']
                        summary.append(f"**{platform.upper()}平台：**")
                        summary.append(f"- 产品数量：{overview.get('total_products', 0)}")
                        summary.append(f"- 总销量：{overview.get('total_sales', 0):,}")
                        summary.append(f"- 平均价格：${overview.get('avg_price', 0):.2f}")
                        summary.append(f"- 平均评分：{overview.get('avg_rating', 0):.2f}")
                        summary.append("")
        
        # Stage 2: Comments
        if 'stage2_comments' in data_summary:
            comments = data_summary['stage2_comments']
            summary.append(f"**用户评论分析：**")
            summary.append(f"- 总评论数：{comments.get('total_comments', 0)}")
            summary.append(f"- TikTok评论：{comments.get('tiktok_comments', 0)}")
            summary.append(f"- Reddit评论：{comments.get('reddit_comments', 0)}")
            summary.append("")
        
        # Stage 3: Reviews
        if 'stage3_reviews' in data_summary:
            reviews = data_summary['stage3_reviews']
            summary.append(f"**产品评价分析：**")
            summary.append(f"- 总评价数：{reviews.get('total_reviews', 0)}")
            summary.append(f"- 平均评分：{reviews.get('avg_rating', 0):.2f}")
            summary.append("")
        
        return "\n".join(summary)


def create_master_summary(
    market_stats: Optional[Dict[str, Any]] = None,
    voc_stats: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create master summary JSON from all stages.
    
    Args:
        market_stats: Stage 1 market statistics
        voc_stats: Stages 2&3 VOC statistics
        
    Returns:
        Master summary dictionary
    """
    summary = {}
    
    if market_stats:
        summary['stage1_market'] = market_stats
    
    if voc_stats:
        if 'stage2_comments' in voc_stats:
            summary['stage2_comments'] = voc_stats['stage2_comments']
        if 'stage3_reviews' in voc_stats:
            summary['stage3_reviews'] = voc_stats['stage3_reviews']
    
    return summary
