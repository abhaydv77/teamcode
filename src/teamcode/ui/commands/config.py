from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class ConfigCommand(BaseCommand):
    name = "config"
    description = "View or edit the current configuration"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        if args:
            app.post_message(
                app.CommandResult(f"[yellow]Setting config: {' '.join(args)}[/]")
            )
            return

        table = Table(title="Configuration", border_style="blue")
        table.add_column("Key", style="cyan", width=30)
        table.add_column("Value", style="white")

        settings = app.settings
        for provider, key in settings.available_providers.items():
            masked = f"{key[:8]}..." if key else "[dim]not set[/]"
            table.add_row(f"api_key.{provider}", masked)

        table.add_row("log_level", settings.log_level)
        table.add_row("default_model", settings.default_model)

        app.post_message(app.CommandResult(table))
