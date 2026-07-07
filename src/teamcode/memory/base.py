from __future__ import annotations

from abc import ABC, abstractmethod

from teamcode.domain.message import Message


class BaseMemory(ABC):
    @abstractmethod
    async def add(self, message: Message) -> None: ...

    @abstractmethod
    async def get_context(self, session_id: str) -> list[Message]: ...

    @abstractmethod
    async def clear(self, session_id: str) -> None: ...
