from typing import Dict, Any

from .shared_state import SharedState, update_state
from .assessment_agent import AssessmentAgent
from .resume_agent import ResumeOptimizationAgent
from .cover_letter_agent import CoverLetterAgent
from .interview_agent import InterviewPrepAgent
from .history_agent import HistoryAgent
from .career_advisor_agent import CareerAdvisorAgent
from .learning_agent import LearningAgent
from .quality_review_agent import QualityReviewAgent
from ..langchain_llm_wrapper import LangChainLLMWrapper
from ..llm_provider import LLMProvider
from config import Config


class OrchestratorAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.llm_wrapper = LangChainLLMWrapper(llm_provider)

        self.assessment = AssessmentAgent(llm_provider)
        self.resume_opt = ResumeOptimizationAgent(self.llm_wrapper)
        self.cover_letter = CoverLetterAgent(llm_provider)
        self.interview = InterviewPrepAgent(llm_provider)
        self.history = HistoryAgent()
        self.career = CareerAdvisorAgent()
        self.learning = LearningAgent()
        self.quality = QualityReviewAgent()

    def run(self, initial_state: SharedState) -> SharedState:
        state: Dict[str, Any] = dict(initial_state)

        # Assessment (gate)
        state = self.assessment.run(state)

        # Parallelizable section (run serially here for simplicity)
        state = self.resume_opt.run(state)
        state = self.cover_letter.run(state)
        state = self.interview.run(state)

        # History logging
        state = self.history.run(state)

        # Optional branches
        if Config.ENABLE_CAREER_ADVISOR:
            state = self.career.run(state)
        if Config.ENABLE_LEARNING_PLAN:
            state = self.learning.run(state)

        # Quality review
        state = self.quality.run(state)

        return state  # SharedState


