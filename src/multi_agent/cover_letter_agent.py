from typing import Dict, Any

from .base_agent import BaseAgent
from .shared_state import update_state
from ..llm_provider import LLMProvider
from ..prompts import PromptTemplates
from ..structured_parser import StructuredParser


class CoverLetterAgent(BaseAgent):
    name = "cover_letter"

    def __init__(self, llm_provider: LLMProvider):
        self.parser = StructuredParser(llm_provider)
        self.llm_provider = llm_provider

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        assessment_text = ""
        if state.get("assessment"):
            a = state["assessment"]
            assessment_text = f"Rating: {a.get('rating')}, Strengths: {a.get('strengths')}, Gaps: {a.get('gaps')}"

        prompt = PromptTemplates.get_cover_letter_prompt(
            state["job_description"], state["resume"], assessment_text
        )
        response = self.llm_provider.generate_response(prompt)
        cover_letter = self.parser.parse_cover_letter_response(response)
        return update_state(state, {"cover_letter": cover_letter.model_dump()})


