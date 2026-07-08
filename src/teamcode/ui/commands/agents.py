from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

from teamcode.domain.agent import Role
from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class AgentsCommand(BaseCommand):
    name = "agents"
    description = "List available agent roles and their current assignment"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        table = Table(title="Available Agent Roles", border_style="blue")
        table.add_column("Role", style="cyan", width=20)
        table.add_column("Status", width=12)
        table.add_column("Provider", width=14)
        table.add_column("Model", width=20)

        for role in Role:
            assigned = app.agent_assignments.get(role, None)
            if assigned:
                table.add_row(
                    role.value,
                    "[green]assigned[/]",
                    assigned.get("provider", "—"),
                    assigned.get("model", "—"),
                )
            else:
                table.add_row(role.value, "[dim]unassigned[/]", "—", "—")

        app.post_message(app.CommandResult(table))
