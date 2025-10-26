"""
Tests for structured parser.

This module tests the StructuredParser class to ensure it correctly
parses LLM responses with both JSON and regex fallback mechanisms.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.structured_parser import StructuredParser
from src.models import (
    JobAssessment, 
    ResumeImprovements, 
    CoverLetter, 
    InterviewQuestions, 
    NextSteps,
    RecommendationType,
    ConfidenceLevel
)


class TestStructuredParser:
    """Test StructuredParser class."""
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Create a mock LLM provider."""
        provider = Mock()
        provider.generate_response = Mock(return_value="Mock response")
        return provider
    
    @pytest.fixture
    def parser(self, mock_llm_provider):
        """Create a StructuredParser instance."""
        return StructuredParser(mock_llm_provider)
    
    def test_init(self, mock_llm_provider):
        """Test parser initialization."""
        parser = StructuredParser(mock_llm_provider)
        assert parser.llm == mock_llm_provider
        assert parser.logger is not None


class TestJSONParsing:
    """Test JSON parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mock provider."""
        mock_provider = Mock()
        return StructuredParser(mock_provider)
    
    def test_extract_json_from_markdown_block(self, parser):
        """Test extracting JSON from markdown code block."""
        response = """
        Here's the analysis:
        
        ```json
        {
            "rating": 8,
            "strengths": "Strong technical background",
            "gaps": "Limited management experience",
            "missing_requirements": "None",
            "recommendation": "Yes",
            "confidence": "High"
        }
        ```
        
        This is the complete analysis.
        """
        
        json_data = parser._extract_json_from_response(response)
        
        assert json_data is not None
        assert json_data["rating"] == 8
        assert json_data["strengths"] == "Strong technical background"
        assert json_data["recommendation"] == "Yes"
    
    def test_extract_json_from_generic_block(self, parser):
        """Test extracting JSON from generic code block."""
        response = """
        Analysis results:
        
        ```
        {
            "rating": 7,
            "recommendation": "No"
        }
        ```
        """
        
        json_data = parser._extract_json_from_response(response)
        
        assert json_data is not None
        assert json_data["rating"] == 7
        assert json_data["recommendation"] == "No"
    
    def test_extract_json_from_plain_object(self, parser):
        """Test extracting JSON from plain object."""
        response = """
        The assessment is: {"rating": 6, "recommendation": "Maybe"}
        """
        
        json_data = parser._extract_json_from_response(response)
        
        assert json_data is not None
        assert json_data["rating"] == 6
        assert json_data["recommendation"] == "Maybe"
    
    def test_extract_json_no_json_found(self, parser):
        """Test when no JSON is found in response."""
        response = "This is just plain text with no JSON."
        
        json_data = parser._extract_json_from_response(response)
        
        assert json_data is None
    
    def test_extract_json_invalid_json(self, parser):
        """Test when invalid JSON is found."""
        response = """
        ```json
        {
            "rating": 8,
            "strengths": "Strong technical background",
            "gaps": "Limited management experience",
            "missing_requirements": "None",
            "recommendation": "Yes",
            "confidence": "High"
        ```
        """
        
        json_data = parser._extract_json_from_response(response)
        
        assert json_data is None


class TestAssessmentParsing:
    """Test assessment parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mock provider."""
        mock_provider = Mock()
        return StructuredParser(mock_provider)
    
    def test_parse_assessment_json_success(self, parser):
        """Test successful JSON parsing of assessment."""
        response = """
        ```json
        {
            "rating": 8,
            "strengths": "Strong technical background in Python and JavaScript",
            "gaps": "Limited experience with cloud platforms",
            "missing_requirements": "None",
            "recommendation": "Yes",
            "confidence": "High"
        }
        ```
        """
        
        assessment = parser.parse_assessment_response(response)
        
        assert isinstance(assessment, JobAssessment)
        assert assessment.rating == 8
        assert assessment.strengths == "Strong technical background in Python and JavaScript"
        assert assessment.gaps == "Limited experience with cloud platforms"
        assert assessment.missing_requirements == "None"
        assert assessment.recommendation == RecommendationType.YES
        assert assessment.confidence == ConfidenceLevel.HIGH
    
    def test_parse_assessment_regex_fallback(self, parser):
        """Test regex fallback parsing of assessment."""
        response = """
        SUITABILITY RATING: 7
        
        STRENGTHS: 
        - Strong technical background
        - Good communication skills
        - Relevant experience
        
        GAPS:
        - Limited management experience
        - No cloud platform experience
        
        MISSING REQUIREMENTS: None
        
        RECOMMENDATION: Yes
        
        CONFIDENCE LEVEL: Medium
        """
        
        assessment = parser.parse_assessment_response(response)
        
        assert isinstance(assessment, JobAssessment)
        assert assessment.rating == 7
        assert "Strong technical background" in assessment.strengths
        assert "Limited management experience" in assessment.gaps
        assert assessment.missing_requirements == "None"
        assert assessment.recommendation == RecommendationType.YES
        assert assessment.confidence == ConfidenceLevel.MEDIUM
    
    def test_parse_assessment_minimal_response(self, parser):
        """Test parsing with minimal response."""
        response = "Rating: 5. Recommendation: No."
        
        assessment = parser.parse_assessment_response(response)
        
        assert isinstance(assessment, JobAssessment)
        assert assessment.rating == 5
        assert assessment.recommendation == RecommendationType.NO
        assert assessment.confidence == ConfidenceLevel.MEDIUM  # Default
    
    def test_parse_assessment_default_values(self, parser):
        """Test parsing with missing fields uses defaults."""
        response = "This is a very minimal response."
        
        assessment = parser.parse_assessment_response(response)
        
        assert isinstance(assessment, JobAssessment)
        assert assessment.rating == 5  # Default
        assert assessment.strengths == "Not specified"
        assert assessment.gaps == "Not specified"
        assert assessment.missing_requirements == "Not specified"
        assert assessment.recommendation == RecommendationType.UNKNOWN
        assert assessment.confidence == ConfidenceLevel.MEDIUM


class TestResumeImprovementsParsing:
    """Test resume improvements parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mock provider."""
        mock_provider = Mock()
        return StructuredParser(mock_provider)
    
    def test_parse_improvements_json_success(self, parser):
        """Test successful JSON parsing of improvements."""
        response = """
        ```json
        {
            "keyword_suggestions": ["Python", "JavaScript", "React"],
            "section_improvements": {
                "experience": "Add more quantifiable achievements",
                "skills": "Include cloud technologies"
            },
            "formatting_fixes": ["Fix inconsistent bullet points"],
            "content_enhancements": ["Add more technical details"],
            "priority_changes": ["Update skills section", "Add project examples"],
            "quick_wins": ["Fix typos", "Update contact info"]
        }
        ```
        """
        
        improvements = parser.parse_resume_improvements(response)
        
        assert isinstance(improvements, ResumeImprovements)
        assert len(improvements.keyword_suggestions) == 3
        assert "Python" in improvements.keyword_suggestions
        assert improvements.section_improvements["experience"] == "Add more quantifiable achievements"
        assert len(improvements.priority_changes) == 2
        assert len(improvements.quick_wins) == 2
    
    def test_parse_improvements_regex_fallback(self, parser):
        """Test regex fallback parsing of improvements."""
        response = """
        KEYWORDS TO ADD:
        - Python
        - JavaScript
        - React
        - AWS
        
        FORMATTING FIXES:
        - Fix inconsistent bullet points
        - Align dates properly
        
        CONTENT ENHANCEMENTS:
        - Add more technical details
        - Include quantifiable achievements
        
        PRIORITY CHANGES:
        - Update skills section
        - Add project examples
        - Include certifications
        
        QUICK WINS:
        - Fix typos
        - Update contact info
        """
        
        improvements = parser.parse_resume_improvements(response)
        
        assert isinstance(improvements, ResumeImprovements)
        assert len(improvements.keyword_suggestions) >= 4
        assert "Python" in improvements.keyword_suggestions
        assert len(improvements.formatting_fixes) >= 2
        assert len(improvements.content_enhancements) >= 2
        assert len(improvements.priority_changes) >= 3
        assert len(improvements.quick_wins) >= 2


class TestCoverLetterParsing:
    """Test cover letter parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mock provider."""
        mock_provider = Mock()
        return StructuredParser(mock_provider)
    
    def test_parse_cover_letter_json_success(self, parser):
        """Test successful JSON parsing of cover letter."""
        response = """
        ```json
        {
            "opening": "Dear Hiring Manager,",
            "body": "I am writing to express my interest in the Software Engineer position...",
            "closing": "Thank you for your consideration.",
            "full_letter": "Dear Hiring Manager,\\n\\nI am writing to express my interest..."
        }
        ```
        """
        
        cover_letter = parser.parse_cover_letter(response)
        
        assert isinstance(cover_letter, CoverLetter)
        assert cover_letter.opening == "Dear Hiring Manager,"
        assert "Software Engineer" in cover_letter.body
        assert cover_letter.closing == "Thank you for your consideration."
    
    def test_parse_cover_letter_regex_fallback(self, parser):
        """Test regex fallback parsing of cover letter."""
        response = """
        OPENING: Dear Hiring Manager,
        
        BODY: I am writing to express my interest in the Software Engineer position at your company. With my 5 years of experience in Python and JavaScript, I believe I would be a great fit for this role.
        
        CLOSING: Thank you for your consideration. I look forward to hearing from you.
        """
        
        cover_letter = parser.parse_cover_letter(response)
        
        assert isinstance(cover_letter, CoverLetter)
        assert "Dear Hiring Manager" in cover_letter.opening
        assert "Software Engineer" in cover_letter.body
        assert "Thank you" in cover_letter.closing
        assert "Dear Hiring Manager" in cover_letter.full_letter


class TestInterviewQuestionsParsing:
    """Test interview questions parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mock provider."""
        mock_provider = Mock()
        return StructuredParser(mock_provider)
    
    def test_parse_interview_questions_json_success(self, parser):
        """Test successful JSON parsing of interview questions."""
        response = """
        ```json
        {
            "questions_for_employer": [
                "What is the team structure?",
                "What technologies do you use?"
            ],
            "anticipated_questions": [
                "Tell me about yourself",
                "Why do you want this job?"
            ],
            "suggested_answers": [
                "I am a software engineer with 5 years experience...",
                "I am excited about this opportunity because..."
            ]
        }
        ```
        """
        
        questions = parser.parse_interview_questions(response)
        
        assert isinstance(questions, InterviewQuestions)
        assert len(questions.questions_for_employer) == 2
        assert "team structure" in questions.questions_for_employer[0]
        assert len(questions.anticipated_questions) == 2
        assert len(questions.suggested_answers) == 2
    
    def test_parse_interview_questions_regex_fallback(self, parser):
        """Test regex fallback parsing of interview questions."""
        response = """
        QUESTIONS TO ASK EMPLOYER:
        - What is the team structure?
        - What technologies do you use?
        - What are the growth opportunities?
        
        ANTICIPATED QUESTIONS:
        - Tell me about yourself
        - Why do you want this job?
        - What are your strengths?
        
        SUGGESTED ANSWERS:
        - I am a software engineer with 5 years experience...
        - I am excited about this opportunity because...
        - My main strengths are technical skills and teamwork...
        """
        
        questions = parser.parse_interview_questions(response)
        
        assert isinstance(questions, InterviewQuestions)
        assert len(questions.questions_for_employer) >= 3
        assert len(questions.anticipated_questions) >= 3
        assert len(questions.suggested_answers) >= 3


class TestNextStepsParsing:
    """Test next steps parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mock provider."""
        mock_provider = Mock()
        return StructuredParser(mock_provider)
    
    def test_parse_next_steps_json_success(self, parser):
        """Test successful JSON parsing of next steps."""
        response = """
        ```json
        {
            "immediate_actions": [
                "Update resume",
                "Prepare cover letter"
            ],
            "short_term_preparation": [
                "Research company",
                "Practice interview questions"
            ],
            "long_term_development": [
                "Learn new technologies",
                "Build portfolio projects"
            ],
            "application_strategy": [
                "Apply to similar positions",
                "Network with industry professionals"
            ],
            "risk_mitigation": [
                "Have backup options",
                "Prepare for rejection"
            ]
        }
        ```
        """
        
        steps = parser.parse_next_steps(response)
        
        assert isinstance(steps, NextSteps)
        assert len(steps.immediate_actions) == 2
        assert "Update resume" in steps.immediate_actions
        assert len(steps.short_term_preparation) == 2
        assert len(steps.long_term_development) == 2
        assert len(steps.application_strategy) == 2
        assert len(steps.risk_mitigation) == 2
    
    def test_parse_next_steps_regex_fallback(self, parser):
        """Test regex fallback parsing of next steps."""
        response = """
        IMMEDIATE ACTIONS:
        - Update resume
        - Prepare cover letter
        - Research company
        
        SHORT-TERM PREPARATION:
        - Practice interview questions
        - Prepare portfolio
        - Network with employees
        
        LONG-TERM DEVELOPMENT:
        - Learn new technologies
        - Build portfolio projects
        - Get certifications
        
        APPLICATION STRATEGY:
        - Apply to similar positions
        - Network with industry professionals
        - Follow up on applications
        
        RISK MITIGATION:
        - Have backup options
        - Prepare for rejection
        - Keep applying to other jobs
        """
        
        steps = parser.parse_next_steps(response)
        
        assert isinstance(steps, NextSteps)
        assert len(steps.immediate_actions) >= 3
        assert len(steps.short_term_preparation) >= 3
        assert len(steps.long_term_development) >= 3
        assert len(steps.application_strategy) >= 3
        assert len(steps.risk_mitigation) >= 3


class TestHelperMethods:
    """Test helper methods."""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mock provider."""
        mock_provider = Mock()
        return StructuredParser(mock_provider)
    
    def test_extract_section_content_success(self, parser):
        """Test successful section content extraction."""
        response = "STRENGTHS: Strong technical background and good communication skills."
        
        content = parser._extract_section_content(
            response, 
            [r'strengths[:\s]*(.*?)(?=\n|$)'], 
            "Not specified"
        )
        
        assert "Strong technical background" in content
    
    def test_extract_section_content_default(self, parser):
        """Test section content extraction with default."""
        response = "This response has no strengths section."
        
        content = parser._extract_section_content(
            response, 
            [r'strengths[:\s]*(.*?)(?=\n|$)'], 
            "Not specified"
        )
        
        assert content == "Not specified"
    
    def test_extract_list_content_success(self, parser):
        """Test successful list content extraction."""
        response = """
        KEYWORDS:
        - Python
        - JavaScript
        - React
        """
        
        content = parser._extract_list_content(
            response,
            [r'keywords[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)']
        )
        
        assert len(content) >= 3
        assert "Python" in content
        assert "JavaScript" in content
        assert "React" in content
    
    def test_extract_recommendation_success(self, parser):
        """Test successful recommendation extraction."""
        response = "RECOMMENDATION: Yes, proceed with application."
        
        recommendation = parser._extract_recommendation(
            response,
            [r'recommendation[:\s]*(yes|no|maybe)']
        )
        
        assert recommendation == RecommendationType.YES
    
    def test_extract_confidence_success(self, parser):
        """Test successful confidence extraction."""
        response = "CONFIDENCE LEVEL: High"
        
        confidence = parser._extract_confidence(
            response,
            [r'confidence level[:\s]*(high|medium|low)']
        )
        
        assert confidence == ConfidenceLevel.HIGH
    
    def test_validate_parsing_success_json(self, parser):
        """Test validation with successful JSON parsing."""
        response = """
        ```json
        {
            "rating": 8,
            "recommendation": "Yes"
        }
        ```
        """
        
        is_valid = parser.validate_parsing_success(
            response, 
            ["rating", "recommendation"]
        )
        
        assert is_valid is True
    
    def test_validate_parsing_success_regex(self, parser):
        """Test validation with regex parsing."""
        response = "Rating: 7. Recommendation: No."
        
        is_valid = parser.validate_parsing_success(
            response, 
            ["rating", "recommendation"]
        )
        
        assert is_valid is True
    
    def test_validate_parsing_failure(self, parser):
        """Test validation failure."""
        response = "This response has no useful information."
        
        is_valid = parser.validate_parsing_success(
            response, 
            ["rating", "recommendation"]
        )
        
        assert is_valid is False


if __name__ == "__main__":
    pytest.main([__file__])
