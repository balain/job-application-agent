"""
LangChain LLM wrapper for integrating with existing providers.
"""

import logging
from typing import Optional, Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import HumanMessage, SystemMessage

from .llm_provider import LLMProvider, ClaudeProvider, OllamaProvider

logger = logging.getLogger(__name__)


class LangChainLLMWrapper:
    """
    Wrapper to convert existing LLM providers to LangChain format.
    """
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.langchain_llm = self._create_langchain_llm()
    
    def _create_langchain_llm(self) -> BaseLanguageModel:
        """Create LangChain LLM from existing provider."""
        if isinstance(self.provider, ClaudeProvider):
            return ChatAnthropic(
                model=self.provider.model,
                api_key=self.provider.api_key,
                temperature=self.provider.temperature,
                max_tokens=self.provider.max_tokens,
            )
        elif isinstance(self.provider, OllamaProvider):
            return Ollama(
                model=self.provider.model,
                base_url=self.provider.base_url,
                temperature=self.provider.temperature,
            )
        else:
            raise ValueError(f"Unsupported provider type: {type(self.provider)}")
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Invoke the LangChain LLM with messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional arguments for the LLM
            
        Returns:
            Generated response text
        """
        try:
            # Convert messages to LangChain format
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            
            # Invoke the LLM
            response = self.langchain_llm.invoke(langchain_messages, **kwargs)
            
            # Extract content from response
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error invoking LangChain LLM: {e}")
            raise
    
    def stream(self, messages: List[Dict[str, str]], **kwargs):
        """
        Stream responses from the LangChain LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional arguments for the LLM
            
        Yields:
            Chunks of generated text
        """
        try:
            # Convert messages to LangChain format
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            
            # Stream the LLM
            for chunk in self.langchain_llm.stream(langchain_messages, **kwargs):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)
                    
        except Exception as e:
            logger.error(f"Error streaming from LangChain LLM: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the underlying model."""
        return {
            "provider": self.provider.__class__.__name__,
            "model": self.provider.model,
            "langchain_class": self.langchain_llm.__class__.__name__,
        }


def create_langchain_llm(provider: LLMProvider) -> LangChainLLMWrapper:
    """
    Create a LangChain LLM wrapper from an existing provider.
    
    Args:
        provider: Existing LLM provider instance
        
    Returns:
        LangChain LLM wrapper
    """
    return LangChainLLMWrapper(provider)
