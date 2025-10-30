from typing import Dict, Any

from .base_agent import BaseAgent
from .shared_state import update_state
from ..llm_provider import LLMProvider
from ..prompts import PromptTemplates
from ..structured_parser import StructuredParser


class InterviewPrepAgent(BaseAgent):
    name = "interview_prep"

    def __init__(self, llm_provider: LLMProvider):
        self.parser = StructuredParser(llm_provider)
        self.llm_provider = llm_provider

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = PromptTemplates.get_interview_prep_prompt(
            state["job_description"], state["resume"]
        )
        response = self.llm_provider.generate_response(prompt)
        interview = self.parser.parse_interview_questions_response(response)
        return update_state(state, {"interview_questions": interview.model_dump()})


