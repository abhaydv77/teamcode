from __future__ import annotations

from typing import TYPE_CHECKING

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class ModelsCommand(BaseCommand):
    name = "models"
    description = "List cached models from OpenRouter"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        cm = app.config_manager
        if cm is None:
            app.post_message(app.CommandResult("[bold red]Error:[/] ConfigManager not initialized"))
            return

        models = cm.get_cached_models()
        if not models:
            app.post_message(app.CommandResult(
                "[yellow]No cached models. Press r in /config to fetch from OpenRouter.[/]"
            ))
            return

        lines = [f"[bold #c0caf5]Cached Models[/]  ([dim]{len(models)} total[/])\n"]
        for m in models:
            mid = m.get("id", "?")
            name = m.get("name", "")
            ctx = m.get("context_length", 0)
            ctx_str = f"  {ctx // 1000}k ctx" if ctx else ""
            lines.append(f"  {mid}  [dim]{name}{ctx_str}[/]")

        app.post_message(app.CommandResult("\n".join(lines)))
