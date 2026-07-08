from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class HistoryCommand(BaseCommand):
    name = "history"
    description = "Show recent command and message history"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        limit = 20
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                pass

        history = app.message_history[-limit:]

        table = Table(
            title=f"History (last {len(history)} entries)",
            border_style="blue",
        )
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Content", style="white", max_width=60)
        table.add_column("Timestamp", style="dim", width=20)

        for entry in reversed(history):
            table.add_row(
                entry.get("type", "?"),
                entry.get("content", "")[:60],
                entry.get("timestamp", ""),
            )

        app.post_message(app.CommandResult(table))
