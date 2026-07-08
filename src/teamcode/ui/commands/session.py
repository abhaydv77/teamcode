from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class SessionCommand(BaseCommand):
    name = "session"
    description = "Manage or inspect the current session"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        if not args:
            state = app.session_state
            table = Table(title="Current Session", border_style="blue")
            table.add_column("Property", style="cyan", width=20)
            table.add_column("Value", style="white")
            table.add_row("Session ID", state.get("session_id", "—"))
            table.add_row("Status", state.get("status", "[dim]idle[/]"))
            table.add_row("Task count", str(state.get("task_count", 0)))
            app.post_message(app.CommandResult(table))
            return

        sub = args[0]
        if sub == "start":
            app.session_state["status"] = "active"
            app.post_message(app.CommandResult("[green]Session started.[/]"))
        elif sub == "stop":
            app.session_state["status"] = "idle"
            app.post_message(app.CommandResult("[yellow]Session stopped.[/]"))
        else:
            app.post_message(app.CommandResult(f"[red]Unknown subcommand: {sub}[/]"))
