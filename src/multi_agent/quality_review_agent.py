from typing import Dict, Any

from .base_agent import BaseAgent
from .shared_state import update_state


class QualityReviewAgent(BaseAgent):
    name = "quality_review"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        warnings = []
        a = state.get("assessment") or {}
        cl = state.get("cover_letter") or {}
        if a and cl and str(a.get("strengths", "")).strip() and str(cl.get("full_letter", "")).strip():
            strengths = a.get("strengths", "").lower()
            if strengths and strengths not in cl.get("full_letter", "").lower():
                warnings.append("Cover letter may not reflect assessed strengths.")

        return update_state(state, {"quality": {"warnings": warnings}})


