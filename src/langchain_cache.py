"""
LangChain caching layer for LLM responses.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from langchain_core.language_models.base import BaseLanguageModel

from pathlib import Path
from platformdirs import user_data_dir

logger = logging.getLogger(__name__)


class LangChainCacheManager:
    """
    Manages LangChain caching for LLM responses.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(user_data_dir("job-application-agent")) / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_db_path = self.cache_dir / "langchain_cache.db"
        self._cache = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the LangChain cache."""
        if self._initialized:
            return
        
        try:
            # Create SQLite cache
            self._cache = SQLiteCache(database_path=str(self.cache_db_path))
            
            # Set as global cache
            set_llm_cache(self._cache)
            
            self._initialized = True
            logger.info(f"LangChain cache initialized at {self.cache_db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain cache: {e}")
            raise
    
    def clear_cache(self) -> None:
        """Clear the cache database."""
        try:
            if self.cache_db_path.exists():
                self.cache_db_path.unlink()
                logger.info("LangChain cache cleared")
            
            # Reinitialize cache
            self._initialized = False
            self.initialize()
            
        except Exception as e:
            logger.error(f"Failed to clear LangChain cache: {e}")
            raise
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if not self.cache_db_path.exists():
                return {
                    "cache_size": 0,
                    "cache_path": str(self.cache_db_path),
                    "initialized": self._initialized
                }
            
            # Get file size
            cache_size = self.cache_db_path.stat().st_size
            
            return {
                "cache_size": cache_size,
                "cache_size_mb": round(cache_size / (1024 * 1024), 2),
                "cache_path": str(self.cache_db_path),
                "initialized": self._initialized
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                "error": str(e),
                "initialized": self._initialized
            }
    
    def is_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._initialized and self._cache is not None
    
    def disable(self) -> None:
        """Disable caching."""
        try:
            set_llm_cache(None)
            self._initialized = False
            logger.info("LangChain cache disabled")
        except Exception as e:
            logger.error(f"Failed to disable LangChain cache: {e}")
    
    def enable(self) -> None:
        """Enable caching."""
        if not self._initialized:
            self.initialize()
        else:
            set_llm_cache(self._cache)
            logger.info("LangChain cache enabled")


# Global cache manager instance
_cache_manager: Optional[LangChainCacheManager] = None


def get_cache_manager() -> LangChainCacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = LangChainCacheManager()
    return _cache_manager


def initialize_langchain_cache() -> None:
    """Initialize the global LangChain cache."""
    cache_manager = get_cache_manager()
    cache_manager.initialize()


def clear_langchain_cache() -> None:
    """Clear the global LangChain cache."""
    cache_manager = get_cache_manager()
    cache_manager.clear_cache()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    cache_manager = get_cache_manager()
    return cache_manager.get_cache_stats()
