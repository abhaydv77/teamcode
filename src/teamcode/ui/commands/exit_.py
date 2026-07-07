from __future__ import annotations

from typing import TYPE_CHECKING

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class ExitCommand(BaseCommand):
    name = "exit"
    description = "Exit the application"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        await app.action_quit()
