from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CompletionRequest:
    model: str
    messages: list[dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str | None = None


@dataclass
class CompletionResponse:
    content: str
    model: str
    usage: dict | None = None


class BaseProvider(ABC):
    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def supported_models(self) -> list[str]: ...
