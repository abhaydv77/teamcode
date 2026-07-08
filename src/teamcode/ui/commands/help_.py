from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

from teamcode.ui.commands.base import BaseCommand
from teamcode.ui.commands.registry import CommandRegistry

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class HelpCommand(BaseCommand):
    name = "help"
    description = "Show available commands and usage information"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        table = Table(title="TeamCode Commands", border_style="blue")
        table.add_column("Command", style="cyan", width=20)
        table.add_column("Description", style="white")

        for name, cmd_cls in sorted(CommandRegistry.all().items()):
            table.add_row(f"/{name}", cmd_cls.description)

        app.post_message(app.CommandResult(table))
