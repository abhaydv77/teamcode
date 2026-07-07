from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTelemetry(ABC):
    @abstractmethod
    async def capture(self, event: str, data: dict[str, Any] | None = None) -> None: ...
