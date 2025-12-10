"""
LLM Client Wrappers

This module provides unified interfaces for different LLM providers.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json


class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            api_key: API key for the provider (optional, can use env var)
            model: Model name to use (optional, uses default if not provided)
        """
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """
        Generate response from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API client wrapper."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (defaults to gpt-4o-mini)
        """
        super().__init__(api_key, model)
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Generate response using OpenAI API."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return response.choices[0].message.content
        
        except ImportError:
            return "Error: openai library not installed. Run: pip install openai"
        except Exception as e:
            return f"Error generating response from OpenAI: {str(e)}"
    
    def get_provider_name(self) -> str:
        return f"OpenAI ({self.model})"


class GeminiClient(BaseLLMClient):
    """Google Gemini API client wrapper."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Model name (defaults to gemini-pro)
        """
        super().__init__(api_key, model)
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY', '')
        
        if not self.api_key:
            raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable.")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Generate response using Gemini API."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            # Combine system prompt with user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            return response.text
        
        except ImportError:
            return "Error: google-generativeai library not installed. Run: pip install google-generativeai"
        except Exception as e:
            return f"Error generating response from Gemini: {str(e)}"
    
    def get_provider_name(self) -> str:
        return f"Google Gemini ({self.model})"


class DeepSeekClient(BaseLLMClient):
    """DeepSeek API client wrapper (OpenAI-compatible)."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        """
        Initialize DeepSeek client.
        
        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
            model: Model name (defaults to deepseek-chat)
        """
        super().__init__(api_key, model)
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY', '')
        
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided. Set DEEPSEEK_API_KEY environment variable.")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Generate response using DeepSeek API."""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return response.choices[0].message.content
        
        except ImportError:
            return "Error: openai library not installed. Run: pip install openai"
        except Exception as e:
            return f"Error generating response from DeepSeek: {str(e)}"
    
    def get_provider_name(self) -> str:
        return f"DeepSeek ({self.model})"


def get_llm_client(provider: str, api_key: Optional[str] = None, model: Optional[str] = None) -> BaseLLMClient:
    """
    Factory function to get LLM client by provider name.
    
    Args:
        provider: Provider name ('openai', 'gemini', 'deepseek')
        api_key: API key (optional)
        model: Model name (optional)
        
    Returns:
        Initialized LLM client
    """
    provider_lower = provider.lower()
    
    if provider_lower == 'openai':
        return OpenAIClient(api_key=api_key, model=model or "gpt-4o-mini")
    elif provider_lower == 'gemini':
        return GeminiClient(api_key=api_key, model=model or "gemini-pro")
    elif provider_lower == 'deepseek':
        return DeepSeekClient(api_key=api_key, model=model or "deepseek-chat")
    else:
        raise ValueError(f"Unknown provider: {provider}. Supported: openai, gemini, deepseek")
