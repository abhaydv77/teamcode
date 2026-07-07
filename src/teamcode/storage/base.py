from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseStorage(ABC):
    @abstractmethod
    async def save(self, collection: str, key: str, data: dict[str, Any]) -> None: ...

    @abstractmethod
    async def load(self, collection: str, key: str) -> dict[str, Any] | None: ...

    @abstractmethod
    async def delete(self, collection: str, key: str) -> None: ...

    @abstractmethod
    async def list(self, collection: str) -> list[dict[str, Any]]: ...
