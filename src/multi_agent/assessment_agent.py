from typing import Dict, Any

from .base_agent import BaseAgent
from .shared_state import update_state
from ..llm_provider import LLMProvider
from ..prompts import PromptTemplates
from ..structured_parser import StructuredParser


class AssessmentAgent(BaseAgent):
    name = "assessment"

    def __init__(self, llm_provider: LLMProvider):
        self.parser = StructuredParser(llm_provider)
        self.llm_provider = llm_provider

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = PromptTemplates.get_assessment_prompt(
            state["job_description"], state["resume"]
        )
        response = self.llm_provider.generate_response(prompt)
        assessment = self.parser.parse_assessment_response(response)
        return update_state(state, {"assessment": assessment.model_dump()})


