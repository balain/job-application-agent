from typing import Dict, Any

from .base_agent import BaseAgent
from .shared_state import update_state
from ..database_manager import db_manager
from ..database_schema import ApplicationStatus


class HistoryAgent(BaseAgent):
    name = "history"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            email = state.get("user_email", "anonymous@example.com")
            name = state.get("user_name", "Anonymous")
            job_desc = state["job_description"]
            lines = job_desc.split("\n")
            job_title = lines[0].strip() if lines else "Unknown Position"
            company_name = "Unknown Company"

            status = (
                ApplicationStatus.APPLIED
                if (state.get("assessment", {}).get("rating", 0) >= 7)
                else ApplicationStatus.DRAFT
            )

            app = db_manager.create_application(
                person_email=email,
                person_name=name,
                company_name=company_name,
                job_title=job_title,
                status=status,
                notes="Created via multi-agent workflow",
            )

            return update_state(state, {"history": {"application_id": app.id, "status": status.value}})
        except Exception:
            # Non-fatal
            return update_state(state, {"history": {"error": "failed_to_update"}})


