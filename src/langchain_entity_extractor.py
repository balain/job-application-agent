"""
Entity extraction using LangChain and structured outputs.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .langchain_llm_wrapper import LangChainLLMWrapper
from .langchain_structured_parser import StructuredOutputParser

logger = logging.getLogger(__name__)


class JobEntities(BaseModel):
    """Structured job description entities."""
    
    company: str = Field(description="Company name")
    job_title: str = Field(description="Job title")
    skills: List[str] = Field(description="Required skills")
    industry: str = Field(description="Industry sector")
    seniority: str = Field(description="Seniority level")
    location: str = Field(description="Job location")
    salary_range: Optional[str] = Field(description="Salary range if mentioned", default=None)
    employment_type: str = Field(description="Employment type (full-time, part-time, contract, etc.)", default="full-time")
    remote_option: bool = Field(description="Whether remote work is mentioned", default=False)
    experience_required: Optional[str] = Field(description="Experience requirements", default=None)


class ResumeEntities(BaseModel):
    """Structured resume entities."""
    
    name: str = Field(description="Candidate name")
    email: Optional[str] = Field(description="Email address", default=None)
    phone: Optional[str] = Field(description="Phone number", default=None)
    skills: List[str] = Field(description="Skills listed")
    years_experience: int = Field(description="Total years of experience")
    current_role: str = Field(description="Current or most recent role")
    education: List[str] = Field(description="Education background", default_factory=list)
    certifications: List[str] = Field(description="Certifications", default_factory=list)
    languages: List[str] = Field(description="Languages spoken", default_factory=list)
    location: Optional[str] = Field(description="Current location", default=None)


class CompanyEntities(BaseModel):
    """Structured company information."""
    
    company_name: str = Field(description="Company name")
    industry: str = Field(description="Primary industry")
    company_size: Optional[str] = Field(description="Company size (startup, small, medium, large)", default=None)
    headquarters: Optional[str] = Field(description="Headquarters location", default=None)
    founded_year: Optional[int] = Field(description="Year founded", default=None)
    description: Optional[str] = Field(description="Company description", default=None)
    website: Optional[str] = Field(description="Company website", default=None)


class LangChainEntityExtractor:
    """
    Entity extraction using LangChain and structured outputs.
    """
    
    def __init__(self, llm_wrapper: LangChainLLMWrapper):
        self.llm_wrapper = llm_wrapper
        self.llm = llm_wrapper.langchain_llm
        
        # Initialize parsers
        self.job_parser = PydanticOutputParser(pydantic_object=JobEntities)
        self.resume_parser = PydanticOutputParser(pydantic_object=ResumeEntities)
        self.company_parser = PydanticOutputParser(pydantic_object=CompanyEntities)
    
    def extract_from_job_description(self, job_desc: str) -> JobEntities:
        """
        Extract entities from job description.
        
        Args:
            job_desc: Job description text
            
        Returns:
            Structured job entities
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting structured information from job descriptions. 
            Extract all relevant entities including company name, job title, required skills, industry, 
            seniority level, location, salary information, and employment details."""),
            ("user", "{format_instructions}\n\nJob Description:\n{job_desc}")
        ])
        
        chain = prompt | self.llm | self.job_parser
        
        try:
            result = chain.invoke({
                "job_desc": job_desc,
                "format_instructions": self.job_parser.get_format_instructions()
            })
            return result
        except Exception as e:
            logger.error(f"Error extracting job entities: {e}")
            # Return a default result
            return JobEntities(
                company="Unknown",
                job_title="Unknown",
                skills=[],
                industry="Unknown",
                seniority="Unknown",
                location="Unknown"
            )
    
    def extract_from_resume(self, resume: str) -> ResumeEntities:
        """
        Extract entities from resume.
        
        Args:
            resume: Resume content text
            
        Returns:
            Structured resume entities
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting structured information from resumes. 
            Extract all relevant entities including name, contact information, skills, experience, 
            education, certifications, and other relevant details."""),
            ("user", "{format_instructions}\n\nResume:\n{resume}")
        ])
        
        chain = prompt | self.llm | self.resume_parser
        
        try:
            result = chain.invoke({
                "resume": resume,
                "format_instructions": self.resume_parser.get_format_instructions()
            })
            return result
        except Exception as e:
            logger.error(f"Error extracting resume entities: {e}")
            # Return a default result
            return ResumeEntities(
                name="Unknown",
                skills=[],
                years_experience=0,
                current_role="Unknown"
            )
    
    def extract_company_info(self, company_text: str) -> CompanyEntities:
        """
        Extract company information from text.
        
        Args:
            company_text: Company description or information text
            
        Returns:
            Structured company entities
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting company information from text. 
            Extract company name, industry, size, location, founding year, description, and website if available."""),
            ("user", "{format_instructions}\n\nCompany Information:\n{company_text}")
        ])
        
        chain = prompt | self.llm | self.company_parser
        
        try:
            result = chain.invoke({
                "company_text": company_text,
                "format_instructions": self.company_parser.get_format_instructions()
            })
            return result
        except Exception as e:
            logger.error(f"Error extracting company entities: {e}")
            # Return a default result
            return CompanyEntities(
                company_name="Unknown",
                industry="Unknown"
            )
    
    def extract_all_entities(self, job_desc: str, resume: str) -> Dict[str, Any]:
        """
        Extract entities from both job description and resume.
        
        Args:
            job_desc: Job description text
            resume: Resume content text
            
        Returns:
            Dictionary containing all extracted entities
        """
        try:
            job_entities = self.extract_from_job_description(job_desc)
            resume_entities = self.extract_from_resume(resume)
            
            return {
                "job": job_entities.dict(),
                "resume": resume_entities.dict(),
                "extraction_success": True
            }
        except Exception as e:
            logger.error(f"Error extracting all entities: {e}")
            return {
                "job": {},
                "resume": {},
                "extraction_success": False,
                "error": str(e)
            }
    
    def get_skill_match_analysis(self, job_desc: str, resume: str) -> Dict[str, Any]:
        """
        Analyze skill match between job description and resume.
        
        Args:
            job_desc: Job description text
            resume: Resume content text
            
        Returns:
            Skill match analysis
        """
        try:
            job_entities = self.extract_from_job_description(job_desc)
            resume_entities = self.extract_from_resume(resume)
            
            job_skills = set(skill.lower() for skill in job_entities.skills)
            resume_skills = set(skill.lower() for skill in resume_entities.skills)
            
            matched_skills = job_skills.intersection(resume_skills)
            missing_skills = job_skills - resume_skills
            extra_skills = resume_skills - job_skills
            
            match_percentage = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
            
            return {
                "matched_skills": list(matched_skills),
                "missing_skills": list(missing_skills),
                "extra_skills": list(extra_skills),
                "match_percentage": round(match_percentage, 2),
                "total_job_skills": len(job_skills),
                "total_resume_skills": len(resume_skills),
                "analysis_success": True
            }
        except Exception as e:
            logger.error(f"Error analyzing skill match: {e}")
            return {
                "matched_skills": [],
                "missing_skills": [],
                "extra_skills": [],
                "match_percentage": 0.0,
                "analysis_success": False,
                "error": str(e)
            }
