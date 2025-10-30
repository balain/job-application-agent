from typing import Dict, Any

from .base_agent import BaseAgent
from .shared_state import update_state
from ..career_progression_tracker import CareerProgressionTracker
from ..industry_trend_analyzer import IndustryTrendAnalyzer


class CareerAdvisorAgent(BaseAgent):
    name = "career_advisor"

    def __init__(self) -> None:
        self.progression = CareerProgressionTracker()
        self.trends = IndustryTrendAnalyzer()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        profile = {
            "resume_content": state.get("resume", ""),
            "skills": [],
            "current_title": "",
        }
        advice = {
            "progression": self.progression.analyze_progression(profile),
            "industry": [i.model_dump() for i in self.trends.analyze_industry_trends(profile)],
        }
        return update_state(state, {"career_advice": advice})


