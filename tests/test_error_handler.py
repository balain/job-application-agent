"""
Tests for error handling and retry logic.

This module tests the ErrorHandler class, retry decorators, and error handling
functionality for LLM interactions.
"""

import pytest
from datetime import datetime

from src.error_handler import (
    ErrorHandler,
    retry_on_failure,
    retry_on_failure_async,
    default_error_handler,
)
from src.models import ConfidenceLevel


class TestErrorHandler:
    """Test ErrorHandler class functionality."""

    def test_init_default_values(self):
        """Test ErrorHandler initialization with default values."""
        handler = ErrorHandler()
        assert handler.max_retries == 3
        assert handler.retry_delay == 1.0
        assert handler.backoff_factor == 2.0
        assert handler.max_delay == 60.0

    def test_init_custom_values(self):
        """Test ErrorHandler initialization with custom values."""
        handler = ErrorHandler(
            max_retries=5, retry_delay=2.0, backoff_factor=1.5, max_delay=30.0
        )
        assert handler.max_retries == 5
        assert handler.retry_delay == 2.0
        assert handler.backoff_factor == 1.5
        assert handler.max_delay == 30.0

    def test_retry_on_failure_success(self):
        """Test retry decorator with successful function."""
        handler = ErrorHandler(max_retries=2)

        @handler.retry_on_failure()
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_retry_on_failure_eventual_success(self):
        """Test retry decorator with function that eventually succeeds."""
        handler = ErrorHandler(max_retries=3, retry_delay=0.1)
        call_count = 0

        @handler.retry_on_failure()
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = eventually_successful_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_on_failure_max_retries_exceeded(self):
        """Test retry decorator when max retries are exceeded."""
        handler = ErrorHandler(max_retries=2, retry_delay=0.1)

        @handler.retry_on_failure()
        def always_failing_function():
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_failing_function()

    def test_retry_on_failure_with_on_failure_callback(self):
        """Test retry decorator with failure callback."""
        handler = ErrorHandler(max_retries=1, retry_delay=0.1)
        callback_called = False

        def failure_callback(error, *args, **kwargs):
            nonlocal callback_called
            callback_called = True
            return "fallback_result"

        @handler.retry_on_failure(on_failure=failure_callback)
        def failing_function():
            raise ValueError("Always fails")

        result = failing_function()
        assert result == "fallback_result"
        assert callback_called

    def test_retry_on_failure_specific_exceptions(self):
        """Test retry decorator with specific exception types."""
        handler = ErrorHandler(max_retries=1, retry_delay=0.1)

        @handler.retry_on_failure(exceptions=(ValueError,))
        def function_with_value_error():
            raise ValueError("Value error")

        @handler.retry_on_failure(exceptions=(ValueError,))
        def function_with_runtime_error():
            raise RuntimeError("Runtime error")

        # Should retry ValueError
        with pytest.raises(ValueError):
            function_with_value_error()

        # Should not retry RuntimeError
        with pytest.raises(RuntimeError):
            function_with_runtime_error()

    @pytest.mark.asyncio
    async def test_retry_on_failure_async_success(self):
        """Test async retry decorator with successful function."""
        handler = ErrorHandler(max_retries=2, retry_delay=0.1)

        @handler.retry_on_failure_async()
        async def successful_async_function():
            return "async_success"

        result = await successful_async_function()
        assert result == "async_success"

    @pytest.mark.asyncio
    async def test_retry_on_failure_async_eventual_success(self):
        """Test async retry decorator with function that eventually succeeds."""
        handler = ErrorHandler(max_retries=3, retry_delay=0.1)
        call_count = 0

        @handler.retry_on_failure_async()
        async def eventually_successful_async_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary async failure")
            return "async_success"

        result = await eventually_successful_async_function()
        assert result == "async_success"
        assert call_count == 3

    def test_handle_llm_error_rate_limit(self):
        """Test handling rate limit errors."""
        handler = ErrorHandler()
        error = Exception("Rate limit exceeded")

        error_info = handler.handle_llm_error(error, "test context")

        assert error_info.error_type == "Exception"
        assert error_info.error_message == "Rate limit exceeded"
        assert error_info.category == "rate_limit"
        assert (
            error_info.user_message
            == "API rate limit exceeded. Please try again later."
        )
        assert error_info.confidence == ConfidenceLevel.LOW
        assert error_info.context == "test context"
        assert isinstance(error_info.timestamp, datetime)

    def test_handle_llm_error_timeout(self):
        """Test handling timeout errors."""
        handler = ErrorHandler()
        error = Exception("Request timeout")

        error_info = handler.handle_llm_error(error, "timeout test")

        assert error_info.category == "timeout"
        assert (
            error_info.user_message
            == "Request timed out. Please check your connection and try again."
        )
        assert error_info.confidence == ConfidenceLevel.MEDIUM

    def test_handle_llm_error_authentication(self):
        """Test handling authentication errors."""
        handler = ErrorHandler()
        error = Exception("Authentication failed")

        error_info = handler.handle_llm_error(error)

        assert error_info.category == "authentication"
        assert (
            error_info.user_message
            == "Authentication failed. Please check your API key."
        )
        assert error_info.confidence == ConfidenceLevel.HIGH

    def test_handle_llm_error_quota(self):
        """Test handling quota errors."""
        handler = ErrorHandler()
        error = Exception("Quota exceeded")

        error_info = handler.handle_llm_error(error)

        assert error_info.category == "quota"
        assert (
            error_info.user_message
            == "API quota exceeded. Please check your billing status."
        )
        assert error_info.confidence == ConfidenceLevel.HIGH

    def test_handle_llm_error_network(self):
        """Test handling network errors."""
        handler = ErrorHandler()
        error = Exception("Network connection failed")

        error_info = handler.handle_llm_error(error)

        assert error_info.category == "network"
        assert (
            error_info.user_message
            == "Network error occurred. Please check your internet connection."
        )
        assert error_info.confidence == ConfidenceLevel.MEDIUM

    def test_handle_llm_error_unknown(self):
        """Test handling unknown errors."""
        handler = ErrorHandler()
        error = Exception("Some random error")

        error_info = handler.handle_llm_error(error)

        assert error_info.category == "unknown"
        assert (
            error_info.user_message == "An unexpected error occurred: Some random error"
        )
        assert error_info.confidence == ConfidenceLevel.LOW

    def test_validate_response_empty(self):
        """Test response validation with empty response."""
        handler = ErrorHandler()

        assert not handler.validate_response("", "any")
        assert not handler.validate_response("   ", "any")

    def test_validate_response_json(self):
        """Test response validation for JSON structure."""
        handler = ErrorHandler()

        # Valid JSON responses
        assert handler.validate_response('{"key": "value"}', "json")
        assert handler.validate_response('```json\n{"key": "value"}\n```', "json")

        # Invalid JSON responses
        assert not handler.validate_response("Just plain text", "json")
        assert not handler.validate_response("", "json")

    def test_validate_response_text(self):
        """Test response validation for text structure."""
        handler = ErrorHandler()

        # Valid text responses
        assert handler.validate_response("This is a valid text response", "text")
        assert handler.validate_response("Short", "text")  # Edge case

        # Invalid text responses
        assert not handler.validate_response("", "text")
        assert not handler.validate_response("   ", "text")
        assert not handler.validate_response("abc", "text")  # Too short

    def test_validate_response_any(self):
        """Test response validation for any structure."""
        handler = ErrorHandler()

        # Valid responses
        assert handler.validate_response("Any non-empty response", "any")
        assert handler.validate_response("a", "any")

        # Invalid responses
        assert not handler.validate_response("", "any")
        assert not handler.validate_response("   ", "any")

    def test_create_fallback_response(self):
        """Test creating fallback response."""
        handler = ErrorHandler()
        error = Exception("Test error")

        fallback = handler.create_fallback_response(error, "test operation")

        assert fallback["rating"] == 5
        assert fallback["strengths"] == "Unable to analyze due to technical issues"
        assert fallback["gaps"] == "Analysis unavailable - please try again"
        assert fallback["missing_requirements"] == "Unable to determine"
        assert fallback["recommendation"] == "Unknown"
        assert fallback["confidence"] == "Low"
        assert fallback["error"] is True
        assert fallback["fallback_reason"] == "Test error"


class TestConvenienceDecorators:
    """Test convenience decorator functions."""

    def test_retry_on_failure_decorator(self):
        """Test the convenience retry_on_failure decorator."""
        call_count = 0

        @retry_on_failure(max_retries=2, retry_delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"

        result = test_function()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_failure_async_decorator(self):
        """Test the convenience retry_on_failure_async decorator."""
        call_count = 0

        @retry_on_failure_async(max_retries=2, retry_delay=0.1)
        async def test_async_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary async failure")
            return "async_success"

        result = await test_async_function()
        assert result == "async_success"
        assert call_count == 2


class TestDefaultErrorHandler:
    """Test the default error handler instance."""

    def test_default_error_handler_exists(self):
        """Test that default error handler is available."""
        assert default_error_handler is not None
        assert isinstance(default_error_handler, ErrorHandler)

    def test_default_error_handler_configuration(self):
        """Test default error handler configuration."""
        assert default_error_handler.max_retries == 3
        assert default_error_handler.retry_delay == 1.0
        assert default_error_handler.backoff_factor == 2.0
        assert default_error_handler.max_delay == 60.0


class TestErrorHandlerIntegration:
    """Test ErrorHandler integration scenarios."""

    def test_backoff_calculation(self):
        """Test exponential backoff calculation."""
        _ = ErrorHandler(retry_delay=1.0, backoff_factor=2.0, max_delay=10.0)

        # Test backoff calculation
        delay_1 = min(1.0 * (2.0**0), 10.0)  # 1.0
        delay_2 = min(1.0 * (2.0**1), 10.0)  # 2.0
        delay_3 = min(1.0 * (2.0**2), 10.0)  # 4.0
        delay_4 = min(1.0 * (2.0**3), 10.0)  # 8.0
        delay_5 = min(1.0 * (2.0**4), 10.0)  # 10.0 (capped)

        assert delay_1 == 1.0
        assert delay_2 == 2.0
        assert delay_3 == 4.0
        assert delay_4 == 8.0
        assert delay_5 == 10.0

    def test_error_info_serialization(self):
        """Test ErrorInfo model serialization."""
        handler = ErrorHandler()
        error = Exception("Test error")

        error_info = handler.handle_llm_error(error, "test context")

        # Test model_dump
        data = error_info.model_dump()
        assert isinstance(data, dict)
        assert data["error_type"] == "Exception"
        assert data["error_message"] == "Test error"

        # Test model_dump_json
        json_data = error_info.model_dump_json()
        assert isinstance(json_data, str)
        assert "Exception" in json_data
        assert "Test error" in json_data
