"""
LangGraph workflows for resume optimization and iterative improvement.
"""

import logging
from typing import TypedDict, List, Literal, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.base import BaseLanguageModel

from .langchain_llm_wrapper import LangChainLLMWrapper
from .langchain_structured_parser import ResumeImprovementResult

logger = logging.getLogger(__name__)


class ResumeTailorState(TypedDict):
    """State for resume tailoring workflow."""
    original_resume: str
    job_description: str
    tailored_resume: str
    ats_score: float
    keyword_score: float
    iterations: int
    max_iterations: int
    improvements: List[str]
    current_analysis: Optional[ResumeImprovementResult]
    final_recommendations: List[str]


class LangGraphResumeTailor:
    """
    LangGraph workflow for iterative resume optimization.
    """
    
    def __init__(self, llm_wrapper: LangChainLLMWrapper):
        self.llm_wrapper = llm_wrapper
        self.llm = llm_wrapper.langchain_llm
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the resume tailoring workflow."""
        workflow = StateGraph(ResumeTailorState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("tailor", self._tailor_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Set entry point
        workflow.set_entry_point("analyze")
        
        # Add edges
        workflow.add_edge("analyze", "tailor")
        workflow.add_edge("tailor", "validate")
        
        # Conditional edge: continue improving or finish
        workflow.add_conditional_edges(
            "validate",
            self._should_continue,
            {
                "continue": "analyze",
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _analyze_node(self, state: ResumeTailorState) -> ResumeTailorState:
        """Analyze current resume against job description."""
        try:
            from .langchain_structured_parser import StructuredOutputParser
            
            parser = StructuredOutputParser(self.llm_wrapper)
            
            # Get current resume (original or previously tailored)
            current_resume = state.get("tailored_resume", state["original_resume"])
            
            # Analyze resume improvements
            analysis = parser.parse_resume_improvement(
                resume_content=current_resume,
                job_description=state["job_description"]
            )
            
            state["current_analysis"] = analysis
            state["ats_score"] = analysis.ats_score
            state["keyword_score"] = analysis.keyword_match
            
            logger.info(f"Analysis complete - ATS: {analysis.ats_score}, Keywords: {analysis.keyword_match}")
            
        except Exception as e:
            logger.error(f"Error in analyze node: {e}")
            state["ats_score"] = 50.0
            state["keyword_score"] = 50.0
        
        return state
    
    def _tailor_node(self, state: ResumeTailorState) -> ResumeTailorState:
        """Tailor resume based on analysis."""
        try:
            current_resume = state.get("tailored_resume", state["original_resume"])
            analysis = state.get("current_analysis")
            
            # Create tailored prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert resume writer. Improve this resume to better match the job description.
                Focus on:
                1. Adding missing keywords naturally
                2. Improving ATS compatibility
                3. Enhancing content relevance
                4. Maintaining authenticity
                
                Provide only the improved resume text, no explanations."""),
                ("user", """Job Description:
{job_description}

Current Resume:
{resume}

Previous Analysis:
- ATS Score: {ats_score}
- Keyword Match: {keyword_score}
- Missing Keywords: {missing_keywords}
- Content Improvements: {content_improvements}

Improve the resume to better match the job requirements.""")
            ])
            
            chain = prompt | self.llm
            
            # Prepare missing keywords and improvements
            missing_keywords = []
            content_improvements = []
            
            if analysis:
                missing_keywords = analysis.missing_keywords
                content_improvements = analysis.content_improvements
            
            result = chain.invoke({
                "job_description": state["job_description"],
                "resume": current_resume,
                "ats_score": state["ats_score"],
                "keyword_score": state["keyword_score"],
                "missing_keywords": ", ".join(missing_keywords),
                "content_improvements": ", ".join(content_improvements)
            })
            
            # Extract content from response
            if hasattr(result, 'content'):
                tailored_resume = result.content
            else:
                tailored_resume = str(result)
            
            state["tailored_resume"] = tailored_resume
            state["iterations"] = state.get("iterations", 0) + 1
            
            logger.info(f"Tailoring complete - Iteration {state['iterations']}")
            
        except Exception as e:
            logger.error(f"Error in tailor node: {e}")
            # Keep current resume if tailoring fails
            state["tailored_resume"] = state.get("tailored_resume", state["original_resume"])
            state["iterations"] = state.get("iterations", 0) + 1
        
        return state
    
    def _validate_node(self, state: ResumeTailorState) -> ResumeTailorState:
        """Validate tailored resume quality."""
        try:
            # Re-analyze the tailored resume
            from .langchain_structured_parser import StructuredOutputParser
            
            parser = StructuredOutputParser(self.llm_wrapper)
            
            analysis = parser.parse_resume_improvement(
                resume_content=state["tailored_resume"],
                job_description=state["job_description"]
            )
            
            state["ats_score"] = analysis.ats_score
            state["keyword_score"] = analysis.keyword_match
            
            # Add improvements to list
            improvements = state.get("improvements", [])
            if analysis.content_improvements:
                improvements.extend(analysis.content_improvements)
            state["improvements"] = improvements
            
            logger.info(f"Validation complete - ATS: {analysis.ats_score}, Keywords: {analysis.keyword_match}")
            
        except Exception as e:
            logger.error(f"Error in validate node: {e}")
        
        return state
    
    def _finalize_node(self, state: ResumeTailorState) -> ResumeTailorState:
        """Finalize the resume tailoring process."""
        try:
            # Generate final recommendations
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert resume consultant. Provide final recommendations for the tailored resume.
                Focus on:
                1. Key improvements made
                2. Remaining areas for improvement
                3. Next steps for the candidate
                4. Overall assessment"""),
                ("user", """Job Description:
{job_description}

Final Tailored Resume:
{tailored_resume}

Final Scores:
- ATS Score: {ats_score}
- Keyword Match: {keyword_score}

Provide final recommendations.""")
            ])
            
            chain = prompt | self.llm
            
            result = chain.invoke({
                "job_description": state["job_description"],
                "tailored_resume": state["tailored_resume"],
                "ats_score": state["ats_score"],
                "keyword_score": state["keyword_score"]
            })
            
            # Extract content from response
            if hasattr(result, 'content'):
                final_recommendations = result.content
            else:
                final_recommendations = str(result)
            
            state["final_recommendations"] = [final_recommendations]
            
            logger.info("Finalization complete")
            
        except Exception as e:
            logger.error(f"Error in finalize node: {e}")
            state["final_recommendations"] = ["Final recommendations could not be generated"]
        
        return state
    
    def _should_continue(self, state: ResumeTailorState) -> Literal["continue", "finalize"]:
        """Decide whether to continue improving or finish."""
        iterations = state.get("iterations", 0)
        max_iterations = state.get("max_iterations", 3)
        ats_score = state.get("ats_score", 0)
        keyword_score = state.get("keyword_score", 0)
        
        # Stop if max iterations reached
        if iterations >= max_iterations:
            logger.info(f"Reached max iterations ({max_iterations})")
            return "finalize"
        
        # Stop if scores are good enough
        if ats_score >= 80 and keyword_score >= 70:
            logger.info(f"Good scores achieved - ATS: {ats_score}, Keywords: {keyword_score}")
            return "finalize"
        
        # Continue improving
        logger.info(f"Continuing improvement - ATS: {ats_score}, Keywords: {keyword_score}")
        return "continue"
    
    def tailor_resume(
        self,
        resume: str,
        job_desc: str,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Run the resume tailoring workflow.
        
        Args:
            resume: Original resume content
            job_desc: Job description
            max_iterations: Maximum number of improvement iterations
            
        Returns:
            Final workflow state with tailored resume and recommendations
        """
        initial_state = {
            "original_resume": resume,
            "job_description": job_desc,
            "tailored_resume": resume,
            "ats_score": 0.0,
            "keyword_score": 0.0,
            "iterations": 0,
            "max_iterations": max_iterations,
            "improvements": [],
            "current_analysis": None,
            "final_recommendations": []
        }
        
        try:
            final_state = self.workflow.invoke(initial_state)
            logger.info(f"Resume tailoring complete after {final_state['iterations']} iterations")
            return final_state
        except Exception as e:
            logger.error(f"Error in resume tailoring workflow: {e}")
            return {
                **initial_state,
                "error": str(e),
                "tailored_resume": resume  # Return original if workflow fails
            }
