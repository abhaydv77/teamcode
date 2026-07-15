"""Role management command — view and edit per-role config."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.text import Text

from teamcode.ui.commands.base import BaseCommand

if TYPE_CHECKING:
    from teamcode.ui.app import TeamCodeApp

ROLE_LABELS: dict[str, str] = {
    "product_manager": "Product Manager",
    "coordinator": "Coordinator",
    "architect": "Architect",
    "developer": "Junior Engineer",
    "reviewer": "Reviewer",
    "tester": "Tester",
}

ROLE_ORDER = [
    "product_manager",
    "coordinator",
    "architect",
    "developer",
    "reviewer",
    "tester",
]


def _build_role_list(cm: Any, active_index: int = 0, editing_role: str | None = None) -> Text:
    lines: list[tuple[str, str]] = []
    lines.append(("AI Roles", "bold #c0caf5"))
    roles_data = cm.list_roles()
    count = len(roles_data)
    lines.append((f"  ({count} configured)\n\n", "dim #565f89"))

    for i, name in enumerate(ROLE_ORDER):
        if name not in roles_data:
            continue
        cfg = roles_data[name]
        label = ROLE_LABELS.get(name, name.replace("_", " ").title())
        model = cfg.get("model", "—")
        prefix = "  "
        if i == active_index:
            prefix = "> "
        mark = "  [bold #00d4aa]\u25cf[/]" if name == editing_role else ""
        lines.append((f"{prefix}{label:<22} {model}{mark}\n", ""))

    lines.append(("\n", ""))
    lines.append((
        "  [yellow][\u2191\u2193][/] Navigate  \u00b7  [yellow][Enter][/] Edit"
        "  \u00b7  [yellow][r][/] Reset  \u00b7  [yellow][Esc][/] Back\n",
        "dim #565f89",
    ))
    text = Text()
    for content, style in lines:
        if style:
            text.append(content, style=style)
        else:
            text.append(content)
    return text


def _build_role_edit(cm: Any, role_name: str) -> Text:
    cfg = cm.get_role_config(role_name)
    label = ROLE_LABELS.get(role_name, role_name.replace("_", " ").title())
    model = cfg.get("model", "—")
    prompt = cfg.get("system_prompt", "")

    lines: list[tuple[str, str]] = []
    lines.append((f"Edit Role: {label}\n\n", "bold #c0caf5"))
    lines.append((f"  Model:           {model}\n\n", ""))
    lines.append(("  System Prompt:\n", ""))
    lines.append(("  \u2500" * 50 + "\n", "dim #565f89"))
    for line in prompt.split("\n"):
        lines.append((f"  {line}\n", "italic #c0caf5"))
    lines.append(("  \u2500" * 50 + "\n\n", "dim #565f89"))
    lines.append((
        "  [yellow][m][/] Change Model  \u00b7  [yellow][p][/] Edit Prompt"
        "  \u00b7  [yellow][r][/] Reset to Default"
        "  \u00b7  [yellow][Enter][/] Save  \u00b7  [yellow][Esc][/] Back\n",
        "dim #565f89",
    ))

    text = Text()
    for content, style in lines:
        if style:
            text.append(content, style=style)
        else:
            text.append(content)
    return text


class RolesCommand(BaseCommand):
    name = "roles"
    description = "View and edit per-role AI configuration"

    async def execute(self, app: TeamCodeApp, args: list[str]) -> None:
        cm = app.config_manager
        if cm is None:
            app.post_message(app.CommandResult("[bold red]Error:[/] ConfigManager not initialized"))
            return

        app.roles_mode = True
        app.roles_view = "list"
        app.roles_active_index = 0
        app.roles_editing_role = None
        app.post_message(app.CommandResult(_build_role_list(cm)))
