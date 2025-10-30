from __future__ import annotations

from typing import Dict, Any, Protocol


class AgentProtocol(Protocol):
    name: str

    def prepare(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def postprocess(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ...


class BaseAgent:
    name: str = "agent"
    capabilities: Dict[str, Any] = {}

    def prepare(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state

    def postprocess(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state = dict(state)
        state = self.prepare(state)
        state = self.execute(state)
        state = self.postprocess(state)
        return state


