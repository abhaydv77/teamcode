from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class BaseCommand(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, app: TeamCodeApp, args: list[str]) -> None: ...
