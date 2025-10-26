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
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    
    # Default LLM settings
    # DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5-20250929" # 
    DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    # DEFAULT_OLLAMA_MODEL = "llama3.1:70b"
    # DEFAULT_OLLAMA_MODEL = "llama3.3:latest"
    DEFAULT_OLLAMA_MODEL = "granite4:small-h"
    
    # Output settings
    DEFAULT_OUTPUT_FORMAT = "console"  # console, json
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
    
    # Encryption and Cache settings
    CACHE_ENCRYPTION_ENABLED = os.getenv("CACHE_ENCRYPTION_ENABLED", "true").lower() == "true"
    CACHE_AUTH_METHOD = os.getenv("CACHE_AUTH_METHOD", "password")  # password, keyfile, yubikey
    CACHE_KEYFILE_PATH = os.getenv("CACHE_KEYFILE_PATH", "")
    CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", "90"))
    CACHE_PASSWORD = os.getenv("CACHE_PASSWORD", "")
    
    # YubiKey settings (if using hardware key)
    YUBIKEY_SERIAL = os.getenv("YUBIKEY_SERIAL", "")
    YUBIKEY_SLOT = int(os.getenv("YUBIKEY_SLOT", "2"))
    YUBIKEY_PIN = os.getenv("YUBIKEY_PIN", "")
    
    # Error handling and retry settings
    MAX_LLM_RETRIES = int(os.getenv("MAX_LLM_RETRIES", "3"))
    LLM_RETRY_DELAY = float(os.getenv("LLM_RETRY_DELAY", "1.0"))
    LLM_BACKOFF_FACTOR = float(os.getenv("LLM_BACKOFF_FACTOR", "2.0"))
    LLM_MAX_DELAY = float(os.getenv("LLM_MAX_DELAY", "60.0"))
    ENABLE_RETRY_LOGIC = os.getenv("ENABLE_RETRY_LOGIC", "true").lower() == "true"
    
    # Structured parsing settings
    STRUCTURED_PARSING_ENABLED = os.getenv("STRUCTURED_PARSING_ENABLED", "true").lower() == "true"
    FALLBACK_TO_REGEX = os.getenv("FALLBACK_TO_REGEX", "true").lower() == "true"
    RESPONSE_VALIDATION_ENABLED = os.getenv("RESPONSE_VALIDATION_ENABLED", "true").lower() == "true"
    
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
