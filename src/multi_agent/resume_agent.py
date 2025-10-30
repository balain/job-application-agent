from typing import Dict, Any

from .base_agent import BaseAgent
from .shared_state import update_state
from ..langchain_llm_wrapper import LangChainLLMWrapper
from ..langchain_structured_parser import StructuredOutputParser


class ResumeOptimizationAgent(BaseAgent):
    name = "resume_optimization"

    def __init__(self, llm_wrapper: LangChainLLMWrapper):
        self.parser = StructuredOutputParser(llm_wrapper)

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        analysis = self.parser.parse_resume_improvement(
            resume_content=state["resume"], job_description=state["job_description"]
        )
        return update_state(
            state,
            {
                "resume_improvements": analysis.model_dump(),
            },
        )


