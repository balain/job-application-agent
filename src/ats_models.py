"""
Pydantic models for ATS (Applicant Tracking System) analysis and resume optimization.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ATSCompatibilityLevel(str, Enum):
    """ATS compatibility levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class IssueSeverity(str, Enum):
    """Severity levels for ATS issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ATSIssue(BaseModel):
    """Individual ATS compatibility issue."""
    
    issue_type: str = Field(description="Type of ATS issue")
    description: str = Field(description="Description of the issue")
    severity: IssueSeverity = Field(description="Severity of the issue")
    suggestion: str = Field(description="How to fix this issue")
    line_number: Optional[int] = Field(default=None, description="Line number where issue occurs")
    
    model_config = {"validate_assignment": True}


class KeywordMatch(BaseModel):
    """Keyword matching result."""
    
    keyword: str = Field(description="The keyword found")
    context: str = Field(description="Context where keyword appears")
    relevance_score: float = Field(description="Relevance score (0.0-1.0)")
    is_required: bool = Field(description="Whether this is a required keyword")
    
    model_config = {"validate_assignment": True}


class SectionScore(BaseModel):
    """Score for a specific resume section."""
    
    section_name: str = Field(description="Name of the resume section")
    score: float = Field(description="Score for this section (0.0-1.0)")
    max_score: float = Field(default=1.0, description="Maximum possible score")
    feedback: str = Field(description="Feedback for this section")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    model_config = {"validate_assignment": True}


class ATSCompatibilityReport(BaseModel):
    """Comprehensive ATS compatibility report."""
    
    overall_score: float = Field(description="Overall ATS compatibility score (0.0-1.0)")
    compatibility_level: ATSCompatibilityLevel = Field(description="Overall compatibility level")
    issues: List[ATSIssue] = Field(default_factory=list, description="List of ATS issues found")
    keyword_matches: List[KeywordMatch] = Field(default_factory=list, description="Keyword matches found")
    section_scores: List[SectionScore] = Field(default_factory=list, description="Scores for each section")
    formatting_score: float = Field(description="Formatting compatibility score (0.0-1.0)")
    content_score: float = Field(description="Content quality score (0.0-1.0)")
    keyword_score: float = Field(description="Keyword optimization score (0.0-1.0)")
    
    @field_validator('overall_score', 'formatting_score', 'content_score', 'keyword_score')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    model_config = {"validate_assignment": True}


class ResumeOptimization(BaseModel):
    """Resume optimization recommendations."""
    
    priority_fixes: List[str] = Field(default_factory=list, description="High priority fixes")
    content_improvements: List[str] = Field(default_factory=list, description="Content improvement suggestions")
    formatting_suggestions: List[str] = Field(default_factory=list, description="Formatting suggestions")
    keyword_additions: List[str] = Field(default_factory=list, description="Keywords to add")
    section_recommendations: Dict[str, str] = Field(default_factory=dict, description="Section-specific recommendations")
    ats_compatibility: ATSCompatibilityReport = Field(description="ATS compatibility analysis")
    
    model_config = {"validate_assignment": True}


class ResumeScore(BaseModel):
    """Overall resume scoring results."""
    
    total_score: float = Field(description="Total resume score (0-100)")
    ats_score: float = Field(description="ATS compatibility score (0-100)")
    content_score: float = Field(description="Content quality score (0-100)")
    formatting_score: float = Field(description="Formatting score (0-100)")
    keyword_score: float = Field(description="Keyword optimization score (0-100)")
    experience_score: float = Field(description="Experience relevance score (0-100)")
    skills_score: float = Field(description="Skills match score (0-100)")
    
    @field_validator('total_score', 'ats_score', 'content_score', 'formatting_score', 
                     'keyword_score', 'experience_score', 'skills_score')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        if not 0.0 <= v <= 100.0:
            raise ValueError('Score must be between 0.0 and 100.0')
        return v
    
    model_config = {"validate_assignment": True}


class FileParseResult(BaseModel):
    """Result of parsing a resume file."""
    
    file_path: str = Field(description="Path to the parsed file")
    file_type: str = Field(description="Type of file (pdf, docx, doc, txt)")
    content: str = Field(description="Extracted text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="File metadata")
    parse_success: bool = Field(description="Whether parsing was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if parsing failed")
    
    model_config = {"validate_assignment": True}
