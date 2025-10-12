"""Core analysis engine for job application assessment."""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

from rich.console import Console

from .llm_provider import LLMProvider
from .prompts import PromptTemplates

console = Console()


@dataclass
class AssessmentResult:
    """Container for assessment results."""
    rating: int
    strengths: str
    gaps: str
    missing_requirements: str
    recommendation: str
    confidence: str
    raw_response: str


@dataclass
class ApplicationMaterials:
    """Container for generated application materials."""
    resume_improvements: str
    cover_letter: str
    questions_for_employer: str
    anticipated_questions: str
    suggested_answers: str
    next_steps: str


class JobApplicationAnalyzer:
    """Main analyzer for job application assessment."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def analyze_application(self, job_description: str, resume: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of job application.
        
        Args:
            job_description: The job description text
            resume: The resume text
            
        Returns:
            Dictionary containing all analysis results
        """
        console.print("[bold blue]Starting job application analysis...[/bold blue]", file=sys.stderr)
        
        # Step 1: Initial assessment
        console.print("[yellow]Step 1: Assessing job suitability...[/yellow]", file=sys.stderr)
        assessment = self._perform_initial_assessment(job_description, resume)
        
        # Step 2: Generate additional materials if recommended
        materials = None
        if self._should_proceed_with_application(assessment):
            console.print("[yellow]Step 2: Generating application materials...[/yellow]", file=sys.stderr)
            materials = self._generate_application_materials(
                job_description, resume, assessment.raw_response
            )
        
        return {
            'assessment': assessment,
            'materials': materials,
            'should_proceed': self._should_proceed_with_application(assessment)
        }
    
    def _perform_initial_assessment(self, job_description: str, resume: str) -> AssessmentResult:
        """Perform initial suitability assessment."""
        prompt = PromptTemplates.get_assessment_prompt(job_description, resume)
        
        try:
            response = self.llm_provider.generate_response(prompt)
            return self._parse_assessment_response(response)
        except Exception as e:
            console.print(f"[red]Error in assessment: {e}[/red]", file=sys.stderr)
            raise
    
    def _parse_assessment_response(self, response: str) -> AssessmentResult:
        """Parse the LLM response into structured assessment data."""
        # Extract rating
        rating_match = re.search(r'SUITABILITY RATING[:\s]*(\d+)', response, re.IGNORECASE)
        rating = int(rating_match.group(1)) if rating_match else 5
        
        # Extract strengths
        strengths_match = re.search(r'STRENGTHS[:\s]*(.*?)(?=GAPS|MISSING|$)', response, re.IGNORECASE | re.DOTALL)
        strengths = strengths_match.group(1).strip() if strengths_match else "Not specified"
        
        # Extract gaps
        gaps_match = re.search(r'GAPS[:\s]*(.*?)(?=MISSING|$)', response, re.IGNORECASE | re.DOTALL)
        gaps = gaps_match.group(1).strip() if gaps_match else "Not specified"
        
        # Extract missing requirements
        missing_match = re.search(r'MISSING REQUIREMENTS[:\s]*(.*?)(?=RECOMMENDATION|$)', response, re.IGNORECASE | re.DOTALL)
        missing_requirements = missing_match.group(1).strip() if missing_match else "Not specified"
        
        # Extract recommendation
        rec_match = re.search(r'RECOMMENDATION[:\s]*(Yes|No)', response, re.IGNORECASE)
        recommendation = rec_match.group(1) if rec_match else "Unknown"
        
        # Extract confidence
        conf_match = re.search(r'CONFIDENCE LEVEL[:\s]*(High|Medium|Low)', response, re.IGNORECASE)
        confidence = conf_match.group(1) if conf_match else "Medium"
        
        return AssessmentResult(
            rating=rating,
            strengths=strengths,
            gaps=gaps,
            missing_requirements=missing_requirements,
            recommendation=recommendation,
            confidence=confidence,
            raw_response=response
        )
    
    def _should_proceed_with_application(self, assessment: AssessmentResult) -> bool:
        """Determine if the candidate should proceed with the application."""
        return (
            assessment.rating >= 6 and 
            assessment.recommendation.lower() == 'yes'
        )
    
    def _generate_application_materials(self, job_description: str, resume: str, assessment: str) -> ApplicationMaterials:
        """Generate comprehensive application materials."""
        materials = {}
        
        # Generate resume improvements
        console.print("  - Generating resume improvements...", file=sys.stderr)
        resume_prompt = PromptTemplates.get_resume_improvement_prompt(job_description, resume, assessment)
        materials['resume_improvements'] = self.llm_provider.generate_response(resume_prompt)
        
        # Generate cover letter
        console.print("  - Generating cover letter...", file=sys.stderr)
        cover_letter_prompt = PromptTemplates.get_cover_letter_prompt(job_description, resume, assessment)
        materials['cover_letter'] = self.llm_provider.generate_response(cover_letter_prompt)
        
        # Generate interview questions
        console.print("  - Preparing interview questions...", file=sys.stderr)
        questions_prompt = PromptTemplates.get_interview_questions_prompt(job_description, resume, assessment)
        questions_response = self.llm_provider.generate_response(questions_prompt)
        
        # Parse questions response
        questions_data = self._parse_questions_response(questions_response)
        materials.update(questions_data)
        
        # Generate next steps
        console.print("  - Creating action plan...", file=sys.stderr)
        next_steps_prompt = PromptTemplates.get_next_steps_prompt(job_description, resume, assessment)
        materials['next_steps'] = self.llm_provider.generate_response(next_steps_prompt)
        
        return ApplicationMaterials(**materials)
    
    def _parse_questions_response(self, response: str) -> Dict[str, str]:
        """Parse interview questions response into structured data."""
        # Extract questions for employer
        employer_match = re.search(r'QUESTIONS TO ASK THE HIRING MANAGER[:\s]*(.*?)(?=ANTICIPATED|$)', response, re.IGNORECASE | re.DOTALL)
        questions_for_employer = employer_match.group(1).strip() if employer_match else "Not specified"
        
        # Extract anticipated questions
        anticipated_match = re.search(r'ANTICIPATED INTERVIEW QUESTIONS[:\s]*(.*?)(?=SUGGESTED ANSWERS|$)', response, re.IGNORECASE | re.DOTALL)
        anticipated_questions = anticipated_match.group(1).strip() if anticipated_match else "Not specified"
        
        # Extract suggested answers
        answers_match = re.search(r'SUGGESTED ANSWERS[:\s]*(.*?)$', response, re.IGNORECASE | re.DOTALL)
        suggested_answers = answers_match.group(1).strip() if answers_match else "Not specified"
        
        return {
            'questions_for_employer': questions_for_employer,
            'anticipated_questions': anticipated_questions,
            'suggested_answers': suggested_answers
        }
