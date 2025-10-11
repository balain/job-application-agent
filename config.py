"""Configuration management for the job application agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the job application agent."""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Default LLM settings
    DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5-20250929" # "claude-3-5-sonnet-20241022"
    DEFAULT_OLLAMA_MODEL = "llama3.1:8b"
    
    # Output settings
    DEFAULT_OUTPUT_FORMAT = "console"  # console, json
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.ANTHROPIC_API_KEY and not cls.OLLAMA_BASE_URL:
            return False
        return True
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available LLM providers based on configuration."""
        providers = []
        if cls.ANTHROPIC_API_KEY:
            providers.append("claude")
        if cls.OLLAMA_BASE_URL:
            providers.append("ollama")
        return providers
