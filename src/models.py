"""
Pydantic models for structured output parsing.

This module defines all the data models used for parsing LLM responses
into structured, validated data structures.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Union, Dict, Any
from enum import Enum
from datetime import datetime


class RecommendationType(str, Enum):
    """Enumeration for application recommendations."""
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"


class ConfidenceLevel(str, Enum):
    """Enumeration for confidence levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class JobAssessment(BaseModel):
    """Structured assessment result from LLM."""
    
    rating: int = Field(
        ge=1, 
        le=10, 
        description="Suitability rating 1-10"
    )
    strengths: str = Field(
        description="Candidate strengths analysis"
    )
    gaps: str = Field(
        description="Areas for improvement"
    )
    missing_requirements: str = Field(
        description="Missing requirements"
    )
    recommendation: RecommendationType = Field(
        description="Should proceed with application"
    )
    confidence: ConfidenceLevel = Field(
        description="Assessment confidence level"
    )
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        """Validate rating is within acceptable range."""
        if not isinstance(v, int) or v < 1 or v > 10:
            raise ValueError('Rating must be integer between 1-10')
        return v
    
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True
    )


class ResumeImprovements(BaseModel):
    """Structured resume improvement suggestions."""
    
    keyword_suggestions: List[str] = Field(
        default_factory=list,
        description="Keywords to add to resume"
    )
    section_improvements: Dict[str, str] = Field(
        default_factory=dict,
        description="Section-specific improvements"
    )
    formatting_fixes: List[str] = Field(
        default_factory=list,
        description="Formatting issues to fix"
    )
    content_enhancements: List[str] = Field(
        default_factory=list,
        description="Content improvements"
    )
    priority_changes: List[str] = Field(
        default_factory=list,
        description="Top 3 most important changes"
    )
    quick_wins: List[str] = Field(
        default_factory=list,
        description="Simple immediate changes"
    )
    
    model_config = ConfigDict(validate_assignment=True)


class CoverLetter(BaseModel):
    """Structured cover letter."""
    
    opening: str = Field(
        description="Opening paragraph"
    )
    body: str = Field(
        description="Main body paragraphs"
    )
    closing: str = Field(
        description="Closing paragraph"
    )
    full_letter: str = Field(
        description="Complete formatted letter"
    )
    
    model_config = ConfigDict(validate_assignment=True)


class InterviewQuestions(BaseModel):
    """Structured interview questions and answers."""
    
    questions_for_employer: List[str] = Field(
        default_factory=list,
        description="Questions to ask hiring manager"
    )
    anticipated_questions: List[str] = Field(
        default_factory=list,
        description="Questions interviewer might ask"
    )
    suggested_answers: List[str] = Field(
        default_factory=list,
        description="Suggested answers to anticipated questions"
    )
    
    model_config = ConfigDict(validate_assignment=True)


class NextSteps(BaseModel):
    """Structured action plan."""
    
    immediate_actions: List[str] = Field(
        default_factory=list,
        description="Next 1-2 days"
    )
    short_term_preparation: List[str] = Field(
        default_factory=list,
        description="Next week"
    )
    long_term_development: List[str] = Field(
        default_factory=list,
        description="Next month"
    )
    application_strategy: List[str] = Field(
        default_factory=list,
        description="Application approach"
    )
    risk_mitigation: List[str] = Field(
        default_factory=list,
        description="Challenges and solutions"
    )
    
    model_config = ConfigDict(validate_assignment=True)


class AnalysisResult(BaseModel):
    """Complete analysis result containing all components."""
    
    assessment: JobAssessment = Field(
        description="Job assessment results"
    )
    resume_improvements: Optional[ResumeImprovements] = Field(
        default=None,
        description="Resume improvement suggestions"
    )
    cover_letter: Optional[CoverLetter] = Field(
        default=None,
        description="Generated cover letter"
    )
    interview_questions: Optional[InterviewQuestions] = Field(
        default=None,
        description="Interview questions and answers"
    )
    next_steps: Optional[NextSteps] = Field(
        default=None,
        description="Action plan and next steps"
    )
    analysis_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the analysis was performed"
    )
    raw_response: Optional[str] = Field(
        default=None,
        description="Raw LLM response for debugging"
    )
    
    model_config = ConfigDict(validate_assignment=True)


class ErrorInfo(BaseModel):
    """Error information for structured error handling."""
    
    error_type: str = Field(
        description="Type of error that occurred"
    )
    error_message: str = Field(
        description="Human-readable error message"
    )
    error_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context about the error"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the error occurred"
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts made"
    )
    
    model_config = ConfigDict(validate_assignment=True)


class AnalyticsEvent(BaseModel):
    """Analytics event for tracking usage and performance."""
    
    event_type: str = Field(
        description="Type of event (analysis, error, etc.)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the event occurred"
    )
    event_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User identifier (if available)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session identifier (if available)"
    )
    
    model_config = ConfigDict(validate_assignment=True)
