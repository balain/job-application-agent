"""
Tests for Pydantic models.

This module tests all the data models to ensure they work correctly
and handle edge cases properly.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from src.models import (
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


class TestJobAssessment:
    """Test JobAssessment model."""

    def test_valid_assessment(self):
        """Test creating a valid assessment."""
        assessment = JobAssessment(
            rating=8,
            strengths="Strong technical background in Python and JavaScript",
            gaps="Limited experience with cloud platforms",
            missing_requirements="None",
            recommendation=RecommendationType.YES,
            confidence=ConfidenceLevel.HIGH,
        )

        assert assessment.rating == 8
        assert (
            assessment.strengths
            == "Strong technical background in Python and JavaScript"
        )
        assert assessment.gaps == "Limited experience with cloud platforms"
        assert assessment.missing_requirements == "None"
        assert assessment.recommendation == RecommendationType.YES
        assert assessment.confidence == ConfidenceLevel.HIGH

    def test_invalid_rating_too_high(self):
        """Test that rating > 10 raises validation error."""
        with pytest.raises(ValidationError):
            JobAssessment(
                rating=15,
                strengths="Test",
                gaps="Test",
                missing_requirements="Test",
                recommendation=RecommendationType.YES,
                confidence=ConfidenceLevel.HIGH,
            )

    def test_invalid_rating_too_low(self):
        """Test that rating < 1 raises validation error."""
        with pytest.raises(ValidationError):
            JobAssessment(
                rating=0,
                strengths="Test",
                gaps="Test",
                missing_requirements="Test",
                recommendation=RecommendationType.YES,
                confidence=ConfidenceLevel.HIGH,
            )

    def test_invalid_rating_type(self):
        """Test that non-integer rating raises validation error."""
        with pytest.raises(ValidationError):
            JobAssessment(
                rating="eight",
                strengths="Test",
                gaps="Test",
                missing_requirements="Test",
                recommendation=RecommendationType.YES,
                confidence=ConfidenceLevel.HIGH,
            )

    def test_enum_values(self):
        """Test that enum values are properly handled."""
        assessment = JobAssessment(
            rating=5,
            strengths="Test",
            gaps="Test",
            missing_requirements="Test",
            recommendation="No",  # String value
            confidence="Medium",  # String value
        )

        assert assessment.recommendation == RecommendationType.NO
        assert assessment.confidence == ConfidenceLevel.MEDIUM


class TestResumeImprovements:
    """Test ResumeImprovements model."""

    def test_empty_improvements(self):
        """Test creating empty improvements."""
        improvements = ResumeImprovements()

        assert improvements.keyword_suggestions == []
        assert improvements.section_improvements == {}
        assert improvements.formatting_fixes == []
        assert improvements.content_enhancements == []
        assert improvements.priority_changes == []
        assert improvements.quick_wins == []

    def test_populated_improvements(self):
        """Test creating populated improvements."""
        improvements = ResumeImprovements(
            keyword_suggestions=["Python", "JavaScript", "React"],
            section_improvements={"experience": "Add more quantifiable achievements"},
            formatting_fixes=["Fix inconsistent bullet points"],
            content_enhancements=["Add more technical details"],
            priority_changes=["Update skills section", "Add project examples"],
            quick_wins=["Fix typos", "Update contact info"],
        )

        assert len(improvements.keyword_suggestions) == 3
        assert "Python" in improvements.keyword_suggestions
        assert (
            improvements.section_improvements["experience"]
            == "Add more quantifiable achievements"
        )
        assert len(improvements.priority_changes) == 2


class TestCoverLetter:
    """Test CoverLetter model."""

    def test_valid_cover_letter(self):
        """Test creating a valid cover letter."""
        cover_letter = CoverLetter(
            opening="Dear Hiring Manager,",
            body="I am writing to express my interest in the Software Engineer position...",
            closing="Thank you for your consideration.",
            full_letter="Dear Hiring Manager,\n\nI am writing to express my interest...",
        )

        assert cover_letter.opening == "Dear Hiring Manager,"
        assert "Software Engineer" in cover_letter.body
        assert cover_letter.closing == "Thank you for your consideration."


class TestInterviewQuestions:
    """Test InterviewQuestions model."""

    def test_empty_questions(self):
        """Test creating empty questions."""
        questions = InterviewQuestions()

        assert questions.questions_for_employer == []
        assert questions.anticipated_questions == []
        assert questions.suggested_answers == []

    def test_populated_questions(self):
        """Test creating populated questions."""
        questions = InterviewQuestions(
            questions_for_employer=[
                "What is the team structure?",
                "What technologies do you use?",
            ],
            anticipated_questions=[
                "Tell me about yourself",
                "Why do you want this job?",
            ],
            suggested_answers=[
                "I am a software engineer with 5 years experience...",
                "I am excited about this opportunity because...",
            ],
        )

        assert len(questions.questions_for_employer) == 2
        assert len(questions.anticipated_questions) == 2
        assert len(questions.suggested_answers) == 2


class TestNextSteps:
    """Test NextSteps model."""

    def test_empty_next_steps(self):
        """Test creating empty next steps."""
        steps = NextSteps()

        assert steps.immediate_actions == []
        assert steps.short_term_preparation == []
        assert steps.long_term_development == []
        assert steps.application_strategy == []
        assert steps.risk_mitigation == []

    def test_populated_next_steps(self):
        """Test creating populated next steps."""
        steps = NextSteps(
            immediate_actions=["Update resume", "Prepare cover letter"],
            short_term_preparation=["Research company", "Practice interview questions"],
            long_term_development=[
                "Learn new technologies",
                "Build portfolio projects",
            ],
            application_strategy=[
                "Apply to similar positions",
                "Network with industry professionals",
            ],
            risk_mitigation=["Have backup options", "Prepare for rejection"],
        )

        assert len(steps.immediate_actions) == 2
        assert "Update resume" in steps.immediate_actions
        assert len(steps.risk_mitigation) == 2


class TestAnalysisResult:
    """Test AnalysisResult model."""

    def test_minimal_analysis_result(self):
        """Test creating minimal analysis result."""
        assessment = JobAssessment(
            rating=7,
            strengths="Test",
            gaps="Test",
            missing_requirements="Test",
            recommendation=RecommendationType.YES,
            confidence=ConfidenceLevel.MEDIUM,
        )

        result = AnalysisResult(assessment=assessment)

        assert result.assessment == assessment
        assert result.resume_improvements is None
        assert result.cover_letter is None
        assert result.interview_questions is None
        assert result.next_steps is None
        assert isinstance(result.analysis_timestamp, datetime)

    def test_complete_analysis_result(self):
        """Test creating complete analysis result."""
        assessment = JobAssessment(
            rating=8,
            strengths="Strong technical background",
            gaps="Limited management experience",
            missing_requirements="None",
            recommendation=RecommendationType.YES,
            confidence=ConfidenceLevel.HIGH,
        )

        improvements = ResumeImprovements(keyword_suggestions=["Python", "JavaScript"])

        cover_letter = CoverLetter(
            opening="Dear Hiring Manager,",
            body="I am excited about this opportunity...",
            closing="Thank you for your consideration.",
            full_letter="Complete letter...",
        )

        questions = InterviewQuestions(
            questions_for_employer=["What is the team structure?"]
        )

        steps = NextSteps(immediate_actions=["Update resume"])

        result = AnalysisResult(
            assessment=assessment,
            resume_improvements=improvements,
            cover_letter=cover_letter,
            interview_questions=questions,
            next_steps=steps,
            raw_response="Raw LLM response...",
        )

        assert result.assessment == assessment
        assert result.resume_improvements == improvements
        assert result.cover_letter == cover_letter
        assert result.interview_questions == questions
        assert result.next_steps == steps
        assert result.raw_response == "Raw LLM response..."


class TestErrorInfo:
    """Test ErrorInfo model."""

    def test_valid_error_info(self):
        """Test creating valid error info."""
        error = ErrorInfo(
            error_type="ValidationError",
            error_message="Invalid rating provided",
            user_message="Please provide a valid rating between 1-10",
            category="validation",
            confidence=ConfidenceLevel.HIGH,
            error_context={"rating": 15, "field": "rating"},
            retry_count=2,
        )

        assert error.error_type == "ValidationError"
        assert error.error_message == "Invalid rating provided"
        assert error.user_message == "Please provide a valid rating between 1-10"
        assert error.category == "validation"
        assert error.confidence == ConfidenceLevel.HIGH
        assert error.error_context["rating"] == 15
        assert error.retry_count == 2
        assert isinstance(error.timestamp, datetime)

    def test_error_info_defaults(self):
        """Test error info with defaults."""
        error = ErrorInfo(
            error_type="APIError",
            error_message="API request failed",
            user_message="An API error occurred",
            category="api",
            confidence=ConfidenceLevel.MEDIUM,
        )

        assert error.error_type == "APIError"
        assert error.error_message == "API request failed"
        assert error.user_message == "An API error occurred"
        assert error.category == "api"
        assert error.confidence == ConfidenceLevel.MEDIUM
        assert error.context == ""
        assert error.error_context == {}
        assert error.retry_count == 0
        assert isinstance(error.timestamp, datetime)


class TestAnalyticsEvent:
    """Test AnalyticsEvent model."""

    def test_valid_analytics_event(self):
        """Test creating valid analytics event."""
        event = AnalyticsEvent(
            event_type="analysis",
            event_data={"rating": 8, "success": True},
            user_id="user123",
            session_id="session456",
        )

        assert event.event_type == "analysis"
        assert event.event_data["rating"] == 8
        assert event.user_id == "user123"
        assert event.session_id == "session456"
        assert isinstance(event.timestamp, datetime)

    def test_analytics_event_defaults(self):
        """Test analytics event with defaults."""
        event = AnalyticsEvent(event_type="error", event_data={"error": "API timeout"})

        assert event.user_id is None
        assert event.session_id is None
        assert isinstance(event.timestamp, datetime)


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_job_assessment_serialization(self):
        """Test JobAssessment can be serialized to dict."""
        assessment = JobAssessment(
            rating=7,
            strengths="Test",
            gaps="Test",
            missing_requirements="Test",
            recommendation=RecommendationType.YES,
            confidence=ConfidenceLevel.MEDIUM,
        )

        data = assessment.model_dump()

        assert data["rating"] == 7
        assert data["recommendation"] == "Yes"
        assert data["confidence"] == "Medium"

    def test_job_assessment_deserialization(self):
        """Test JobAssessment can be created from dict."""
        data = {
            "rating": 6,
            "strengths": "Test",
            "gaps": "Test",
            "missing_requirements": "Test",
            "recommendation": "No",
            "confidence": "Low",
        }

        assessment = JobAssessment(**data)

        assert assessment.rating == 6
        assert assessment.recommendation == RecommendationType.NO
        assert assessment.confidence == ConfidenceLevel.LOW

    def test_analysis_result_json_serialization(self):
        """Test AnalysisResult can be serialized to JSON."""
        assessment = JobAssessment(
            rating=8,
            strengths="Test",
            gaps="Test",
            missing_requirements="Test",
            recommendation=RecommendationType.YES,
            confidence=ConfidenceLevel.HIGH,
        )

        result = AnalysisResult(assessment=assessment)
        json_data = result.model_dump_json()

        assert '"rating":8' in json_data
        assert '"recommendation":"Yes"' in json_data
        assert '"confidence":"High"' in json_data


if __name__ == "__main__":
    pytest.main([__file__])
