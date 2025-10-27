"""
Structured output parsing using LangChain and Pydantic.
"""

import logging
from typing import List, Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel, Field, ValidationError
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.base import BaseLanguageModel

from .langchain_llm_wrapper import LangChainLLMWrapper

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class JobAnalysisResult(BaseModel):
    """Structured job analysis result."""
    
    suitability_score: float = Field(
        description="Job suitability score from 1-10",
        ge=1.0,
        le=10.0
    )
    match_percentage: float = Field(
        description="Overall match percentage",
        ge=0.0,
        le=100.0
    )
    strengths: List[str] = Field(
        description="List of candidate strengths for this job",
        default_factory=list
    )
    weaknesses: List[str] = Field(
        description="List of areas where candidate doesn't match",
        default_factory=list
    )
    missing_skills: List[str] = Field(
        description="Skills required by job but missing from resume",
        default_factory=list
    )
    recommendations: List[str] = Field(
        description="Specific recommendations for improvement",
        default_factory=list
    )
    overall_assessment: str = Field(
        description="Overall assessment of job fit"
    )


class ResumeImprovementResult(BaseModel):
    """Structured resume improvement suggestions."""
    
    ats_score: float = Field(
        description="ATS compatibility score",
        ge=0.0,
        le=100.0
    )
    keyword_match: float = Field(
        description="Keyword match percentage",
        ge=0.0,
        le=100.0
    )
    formatting_issues: List[str] = Field(
        description="Formatting issues to fix",
        default_factory=list
    )
    content_improvements: List[str] = Field(
        description="Content improvements to make",
        default_factory=list
    )
    missing_keywords: List[str] = Field(
        description="Keywords to add to resume",
        default_factory=list
    )
    section_scores: Dict[str, float] = Field(
        description="Scores for different resume sections",
        default_factory=dict
    )


class InterviewQuestionsResult(BaseModel):
    """Structured interview questions generation."""
    
    behavioral_questions: List[str] = Field(
        description="Behavioral interview questions",
        default_factory=list
    )
    technical_questions: List[str] = Field(
        description="Technical interview questions",
        default_factory=list
    )
    company_specific_questions: List[str] = Field(
        description="Company-specific interview questions",
        default_factory=list
    )
    preparation_tips: List[str] = Field(
        description="Tips for interview preparation",
        default_factory=list
    )
    key_points_to_highlight: List[str] = Field(
        description="Key points to highlight during interview",
        default_factory=list
    )


class StructuredOutputParser:
    """
    Handles structured output parsing using LangChain and Pydantic.
    """
    
    def __init__(self, llm_wrapper: LangChainLLMWrapper):
        self.llm_wrapper = llm_wrapper
        self.llm = llm_wrapper.langchain_llm
    
    def parse_job_analysis(
        self,
        job_description: str,
        resume_content: str,
        system_prompt: Optional[str] = None
    ) -> JobAnalysisResult:
        """
        Parse job analysis with structured output.
        
        Args:
            job_description: Job description text
            resume_content: Resume content text
            system_prompt: Optional custom system prompt
            
        Returns:
            Structured job analysis result
        """
        parser = PydanticOutputParser(pydantic_object=JobAnalysisResult)
        
        if system_prompt is None:
            system_prompt = """You are an expert career advisor analyzing job fit between a candidate's resume and a job description. 
            Provide a comprehensive analysis with specific scores, strengths, weaknesses, and actionable recommendations."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{system_prompt}\n\n{parser.get_format_instructions()}"),
            ("user", "Job Description:\n{job_description}\n\nResume:\n{resume_content}")
        ])
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "job_description": job_description,
                "resume_content": resume_content
            })
            return result
        except ValidationError as e:
            logger.error(f"Validation error in job analysis: {e}")
            # Return a default result with error information
            return JobAnalysisResult(
                suitability_score=5.0,
                match_percentage=50.0,
                overall_assessment=f"Analysis error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error parsing job analysis: {e}")
            raise
    
    def parse_resume_improvement(
        self,
        resume_content: str,
        job_description: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> ResumeImprovementResult:
        """
        Parse resume improvement suggestions with structured output.
        
        Args:
            resume_content: Resume content text
            job_description: Optional job description for targeted improvements
            system_prompt: Optional custom system prompt
            
        Returns:
            Structured resume improvement result
        """
        parser = PydanticOutputParser(pydantic_object=ResumeImprovementResult)
        
        if system_prompt is None:
            system_prompt = """You are an expert resume consultant. Analyze the resume and provide specific, actionable improvement suggestions focusing on ATS compatibility, keyword optimization, and content enhancement."""
        
        if job_description:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"{system_prompt}\n\n{parser.get_format_instructions()}"),
                ("user", "Resume:\n{resume_content}\n\nJob Description (for targeted improvements):\n{job_description}")
            ])
            
            chain = prompt | self.llm | parser
            
            try:
                result = chain.invoke({
                    "resume_content": resume_content,
                    "job_description": job_description
                })
                return result
            except ValidationError as e:
                logger.error(f"Validation error in resume improvement: {e}")
                return ResumeImprovementResult(
                    ats_score=50.0,
                    keyword_match=50.0,
                    content_improvements=[f"Analysis error: {str(e)}"]
                )
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"{system_prompt}\n\n{parser.get_format_instructions()}"),
                ("user", "Resume:\n{resume_content}")
            ])
            
            chain = prompt | self.llm | parser
            
            try:
                result = chain.invoke({
                    "resume_content": resume_content
                })
                return result
            except ValidationError as e:
                logger.error(f"Validation error in resume improvement: {e}")
                return ResumeImprovementResult(
                    ats_score=50.0,
                    keyword_match=50.0,
                    content_improvements=[f"Analysis error: {str(e)}"]
                )
    
    def parse_interview_questions(
        self,
        job_description: str,
        resume_content: str,
        system_prompt: Optional[str] = None
    ) -> InterviewQuestionsResult:
        """
        Parse interview questions generation with structured output.
        
        Args:
            job_description: Job description text
            resume_content: Resume content text
            system_prompt: Optional custom system prompt
            
        Returns:
            Structured interview questions result
        """
        parser = PydanticOutputParser(pydantic_object=InterviewQuestionsResult)
        
        if system_prompt is None:
            system_prompt = """You are an expert interview coach. Generate comprehensive interview questions and preparation tips based on the job description and candidate's background."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{system_prompt}\n\n{parser.get_format_instructions()}"),
            ("user", "Job Description:\n{job_description}\n\nCandidate Resume:\n{resume_content}")
        ])
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "job_description": job_description,
                "resume_content": resume_content
            })
            return result
        except ValidationError as e:
            logger.error(f"Validation error in interview questions: {e}")
            return InterviewQuestionsResult(
                behavioral_questions=["Error generating questions"],
                technical_questions=["Error generating questions"],
                preparation_tips=[f"Analysis error: {str(e)}"]
            )
    
    def parse_custom_model(
        self,
        model_class: Type[T],
        prompt_template: str,
        **kwargs
    ) -> T:
        """
        Parse with a custom Pydantic model.
        
        Args:
            model_class: Custom Pydantic model class
            prompt_template: Prompt template string
            **kwargs: Variables for the prompt template
            
        Returns:
            Parsed result as the specified model type
        """
        parser = PydanticOutputParser(pydantic_object=model_class)
        
        prompt = ChatPromptTemplate.from_template(
            f"{prompt_template}\n\n{{format_instructions}}"
        )
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "format_instructions": parser.get_format_instructions(),
                **kwargs
            })
            return result
        except ValidationError as e:
            logger.error(f"Validation error in custom model parsing: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing custom model: {e}")
            raise
