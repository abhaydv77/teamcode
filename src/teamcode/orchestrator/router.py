from __future__ import annotations

from teamcode.domain.context import SessionContext


class AgentRouter:
    def next_agent(self, context: SessionContext) -> str | None:
        return None
