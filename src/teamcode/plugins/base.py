from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class BasePlugin(ABC):
    name: str

    @abstractmethod
    async def initialize(self, app: TeamCodeApp) -> None: ...

    @abstractmethod
    async def shutdown(self) -> None: ...
