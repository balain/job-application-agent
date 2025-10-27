"""
LangChain-integrated analyzer for enhanced job application assessment.
"""

import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from rich.console import Console

from .llm_provider import LLMProvider
from .langchain_llm_wrapper import LangChainLLMWrapper
from .langchain_structured_parser import StructuredOutputParser, JobAnalysisResult
from .langchain_entity_extractor import LangChainEntityExtractor
from .langchain_rag import ApplicationRAG
from .langgraph_resume_tailor import LangGraphResumeTailor
from .langchain_observability import get_callbacks, log_operation
from .langchain_cache import initialize_langchain_cache
from .models import AnalysisResult, JobAssessment

console = Console(file=sys.stderr)
logger = logging.getLogger(__name__)


class LangChainJobApplicationAnalyzer:
    """
    Enhanced analyzer using LangChain for improved reliability and capabilities.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        
        # Initialize LangChain components
        self.llm_wrapper = LangChainLLMWrapper(llm_provider)
        self.structured_parser = StructuredOutputParser(self.llm_wrapper)
        self.entity_extractor = LangChainEntityExtractor(self.llm_wrapper)
        self.resume_tailor = LangGraphResumeTailor(self.llm_wrapper)
        
        # Initialize RAG (optional)
        self.rag = None
        try:
            self.rag = ApplicationRAG()
        except Exception as e:
            logger.warning(f"RAG initialization failed: {e}")
        
        # Initialize caching
        try:
            initialize_langchain_cache()
        except Exception as e:
            logger.warning(f"Cache initialization failed: {e}")
        
        logger.info("LangChain analyzer initialized successfully")

    def analyze_application(
        self,
        job_description: str,
        resume: str,
        enable_rag: bool = True,
        enable_tailoring: bool = False
    ) -> AnalysisResult:
        """
        Perform comprehensive analysis using LangChain.

        Args:
            job_description: The job description text
            resume: The resume text
            enable_rag: Whether to use RAG for similar applications
            enable_tailoring: Whether to perform resume tailoring

        Returns:
            AnalysisResult containing all analysis results
        """
        console.print("[bold blue]Starting LangChain-enhanced analysis...[/bold blue]")
        
        try:
            log_operation("analyze_application", {
                "job_desc_length": len(job_description),
                "resume_length": len(resume),
                "enable_rag": enable_rag,
                "enable_tailoring": enable_tailoring
            })

            # Step 1: Structured job analysis
            console.print("[yellow]Step 1: Performing structured job analysis...[/yellow]")
            job_analysis = self._perform_structured_analysis(job_description, resume)

            # Step 2: Entity extraction
            console.print("[yellow]Step 2: Extracting entities...[/yellow]")
            entities = self._extract_entities(job_description, resume)

            # Step 3: RAG-based insights (if enabled)
            rag_insights = None
            if enable_rag and self.rag:
                console.print("[yellow]Step 3: Retrieving similar applications...[/yellow]")
                rag_insights = self._get_rag_insights(job_description, entities)

            # Step 4: Resume tailoring (if enabled)
            tailoring_result = None
            if enable_tailoring:
                console.print("[yellow]Step 4: Performing resume tailoring...[/yellow]")
                tailoring_result = self._perform_resume_tailoring(job_description, resume)

            # Step 5: Generate comprehensive results
            console.print("[yellow]Step 5: Generating final results...[/yellow]")
            result = self._generate_comprehensive_result(
                job_analysis,
                entities,
                rag_insights,
                tailoring_result
            )

            log_operation("analyze_application", {"success": True, "result_type": type(result).__name__})
            console.print("[green]✓ LangChain analysis complete[/green]")

            return result

        except Exception as e:
            logger.error(f"Error in LangChain analysis: {e}")
            log_operation("analyze_application", {"success": False, "error": str(e)})
            raise

    def _perform_structured_analysis(
        self,
        job_description: str,
        resume: str
    ) -> JobAnalysisResult:
        """Perform structured job analysis using LangChain."""
        try:
            # Get callbacks for observability
            callbacks = get_callbacks()
            
            # Perform analysis with callbacks
            result = self.structured_parser.parse_job_analysis(
                job_description=job_description,
                resume_content=resume
            )
            
            console.print(f"[green]✓ Structured analysis complete - Score: {result.suitability_score}/10[/green]")
            return result
            
        except Exception as e:
            logger.error(f"Error in structured analysis: {e}")
            # Return default result
            return JobAnalysisResult(
                suitability_score=5.0,
                match_percentage=50.0,
                overall_assessment=f"Analysis error: {str(e)}"
            )

    def _extract_entities(self, job_description: str, resume: str) -> Dict[str, Any]:
        """Extract entities from job description and resume."""
        try:
            entities = self.entity_extractor.extract_all_entities(job_description, resume)
            
            if entities.get("extraction_success"):
                console.print("[green]✓ Entity extraction complete[/green]")
            else:
                console.print("[yellow]⚠ Entity extraction had issues[/yellow]")
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return {
                "job": {},
                "resume": {},
                "extraction_success": False,
                "error": str(e)
            }

    def _get_rag_insights(
        self,
        job_description: str,
        entities: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get insights from similar applications using RAG."""
        if not self.rag:
            return None
        
        try:
            # Create search query from job description and entities
            job_entities = entities.get("job", {})
            search_query = f"{job_description} {job_entities.get('company', '')} {job_entities.get('job_title', '')}"
            
            # Find similar applications
            similar_apps = self.rag.find_similar_applications(search_query, k=5)
            
            if similar_apps:
                console.print(f"[green]✓ Found {len(similar_apps)} similar applications[/green]")
                
                # Analyze patterns
                companies = [app["metadata"].get("company", "Unknown") for app in similar_apps]
                industries = [app["metadata"].get("industry", "Unknown") for app in similar_apps]
                
                return {
                    "similar_applications": similar_apps,
                    "common_companies": list(set(companies)),
                    "common_industries": list(set(industries)),
                    "insights_count": len(similar_apps)
                }
            else:
                console.print("[yellow]⚠ No similar applications found[/yellow]")
                return None
                
        except Exception as e:
            logger.error(f"Error in RAG insights: {e}")
            return None

    def _perform_resume_tailoring(
        self,
        job_description: str,
        resume: str
    ) -> Optional[Dict[str, Any]]:
        """Perform resume tailoring using LangGraph workflow."""
        try:
            result = self.resume_tailor.tailor_resume(
                resume=resume,
                job_desc=job_description,
                max_iterations=3
            )
            
            if "error" not in result:
                console.print(f"[green]✓ Resume tailoring complete - {result['iterations']} iterations[/green]")
            else:
                console.print("[yellow]⚠ Resume tailoring had issues[/yellow]")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in resume tailoring: {e}")
            return None

    def _generate_comprehensive_result(
        self,
        job_analysis: JobAnalysisResult,
        entities: Dict[str, Any],
        rag_insights: Optional[Dict[str, Any]],
        tailoring_result: Optional[Dict[str, Any]]
    ) -> AnalysisResult:
        """Generate comprehensive analysis result."""
        try:
            # Convert LangChain result to legacy format
            assessment = JobAssessment(
                suitability_score=job_analysis.suitability_score,
                match_percentage=job_analysis.match_percentage,
                strengths=job_analysis.strengths,
                weaknesses=job_analysis.weaknesses,
                missing_skills=job_analysis.missing_skills,
                recommendations=job_analysis.recommendations,
                overall_assessment=job_analysis.overall_assessment
            )

            # Create comprehensive result
            result = AnalysisResult(
                job_assessment=assessment,
                resume_improvements=job_analysis.recommendations,
                cover_letter_suggestions=job_analysis.recommendations,
                interview_questions=[],
                action_plan=job_analysis.recommendations,
                entities=entities,
                rag_insights=rag_insights,
                tailoring_result=tailoring_result,
                langchain_enhanced=True
            )

            return result

        except Exception as e:
            logger.error(f"Error generating comprehensive result: {e}")
            # Return basic result
            assessment = JobAssessment(
                suitability_score=job_analysis.suitability_score,
                match_percentage=job_analysis.match_percentage,
                overall_assessment=job_analysis.overall_assessment
            )
            
            return AnalysisResult(
                job_assessment=assessment,
                langchain_enhanced=True
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get analysis metrics."""
        from .langchain_observability import get_metrics
        return get_metrics()

    def export_metrics(self, file_path: Optional[str] = None) -> str:
        """Export analysis metrics."""
        from .langchain_observability import export_metrics
        return export_metrics(file_path)
