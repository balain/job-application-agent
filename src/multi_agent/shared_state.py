from typing import TypedDict, Dict, Any, Optional


class SharedState(TypedDict, total=False):
    job_description: str
    resume: str
    assessment: Dict[str, Any]
    resume_improvements: Dict[str, Any]
    cover_letter: Dict[str, Any]
    interview_questions: Dict[str, Any]
    next_steps: Dict[str, Any]
    history: Dict[str, Any]
    career_advice: Dict[str, Any]
    learning_plan: Dict[str, Any]
    errors: Dict[str, str]
    flags: Dict[str, bool]
    metadata: Dict[str, Any]


def update_state(state: SharedState, updates: Dict[str, Any]) -> SharedState:
    new_state = dict(state)
    new_state.update(updates)
    return new_state  # shallow merge; agents own their keys


