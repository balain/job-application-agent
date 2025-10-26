"""Core analysis engine for job application assessment."""

import sys
import logging
from typing import Dict, Any

from rich.console import Console

from .llm_provider import LLMProvider
from .prompts import PromptTemplates
from .structured_parser import StructuredParser
from .error_handler import ErrorHandler
from .models import (
    AnalysisResult,
    JobAssessment,
)

console = Console(file=sys.stderr)
logger = logging.getLogger(__name__)


class JobApplicationAnalyzer:
    """Main analyzer for job application assessment."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.parser = StructuredParser(llm_provider)
        self.error_handler = ErrorHandler()

    def analyze_application(self, job_description: str, resume: str) -> AnalysisResult:
        """
        Perform comprehensive analysis of job application.

        Args:
            job_description: The job description text
            resume: The resume text

        Returns:
            AnalysisResult containing all analysis results
        """
        console.print("[bold blue]Starting job application analysis...[/bold blue]")

        try:
            # Step 1: Initial assessment
            console.print("[yellow]Step 1: Assessing job suitability...[/yellow]")
            assessment = self._perform_initial_assessment(job_description, resume)

            # Step 2: Generate additional materials if recommended
            materials = None
            if self._should_proceed_with_application(assessment):
                console.print(
                    "[yellow]Step 2: Generating application materials...[/yellow]"
                )
                materials = self._generate_application_materials(
                    job_description, resume, assessment
                )

            return AnalysisResult(
                assessment=assessment,
                resume_improvements=materials.get("resume_improvements")
                if materials
                else None,
                cover_letter=materials.get("cover_letter") if materials else None,
                interview_questions=materials.get("interview_questions")
                if materials
                else None,
                next_steps=materials.get("next_steps") if materials else None,
                should_proceed=self._should_proceed_with_application(assessment),
                error_info=None,
            )

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            error_info = self.error_handler.handle_llm_error(
                e, "Job application analysis"
            )
            console.print(f"[red]Analysis failed: {error_info.user_message}[/red]")

            return AnalysisResult(
                assessment=None,
                resume_improvements=None,
                cover_letter=None,
                interview_questions=None,
                next_steps=None,
                should_proceed=False,
                error_info=error_info,
            )

    def _perform_initial_assessment(
        self, job_description: str, resume: str
    ) -> JobAssessment:
        """Perform initial suitability assessment."""
        prompt = PromptTemplates.get_assessment_prompt(job_description, resume)

        try:
            response = self.llm_provider.generate_response(prompt)
            return self.parser.parse_assessment_response(response)
        except Exception as e:
            logger.error(f"Assessment failed: {e}")
            error_info = self.error_handler.handle_llm_error(e, "Initial assessment")
            console.print(f"[red]Assessment failed: {error_info.user_message}[/red]")
            raise

    def _should_proceed_with_application(self, assessment: JobAssessment) -> bool:
        """Determine if the candidate should proceed with the application."""
        return assessment.rating >= 6 and assessment.recommendation.lower() == "yes"

    def _generate_application_materials(
        self, job_description: str, resume: str, assessment: JobAssessment
    ) -> Dict[str, Any]:
        """Generate comprehensive application materials."""
        materials = {}

        try:
            # Generate resume improvements
            console.print("  - Generating resume improvements...")
            resume_prompt = PromptTemplates.get_resume_improvement_prompt(
                job_description, resume, assessment.model_dump_json()
            )
            resume_response = self.llm_provider.generate_response(resume_prompt)
            materials["resume_improvements"] = self.parser.parse_resume_improvements(
                resume_response
            )

            # Generate cover letter
            console.print("  - Generating cover letter...")
            cover_letter_prompt = PromptTemplates.get_cover_letter_prompt(
                job_description, resume, assessment.model_dump_json()
            )
            cover_letter_response = self.llm_provider.generate_response(
                cover_letter_prompt
            )
            materials["cover_letter"] = self.parser.parse_cover_letter(
                cover_letter_response
            )

            # Generate interview questions
            console.print("  - Preparing interview questions...")
            questions_prompt = PromptTemplates.get_interview_questions_prompt(
                job_description, resume, assessment.model_dump_json()
            )
            questions_response = self.llm_provider.generate_response(questions_prompt)
            materials["interview_questions"] = self.parser.parse_interview_questions(
                questions_response
            )

            # Generate next steps
            console.print("  - Creating action plan...")
            next_steps_prompt = PromptTemplates.get_next_steps_prompt(
                job_description, resume, assessment.model_dump_json()
            )
            next_steps_response = self.llm_provider.generate_response(next_steps_prompt)
            materials["next_steps"] = self.parser.parse_next_steps(next_steps_response)

        except Exception as e:
            logger.error(f"Material generation failed: {e}")
            error_info = self.error_handler.handle_llm_error(
                e, "Application materials generation"
            )
            console.print(
                f"[red]Material generation failed: {error_info.user_message}[/red]"
            )
            raise

        return materials
