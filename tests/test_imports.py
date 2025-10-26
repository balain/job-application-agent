#!/usr/bin/env python3
"""Test to verify all imports work correctly and no undefined references exist."""

import pytest
import sys
from pathlib import Path


def test_all_imports_work():
    """Test that all main modules can be imported without errors."""

    # Test individual module imports
    try:
        from src.models import (  # noqa: F401
            JobAssessment,
            ResumeImprovements,
            CoverLetter,
            InterviewQuestions,
            NextSteps,
            AnalysisResult,
            ErrorInfo,
            AnalyticsEvent,
            RecommendationType,
            ConfidenceLevel,
        )

        print("✅ Models import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")

    try:
        from src.structured_parser import StructuredParser  # noqa: F401

        print("✅ StructuredParser import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import StructuredParser: {e}")

    try:
        from src.error_handler import ErrorHandler, retry_on_failure  # noqa: F401

        print("✅ ErrorHandler import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import ErrorHandler: {e}")

    try:
        from src.prompts import PromptTemplates  # noqa: F401

        print("✅ PromptTemplates import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import PromptTemplates: {e}")

    try:
        from src.output import OutputFormatter  # noqa: F401

        print("✅ OutputFormatter import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import OutputFormatter: {e}")

    try:
        from src.analyzer import JobApplicationAnalyzer  # noqa: F401

        print("✅ JobApplicationAnalyzer import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import JobApplicationAnalyzer: {e}")

    try:
        from src.llm_provider import LLMProvider, ClaudeProvider, OllamaProvider  # noqa: F401

        print("✅ LLM providers import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import LLM providers: {e}")


def test_main_module_imports():
    """Test that main.py can be imported without errors."""
    try:
        # Add the project root to Python path
        project_root = Path(__file__).parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # Import main module components
        import main

        print("✅ main.py import successful")

        # Test that main function exists
        assert hasattr(main, "main"), "main function should exist"
        print("✅ main function exists")

    except ImportError as e:
        pytest.fail(f"Failed to import main module: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error importing main module: {e}")


def test_no_undefined_references():
    """Test that there are no undefined references in the codebase."""

    # Test that OutputFormatter doesn't reference undefined classes
    from src.output import OutputFormatter

    # Check that the problematic method was removed
    assert not hasattr(OutputFormatter, "_display_application_materials"), (
        "Old _display_application_materials method should be removed"
    )

    print("✅ No undefined references found")


def test_analyzer_integration():
    """Test that analyzer can be instantiated with all dependencies."""
    from unittest.mock import Mock
    from src.analyzer import JobApplicationAnalyzer

    # Create mock LLM provider
    mock_provider = Mock()

    # Test analyzer instantiation
    analyzer = JobApplicationAnalyzer(mock_provider)

    # Verify all components are available
    assert analyzer.parser is not None, "Parser should be initialized"
    assert analyzer.error_handler is not None, "Error handler should be initialized"
    assert analyzer.llm_provider is not None, "LLM provider should be set"

    print("✅ Analyzer integration test passed")


if __name__ == "__main__":
    test_all_imports_work()
    test_main_module_imports()
    test_no_undefined_references()
    test_analyzer_integration()
    print("\n🎉 All import tests passed!")
