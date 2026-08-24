from __future__ import annotations

from typing import Any


class LangGraphRentalAgent:
    def __init__(self, model_name: str = "gpt-4o-mini") -> None:
        self.model_name = model_name

    def run(self, message: str, context: list[str] | None = None) -> dict[str, Any]:
        context_text = "\n".join(context or [])
        return {
            "message": message,
            "model": self.model_name,
            "context": context_text,
            "status": "ready",
            "workflow": "langgraph-rental-agent",
        }
