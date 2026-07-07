from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class UsageCommand(BaseCommand):
    name = "usage"
    description = "Display token usage and cost estimates"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        usage = app.usage_stats

        table = Table(title="Usage Statistics", border_style="blue")
        table.add_column("Metric", style="cyan", width=24)
        table.add_column("Value", style="white")

        total_tokens = usage.get("total_tokens", 0)
        total_cost = usage.get("total_cost", 0.0)
        api_calls = usage.get("api_calls", 0)

        table.add_row("Total API calls", str(api_calls))
        table.add_row("Total tokens", str(total_tokens))
        table.add_row("Estimated cost", f"${total_cost:.4f}")
        table.add_row("Session tokens", str(usage.get("session_tokens", 0)))

        await app.post_message(app.CommandResult(table))
