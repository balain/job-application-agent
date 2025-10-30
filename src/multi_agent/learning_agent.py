from typing import Dict, Any

from .base_agent import BaseAgent
from .shared_state import update_state
from ..personalized_recommendation_engine import PersonalizedRecommendationEngine


class LearningAgent(BaseAgent):
    name = "learning"

    def __init__(self) -> None:
        self.engine = PersonalizedRecommendationEngine()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        profile = {
            "user_id": state.get("user_email", "anonymous"),
            "email": state.get("user_email", "anonymous@example.com"),
            "resume_content": state.get("resume", ""),
            "skills": [],
            "current_title": "",  # could extract
            "location": "",
        }
        plan = self.engine.create_learning_plan(profile)
        return update_state(state, {"learning_plan": plan.model_dump() if hasattr(plan, "model_dump") else plan})


