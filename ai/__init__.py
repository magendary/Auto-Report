"""
AI Module

This module handles LLM integration, including:
- Multi-provider LLM clients (OpenAI, Gemini, DeepSeek, etc.)
- Multi-model debate orchestration
- Prompt templates for analysis
"""

from .llm_clients import (
    BaseLLMClient,
    OpenAIClient,
    GeminiClient,
    DeepSeekClient,
    get_llm_client,
)
from .debate_orchestrator import DebateOrchestrator
from .prompts import (
    ANALYST_PROMPT,
    JUDGE_PROMPT,
    get_analysis_prompt,
    get_judge_prompt,
)

__all__ = [
    'BaseLLMClient',
    'OpenAIClient',
    'GeminiClient',
    'DeepSeekClient',
    'get_llm_client',
    'DebateOrchestrator',
    'ANALYST_PROMPT',
    'JUDGE_PROMPT',
    'get_analysis_prompt',
    'get_judge_prompt',
]
