from __future__ import annotations

from teamcode.agents.base import BaseAgent
from teamcode.domain.agent import AgentConfig
from teamcode.providers.base import BaseProvider


class AgentRegistry:
    _agents: dict[str, type[BaseAgent]] = {}

    @classmethod
    def register(cls, role: str, agent_cls: type[BaseAgent]) -> None:
        cls._agents[role] = agent_cls

    @classmethod
    def get(cls, role: str) -> type[BaseAgent]:
        if role not in cls._agents:
            msg = f"Unknown agent role: '{role}'. Available: {list(cls._agents)}"
            raise KeyError(msg)
        return cls._agents[role]

    @classmethod
    def create(cls, role: str, config: AgentConfig, provider: BaseProvider) -> BaseAgent:
        agent_cls = cls.get(role)
        return agent_cls(config=config, provider=provider)

    @classmethod
    def all_roles(cls) -> list[str]:
        return list(cls._agents)

    @classmethod
    def clear(cls) -> None:
        cls._agents.clear()
