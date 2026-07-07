from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


class ModelsCommand(BaseCommand):
    name = "models"
    description = "List available models and their providers"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        table = Table(title="Available Models", border_style="blue")
        table.add_column("Provider", style="cyan", width=16)
        table.add_column("Models", style="white")

        models_by_provider = {
            "openai": "gpt-4o, gpt-4o-mini, gpt-4-turbo",
            "anthropic": "claude-3-opus, claude-3-sonnet, claude-3-haiku",
            "gemini": "gemini-1.5-pro, gemini-1.5-flash",
            "groq": "llama-3.1-70b, mixtral-8x7b",
            "mistral": "mistral-large, mistral-medium",
            "deepseek": "deepseek-coder, deepseek-chat",
            "openrouter": "any supported model via OpenRouter",
        }

        settings = app.settings
        for provider, models in models_by_provider.items():
            key = settings.available_providers.get(provider)
            status = "[green]✓[/]" if key else "[dim]no key[/]"
            table.add_row(f"{status} {provider}", models)

        await app.post_message(app.CommandResult(table))
