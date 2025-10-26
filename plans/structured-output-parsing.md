# Structured Output Parsing & Reliability

## Overview

Implement structured output parsing using Pydantic models to replace fragile regex parsing, add comprehensive error handling, and improve LLM response reliability. This foundation will make the entire application more robust and reliable.

## Prerequisites

- Existing LLM provider working (Claude/Ollama)
- Current analysis workflow functional

## Implementation Steps

### 1. Create Structured Output Models (`src/models.py`)

**New file**: `src/models.py`

Implement Pydantic models for all LLM responses:

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from enum import Enum

class RecommendationType(str, Enum):
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"

class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class JobAssessment(BaseModel):
    """Structured assessment result from LLM"""
    rating: int = Field(ge=1, le=10, description="Suitability rating 1-10")
    strengths: str = Field(description="Candidate strengths analysis")
    gaps: str = Field(description="Areas for improvement")
    missing_requirements: str = Field(description="Missing requirements")
    recommendation: RecommendationType = Field(description="Should proceed with application")
    confidence: ConfidenceLevel = Field(description="Assessment confidence level")
    
    @validator('rating')
    def validate_rating(cls, v):
        if not isinstance(v, int) or v < 1 or v > 10:
            raise ValueError('Rating must be integer between 1-10')
        return v

class ResumeImprovements(BaseModel):
    """Structured resume improvement suggestions"""
    keyword_suggestions: List[str] = Field(description="Keywords to add")
    section_improvements: dict = Field(description="Section-specific improvements")
    formatting_fixes: List[str] = Field(description="Formatting issues to fix")
    content_enhancements: List[str] = Field(description="Content improvements")
    priority_changes: List[str] = Field(description="Top 3 most important changes")
    quick_wins: List[str] = Field(description="Simple immediate changes")

class CoverLetter(BaseModel):
    """Structured cover letter"""
    opening: str = Field(description="Opening paragraph")
    body: str = Field(description="Main body paragraphs")
    closing: str = Field(description="Closing paragraph")
    full_letter: str = Field(description="Complete formatted letter")

class InterviewQuestions(BaseModel):
    """Structured interview questions and answers"""
    questions_for_employer: List[str] = Field(description="Questions to ask hiring manager")
    anticipated_questions: List[str] = Field(description="Questions interviewer might ask")
    suggested_answers: List[str] = Field(description="Suggested answers to anticipated questions")

class NextSteps(BaseModel):
    """Structured action plan"""
    immediate_actions: List[str] = Field(description="Next 1-2 days")
    short_term_preparation: List[str] = Field(description="Next week")
    long_term_development: List[str] = Field(description="Next month")
    application_strategy: List[str] = Field(description="Application approach")
    risk_mitigation: List[str] = Field(description="Challenges and solutions")
```

**Dependencies to add**:
- `pydantic>=2.0.0` - Structured data validation

### 2. Create Structured Parser (`src/structured_parser.py`)

**New file**: `src/structured_parser.py`

Implement structured parsing with fallback mechanisms:

```python
from typing import Dict, Any, Optional
import json
import re
from .models import JobAssessment, ResumeImprovements, CoverLetter, InterviewQuestions, NextSteps
from .llm_provider import LLMProvider

class StructuredParser:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    def parse_assessment_response(self, response: str) -> JobAssessment:
        """Parse assessment response with structured fallback"""
        try:
            # Try JSON parsing first
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                return JobAssessment(**json_data)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback to regex parsing
        return self._parse_assessment_regex(response)
    
    def parse_resume_improvements(self, response: str) -> ResumeImprovements:
        """Parse resume improvements with structured fallback"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                return ResumeImprovements(**json_data)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback to regex parsing
        return self._parse_improvements_regex(response)
    
    def _parse_assessment_regex(self, response: str) -> JobAssessment:
        """Fallback regex parsing for assessment"""
        rating_match = re.search(r'SUITABILITY RATING[:\s]*(\d+)', response, re.IGNORECASE)
        rating = int(rating_match.group(1)) if rating_match else 5
        
        strengths_match = re.search(r'STRENGTHS[:\s]*(.*?)(?=GAPS|MISSING|$)', response, re.IGNORECASE | re.DOTALL)
        strengths = strengths_match.group(1).strip() if strengths_match else "Not specified"
        
        gaps_match = re.search(r'GAPS[:\s]*(.*?)(?=MISSING|$)', response, re.IGNORECASE | re.DOTALL)
        gaps = gaps_match.group(1).strip() if gaps_match else "Not specified"
        
        missing_match = re.search(r'MISSING REQUIREMENTS[:\s]*(.*?)(?=RECOMMENDATION|$)', response, re.IGNORECASE | re.DOTALL)
        missing_requirements = missing_match.group(1).strip() if missing_match else "Not specified"
        
        rec_match = re.search(r'RECOMMENDATION[:\s]*(Yes|No)', response, re.IGNORECASE)
        recommendation = rec_match.group(1) if rec_match else "Unknown"
        
        conf_match = re.search(r'CONFIDENCE LEVEL[:\s]*(High|Medium|Low)', response, re.IGNORECASE)
        confidence = conf_match.group(1) if conf_match else "Medium"
        
        return JobAssessment(
            rating=rating,
            strengths=strengths,
            gaps=gaps,
            missing_requirements=missing_requirements,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _parse_improvements_regex(self, response: str) -> ResumeImprovements:
        """Fallback regex parsing for improvements"""
        # Extract keyword suggestions
        keyword_match = re.search(r'KEYWORDS? TO ADD[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)', response, re.IGNORECASE | re.DOTALL)
        keywords = keyword_match.group(1).strip().split('\n') if keyword_match else []
        
        # Extract formatting fixes
        format_match = re.search(r'FORMATTING[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)', response, re.IGNORECASE | re.DOTALL)
        formatting = format_match.group(1).strip().split('\n') if format_match else []
        
        return ResumeImprovements(
            keyword_suggestions=keywords,
            section_improvements={},
            formatting_fixes=formatting,
            content_enhancements=[],
            priority_changes=[],
            quick_wins=[]
        )
```

### 3. Update Prompt Templates (`src/prompts.py`)

**Modify existing**: `src/prompts.py`

Update prompts to request structured JSON output:

```python
@staticmethod
def get_assessment_prompt(job_description: str, resume: str) -> str:
    """Generate prompt for structured assessment"""
    return f"""You are an expert career advisor. Analyze this job application and provide a structured assessment.

JOB DESCRIPTION:
{job_description}

CANDIDATE'S RESUME:
{resume}

Please provide your response in this exact JSON format:
{{
    "rating": <integer 1-10>,
    "strengths": "<detailed strengths analysis>",
    "gaps": "<areas for improvement>",
    "missing_requirements": "<missing requirements>",
    "recommendation": "<Yes/No/Unknown>",
    "confidence": "<High/Medium/Low>"
}}

Be specific and reference concrete examples from both the job description and resume."""

@staticmethod
def get_resume_improvement_prompt(job_description: str, resume: str, assessment: str) -> str:
    """Generate prompt for structured resume improvements"""
    return f"""Based on the job description, resume, and assessment, provide structured improvement recommendations.

JOB DESCRIPTION:
{job_description}

CURRENT RESUME:
{resume}

PREVIOUS ASSESSMENT:
{assessment}

Please provide your response in this exact JSON format:
{{
    "keyword_suggestions": ["keyword1", "keyword2"],
    "section_improvements": {{"experience": "improvement", "skills": "improvement"}},
    "formatting_fixes": ["fix1", "fix2"],
    "content_enhancements": ["enhancement1", "enhancement2"],
    "priority_changes": ["change1", "change2", "change3"],
    "quick_wins": ["win1", "win2"]
}}

Focus on making the resume more aligned with the job requirements while maintaining honesty and accuracy."""
```

### 4. Update Analyzer (`src/analyzer.py`)

**Modify existing**: `src/analyzer.py`

Replace regex parsing with structured parsing:

```python
# Replace existing _parse_assessment_response method
def _parse_assessment_response(self, response: str) -> AssessmentResult:
    """Parse the LLM response using structured parser"""
    from .structured_parser import StructuredParser
    
    parser = StructuredParser(self.llm_provider)
    structured_result = parser.parse_assessment_response(response)
    
    # Convert to existing AssessmentResult format for compatibility
    return AssessmentResult(
        rating=structured_result.rating,
        strengths=structured_result.strengths,
        gaps=structured_result.gaps,
        missing_requirements=structured_result.missing_requirements,
        recommendation=structured_result.recommendation.value,
        confidence=structured_result.confidence.value,
        raw_response=response
    )

# Update _parse_questions_response method
def _parse_questions_response(self, response: str) -> Dict[str, str]:
    """Parse interview questions response using structured parser"""
    from .structured_parser import StructuredParser
    
    parser = StructuredParser(self.llm_provider)
    structured_result = parser.parse_interview_questions(response)
    
    return {
        'questions_for_employer': '\n'.join(structured_result.questions_for_employer),
        'anticipated_questions': '\n'.join(structured_result.anticipated_questions),
        'suggested_answers': '\n'.join(structured_result.suggested_answers)
    }
```

### 5. Add Error Handling & Retry Logic (`src/error_handler.py`)

**New file**: `src/error_handler.py`

Implement comprehensive error handling:

```python
import time
import logging
from typing import Callable, Any, Optional
from functools import wraps

class ErrorHandler:
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
    
    def retry_on_failure(self, func: Callable) -> Callable:
        """Decorator to retry function on failure"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {self.retry_delay}s...")
                        time.sleep(self.retry_delay)
                    else:
                        self.logger.error(f"All {self.max_retries + 1} attempts failed")
            
            raise last_exception
        return wrapper
    
    def handle_llm_error(self, error: Exception) -> str:
        """Handle LLM-specific errors gracefully"""
        if "rate limit" in str(error).lower():
            return "Rate limit exceeded. Please try again later."
        elif "timeout" in str(error).lower():
            return "Request timed out. Please try again."
        elif "invalid" in str(error).lower():
            return "Invalid request. Please check your input."
        else:
            return f"LLM error: {str(error)}"
    
    def validate_response(self, response: str, expected_fields: list) -> bool:
        """Validate LLM response has expected structure"""
        try:
            import json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return all(field in data for field in expected_fields)
        except:
            pass
        return False
```

### 6. Update Configuration (`config.py`)

**Modify existing**: `config.py`

Add structured parsing configuration:

```python
# Structured parsing settings
STRUCTURED_PARSING_ENABLED = os.getenv("STRUCTURED_PARSING_ENABLED", "true").lower() == "true"
FALLBACK_TO_REGEX = os.getenv("FALLBACK_TO_REGEX", "true").lower() == "true"
MAX_PARSING_RETRIES = int(os.getenv("MAX_PARSING_RETRIES", "3"))
PARSING_RETRY_DELAY = float(os.getenv("PARSING_RETRY_DELAY", "1.0"))

# Error handling settings
ENABLE_RETRY_LOGIC = os.getenv("ENABLE_RETRY_LOGIC", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

### 7. Update Dependencies (`pyproject.toml`)

**Modify existing**: `pyproject.toml`

Add to dependencies:
```toml
"pydantic>=2.0.0",  # Structured data validation
```

### 8. Update Documentation (`README.md`)

**Modify existing**: `README.md`

Add new section:

**Structured Output Parsing** (new section after "How It Works"):
- Explain improved reliability with structured parsing
- Document fallback mechanisms
- Explain error handling and retry logic
- Show example of structured vs unstructured output

**Environment Variables** (update existing):
```
STRUCTURED_PARSING_ENABLED=true
FALLBACK_TO_REGEX=true
MAX_PARSING_RETRIES=3
PARSING_RETRY_DELAY=1.0
ENABLE_RETRY_LOGIC=true
LOG_LEVEL=INFO
```

## Testing Strategy

1. Test structured parsing with valid JSON responses
2. Test fallback to regex parsing with malformed responses
3. Test error handling and retry logic
4. Test validation of structured responses
5. Test backward compatibility with existing output format
6. Test performance impact of structured parsing
7. Test with various LLM providers (Claude, Ollama)

## Integration Points

**With existing analyzer**:
- Seamless replacement of regex parsing
- Maintains existing output format for compatibility
- Adds structured data validation

**With LLM providers**:
- Works with both Claude and Ollama
- Handles provider-specific response formats
- Implements retry logic for reliability

## Security Considerations

- Validate all structured input to prevent injection
- Sanitize error messages to avoid information leakage
- Implement rate limiting for retry attempts
- Log errors without exposing sensitive data

## Performance Considerations

- Cache parsed responses to avoid re-parsing
- Implement efficient JSON extraction
- Limit retry attempts to prevent infinite loops
- Use async operations where possible

## Files to Create/Modify

**New Files**:
- `src/models.py` (Pydantic models)
- `src/structured_parser.py` (Structured parsing logic)
- `src/error_handler.py` (Error handling and retry logic)

**Modified Files**:
- `src/prompts.py` (Update prompts for structured output)
- `src/analyzer.py` (Replace regex parsing)
- `config.py` (Add parsing configuration)
- `pyproject.toml` (Add pydantic dependency)
- `README.md` (Add documentation)

## Success Criteria

- 95%+ success rate in parsing LLM responses
- Graceful fallback to regex when structured parsing fails
- Comprehensive error handling with retry logic
- Backward compatibility with existing output format
- Performance impact < 10% overhead
- Clear documentation and examples
- All tests passing

## Future Enhancements

- Machine learning for response format detection
- Dynamic prompt optimization based on parsing success
- Advanced validation rules for different response types
- Integration with LangChain for enhanced reliability

## To-dos

- [ ] Create src/models.py with Pydantic models for all LLM responses
- [ ] Create src/structured_parser.py with structured parsing and fallback logic
- [ ] Create src/error_handler.py with retry logic and error handling
- [ ] Update src/prompts.py to request structured JSON output
- [ ] Update src/analyzer.py to use structured parsing instead of regex
- [ ] Add structured parsing configuration to config.py
- [ ] Add pydantic dependency to pyproject.toml
- [ ] Update README.md with structured parsing documentation
