from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from rich.text import Text

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp


def _format_age(dt_str: str | None) -> str:
    if not dt_str:
        return "never"
    try:
        dt = datetime.fromisoformat(dt_str)
        delta = datetime.now(UTC) - dt
        mins = int(delta.total_seconds() // 60)
        if mins < 1:
            return "just now"
        if mins < 60:
            return f"{mins} min ago"
        hours = mins // 60
        return f"{hours}h ago"
    except Exception:
        return "unknown"


def _build_config_display(cm: Any) -> Text:
    lines: list[tuple[str, str]] = []

    lines.append(("Configuration\n", "bold #c0caf5"))

    api_key = cm.get_api_key()
    if api_key:
        masked = api_key[:12] + "..." + api_key[-4:]
        lines.append((f"  API Key:           [{_key_status(api_key)}]{masked}[/]\n", ""))
    else:
        lines.append(("  API Key:           [red]not set[/]\n", ""))

    default_model = cm.get_default_model()
    lines.append((f"  Default Model:     {default_model}\n", ""))

    conn = cm.get_connection_status()
    if conn.get("connection_ok"):
        lines.append(("  Connection:        [green]\u2713 Connected (OpenRouter)[/]\n", ""))
    elif conn.get("last_tested"):
        lines.append(("  Connection:        [red]\u2717 Failed[/]\n", ""))
    elif api_key:
        lines.append(("  Connection:        [yellow]\u2717 not tested[/]\n", ""))
    else:
        lines.append(("  Connection:        [red]\u2717 not tested[/]\n", ""))

    cache = cm.get_cache_info()
    if cache.get("count"):
        age = _format_age(cache.get("fetched_at"))
        lines.append((f"  Models Cached:     {cache['count']} models (updated {age})\n", ""))
    elif api_key:
        lines.append(("  Models Cached:     [dim]none — press r to fetch[/]\n", ""))
    else:
        lines.append(("  Models Cached:     [dim]set an API key first[/]\n", ""))

    lines.append(("\n", ""))
    shortcuts = []
    if api_key:
        shortcuts.append("[yellow][F5][/] Test Connection")
    shortcuts.append("[yellow][e][/] Edit API Key")
    if api_key:
        shortcuts.append("[yellow][d][/] Default Model")
        shortcuts.append("[yellow][r][/] Refresh Models")
    shortcuts.append("[yellow][Esc][/] Back")
    lines.append(("  " + "  \u00b7  ".join(shortcuts) + "\n", ""))

    text = Text()
    for content, style in lines:
        if style:
            text.append(content, style=style)
        else:
            text.append(content)
    return text


def _key_status(api_key: str | None) -> str:
    if api_key:
        return "green"
    return "red"


class ConfigCommand(BaseCommand):
    name = "config"
    description = "View or edit AI provider configuration"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        cm = app.config_manager

        if args and args[0] == "key":
            if len(args) > 1:
                key = args[1]
                if cm.validate_api_key(key):
                    cm.set_api_key(key)
                    app.post_message(app.CommandResult(
                        "[green]\u2713 API key saved[/]"
                    ))
                else:
                    app.post_message(app.CommandResult(
                        "[bold red]Error:[/] Invalid API key format. Expected sk-or-v1-..."
                    ))
            else:
                app.config_pending_action = "key"
                app.post_message(app.CommandResult(
                    "[yellow]Paste your OpenRouter API key and press Enter:[/]"
                ))
            app.config_mode = True
            app.post_message(app.CommandResult(_build_config_display(cm)))
            return

        if args and args[0] == "test":
            app.post_message(app.CommandResult(
                "[yellow]Testing connection...[/]"
            ))
            ok = cm.test_connection()
            if ok:
                app.post_message(app.CommandResult(
                    "[green]\u2713 Connected to OpenRouter[/]"
                ))
            else:
                app.post_message(app.CommandResult(
                    "[bold red]Error:[/] Connection failed. Check your API key and network."
                ))
            app.config_mode = True
            app.post_message(app.CommandResult(_build_config_display(cm)))
            return

        if args and args[0] == "model":
            if len(args) > 1:
                cm.set_default_model(args[1])
                app.post_message(app.CommandResult(
                    f"[green]\u2713 Default model set to {args[1]}[/]"
                ))
            app.config_mode = True
            app.post_message(app.CommandResult(_build_config_display(cm)))
            return

        app.config_mode = True
        app.post_message(app.CommandResult(_build_config_display(cm)))
