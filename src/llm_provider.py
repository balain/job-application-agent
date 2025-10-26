"""LLM provider abstraction and implementations."""

import sys
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

import requests
from anthropic import Anthropic
from rich.console import Console

from config import Config
from .error_handler import ErrorHandler, retry_on_failure

console = Console(file=sys.stderr)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class ClaudeProvider(LLMProvider):
    """Claude API provider using Anthropic."""
    
    def __init__(self, model: str = None):
        self.model = model or Config.DEFAULT_CLAUDE_MODEL
        self.client = None
        self.error_handler = ErrorHandler(
            max_retries=Config.MAX_LLM_RETRIES,
            retry_delay=Config.LLM_RETRY_DELAY,
            backoff_factor=Config.LLM_BACKOFF_FACTOR,
            max_delay=Config.LLM_MAX_DELAY
        )
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Claude client."""
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        try:
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        except Exception as e:
            raise ValueError(f"Failed to initialize Claude client: {e}")
    
    @retry_on_failure(
        exceptions=(requests.exceptions.RequestException, Exception),
        max_retries=Config.MAX_LLM_RETRIES,
        retry_delay=Config.LLM_RETRY_DELAY
    )
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Claude API with retry logic."""
        if not self.client:
            raise ValueError("Claude client not initialized")
        
        # Validate response structure if enabled
        if Config.RESPONSE_VALIDATION_ENABLED:
            if not self.error_handler.validate_response(prompt, "text"):
                raise ValueError("Invalid prompt structure")
        
        try:
            console.print("[blue]Generating response with Claude...[/blue]")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Validate response if enabled
            if Config.RESPONSE_VALIDATION_ENABLED:
                if not self.error_handler.validate_response(response_text, "any"):
                    raise ValueError("Invalid response structure from Claude")
            
            return response_text
            
        except Exception as e:
            error_info = self.error_handler.handle_llm_error(e, "Claude API call")
            console.print(f"[red]Claude API error: {error_info.user_message}[/red]")
            raise ValueError(f"Claude API error: {e}")
    
    def is_available(self) -> bool:
        """Check if Claude is available."""
        return self.client is not None and Config.ANTHROPIC_API_KEY is not None


class OllamaProvider(LLMProvider):
    """Ollama local model provider."""
    
    def __init__(self, model: str = None, base_url: str = None):
        self.model = model or Config.DEFAULT_OLLAMA_MODEL
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.error_handler = ErrorHandler(
            max_retries=Config.MAX_LLM_RETRIES,
            retry_delay=Config.LLM_RETRY_DELAY,
            backoff_factor=Config.LLM_BACKOFF_FACTOR,
            max_delay=Config.LLM_MAX_DELAY
        )
        self._check_availability()
    
    def _check_availability(self):
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ValueError("Ollama server not responding")
        except Exception as e:
            raise ValueError(f"Ollama not available: {e}")
    
    @retry_on_failure(
        exceptions=(requests.exceptions.RequestException, Exception),
        max_retries=Config.MAX_LLM_RETRIES,
        retry_delay=Config.LLM_RETRY_DELAY
    )
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama API with retry logic."""
        # Validate response structure if enabled
        if Config.RESPONSE_VALIDATION_ENABLED:
            if not self.error_handler.validate_response(prompt, "text"):
                raise ValueError("Invalid prompt structure")
        
        try:
            console.print(f"[blue]Generating response with Ollama ({self.model})...[/blue]")
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "num_predict": kwargs.get('max_tokens', 4000)
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', '')
            
            # Validate response if enabled
            if Config.RESPONSE_VALIDATION_ENABLED:
                if not self.error_handler.validate_response(response_text, "any"):
                    raise ValueError("Invalid response structure from Ollama")
            
            return response_text
            
        except Exception as e:
            error_info = self.error_handler.handle_llm_error(e, "Ollama API call")
            console.print(f"[red]Ollama API error: {error_info.user_message}[/red]")
            raise ValueError(f"Ollama API error: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def create_provider(provider_name: str, **kwargs) -> LLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Name of the provider ('claude' or 'ollama')
            **kwargs: Additional arguments for the provider
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider is not supported or not available
        """
        provider_name = provider_name.lower()
        
        if provider_name == 'claude':
            return ClaudeProvider(**kwargs)
        elif provider_name == 'ollama':
            return OllamaProvider(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of available providers."""
        available = []
        
        # Check Claude
        try:
            ClaudeProvider()
            available.append('claude')
        except ValueError:
            pass
        
        # Check Ollama
        try:
            OllamaProvider()
            available.append('ollama')
        except ValueError:
            pass
        
        return available
    
    @staticmethod
    def auto_select_provider() -> str:
        """Automatically select the best available provider."""
        available = LLMProviderFactory.get_available_providers()
        
        if not available:
            raise ValueError("No LLM providers are available. Please check your configuration.")
        
        # Prefer Claude if available, otherwise use Ollama
        if 'claude' in available:
            return 'claude'
        else:
            return available[0]


def create_llm_provider(provider: str = None, **kwargs) -> LLMProvider:
    """
    Create an LLM provider with automatic fallback.
    
    Args:
        provider: Provider name ('claude', 'ollama', or None for auto-select)
        **kwargs: Additional arguments for the provider
        
    Returns:
        LLMProvider instance
    """
    if provider is None:
        provider = LLMProviderFactory.auto_select_provider()
    
    return LLMProviderFactory.create_provider(provider, **kwargs)
