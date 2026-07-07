from __future__ import annotations

from abc import ABC, abstractmethod

from teamcode.domain.agent import AgentConfig
from teamcode.domain.context import SessionContext
from teamcode.prompts.loader import load as load_prompt
from teamcode.providers.base import BaseProvider, CompletionRequest, CompletionResponse


class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, provider: BaseProvider) -> None:
        self.config = config
        self.provider = provider

    @abstractmethod
    async def execute(self, context: SessionContext) -> CompletionResponse: ...

    def build_request(self, context: SessionContext) -> CompletionRequest:
        history = [
            {
                "role": "assistant" if m.sender == self.config.name else m.sender,
                "content": m.content,
            }
            for m in context.messages
        ]
        system = self.config.system_prompt or self.default_system_prompt()
        return CompletionRequest(
            model=self.config.model,
            messages=history,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            system_prompt=system,
        )

    def default_system_prompt(self) -> str:
        return load_prompt(self.config.role.value)
