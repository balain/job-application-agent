"""
Error handling and retry logic for LLM interactions and parsing.

This module provides robust error handling, retry mechanisms, and response validation
for the Job Application Agent's LLM interactions.
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, Type, Union
from datetime import datetime

from .models import ErrorInfo, ConfidenceLevel


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors, retries, and response validation for LLM interactions."""
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0
    ):
        """
        Initialize ErrorHandler with retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            backoff_factor: Multiplier for exponential backoff
            max_delay: Maximum delay between retries
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        
    def retry_on_failure(
        self,
        exceptions: tuple = (Exception,),
        on_failure: Optional[Callable] = None
    ):
        """
        Decorator for retrying functions on failure.
        
        Args:
            exceptions: Tuple of exception types to retry on
            on_failure: Optional callback function to call on final failure
            
        Returns:
            Decorated function with retry logic
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(self.max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < self.max_retries:
                            delay = min(
                                self.retry_delay * (self.backoff_factor ** attempt),
                                self.max_delay
                            )
                            
                            logger.warning(
                                f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                                f"Retrying in {delay:.1f}s..."
                            )
                            
                            time.sleep(delay)
                        else:
                            logger.error(
                                f"All {self.max_retries + 1} attempts failed for {func.__name__}: {e}"
                            )
                            
                            if on_failure:
                                return on_failure(e, *args, **kwargs)
                            else:
                                raise e
                
                # This should never be reached, but just in case
                raise last_exception
                
            return wrapper
        return decorator
    
    def retry_on_failure_async(
        self,
        exceptions: tuple = (Exception,),
        on_failure: Optional[Callable] = None
    ):
        """
        Async decorator for retrying async functions on failure.
        
        Args:
            exceptions: Tuple of exception types to retry on
            on_failure: Optional callback function to call on final failure
            
        Returns:
            Decorated async function with retry logic
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(self.max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < self.max_retries:
                            delay = min(
                                self.retry_delay * (self.backoff_factor ** attempt),
                                self.max_delay
                            )
                            
                            logger.warning(
                                f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                                f"Retrying in {delay:.1f}s..."
                            )
                            
                            await asyncio.sleep(delay)
                        else:
                            logger.error(
                                f"All {self.max_retries + 1} attempts failed for {func.__name__}: {e}"
                            )
                            
                            if on_failure:
                                return on_failure(e, *args, **kwargs)
                            else:
                                raise e
                
                # This should never be reached, but just in case
                raise last_exception
                
            return wrapper
        return decorator
    
    def handle_llm_error(self, error: Exception, context: str = "") -> ErrorInfo:
        """
        Handle LLM-specific errors and return structured error information.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            ErrorInfo object with structured error details
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Categorize common LLM errors
        if "rate limit" in error_message.lower():
            category = "rate_limit"
            user_message = "API rate limit exceeded. Please try again later."
            confidence = ConfidenceLevel.LOW
        elif "timeout" in error_message.lower():
            category = "timeout"
            user_message = "Request timed out. Please check your connection and try again."
            confidence = ConfidenceLevel.MEDIUM
        elif "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
            category = "authentication"
            user_message = "Authentication failed. Please check your API key."
            confidence = ConfidenceLevel.HIGH
        elif "quota" in error_message.lower() or "billing" in error_message.lower():
            category = "quota"
            user_message = "API quota exceeded. Please check your billing status."
            confidence = ConfidenceLevel.HIGH
        elif "network" in error_message.lower() or "connection" in error_message.lower():
            category = "network"
            user_message = "Network error occurred. Please check your internet connection."
            confidence = ConfidenceLevel.MEDIUM
        else:
            category = "unknown"
            user_message = f"An unexpected error occurred: {error_message}"
            confidence = ConfidenceLevel.LOW
        
        return ErrorInfo(
            error_type=error_type,
            error_message=error_message,
            user_message=user_message,
            category=category,
            confidence=confidence,
            context=context,
            timestamp=datetime.now()
        )
    
    def validate_response(self, response: str, expected_structure: str = "json") -> bool:
        """
        Validate LLM response structure before parsing.
        
        Args:
            response: The LLM response to validate
            expected_structure: Expected structure type ("json", "text", "any")
            
        Returns:
            True if response appears valid, False otherwise
        """
        if not response or not response.strip():
            logger.warning("Empty response received from LLM")
            return False
        
        if expected_structure == "json":
            # Check for JSON-like structure
            response_lower = response.lower()
            if ("{" in response and "}" in response) or ("```json" in response_lower):
                return True
            else:
                logger.warning("Expected JSON response but found text format")
                return False
        
        elif expected_structure == "text":
            # Basic text validation
            if len(response.strip()) < 5:
                logger.warning("Response too short to be meaningful")
                return False
            return True
        
        elif expected_structure == "any":
            # Minimal validation
            return len(response.strip()) > 0
        
        return True
    
    def create_fallback_response(self, error: Exception, operation: str) -> Dict[str, Any]:
        """
        Create a fallback response when all retries fail.
        
        Args:
            error: The final error that occurred
            operation: Description of the operation that failed
            
        Returns:
            Dictionary with fallback data
        """
        logger.error(f"Creating fallback response for failed {operation}: {error}")
        
        return {
            "rating": 5,  # Neutral rating
            "strengths": "Unable to analyze due to technical issues",
            "gaps": "Analysis unavailable - please try again",
            "missing_requirements": "Unable to determine",
            "recommendation": "Unknown",
            "confidence": "Low",
            "error": True,
            "fallback_reason": str(error)
        }


# Global error handler instance
default_error_handler = ErrorHandler()


def retry_on_failure(
    exceptions: tuple = (Exception,),
    max_retries: int = 3,
    retry_delay: float = 1.0,
    on_failure: Optional[Callable] = None
):
    """
    Convenience decorator for retrying functions on failure.
    
    Args:
        exceptions: Tuple of exception types to retry on
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries
        on_failure: Optional callback function to call on final failure
        
    Returns:
        Decorated function with retry logic
    """
    handler = ErrorHandler(max_retries=max_retries, retry_delay=retry_delay)
    return handler.retry_on_failure(exceptions=exceptions, on_failure=on_failure)


def retry_on_failure_async(
    exceptions: tuple = (Exception,),
    max_retries: int = 3,
    retry_delay: float = 1.0,
    on_failure: Optional[Callable] = None
):
    """
    Convenience decorator for retrying async functions on failure.
    
    Args:
        exceptions: Tuple of exception types to retry on
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries
        on_failure: Optional callback function to call on final failure
        
    Returns:
        Decorated async function with retry logic
    """
    handler = ErrorHandler(max_retries=max_retries, retry_delay=retry_delay)
    return handler.retry_on_failure_async(exceptions=exceptions, on_failure=on_failure)
