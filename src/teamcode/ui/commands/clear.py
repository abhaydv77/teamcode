from __future__ import annotations

from typing import TYPE_CHECKING

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class ClearCommand(BaseCommand):
    name = "clear"
    description = "Clear the chat area"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        await app.post_message(app.ClearChat())
