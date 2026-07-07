from __future__ import annotations

from typing import Any

from textual.app import App
from textual.message import Message

from teamcode.config.settings import TeamCodeSettings
from teamcode.ui.commands.registry import CommandRegistry
from teamcode.ui.screens.startup_screen import StartupScreen


class TeamCodeApp(App):
    CSS_PATH = "app.tcss"

    agent_assignments: dict[str, dict] = {}
    session_state: dict[str, Any] = {
        "session_id": "",
        "status": "idle",
        "task_count": 0,
    }
    usage_stats: dict[str, Any] = {
        "total_tokens": 0,
        "total_cost": 0.0,
        "api_calls": 0,
        "session_tokens": 0,
    }
    message_history: list[dict[str, Any]] = []
    settings: TeamCodeSettings = TeamCodeSettings()
    current_project: str = ""

    class CommandResult(Message):
        def __init__(self, content: Any) -> None:
            self.content = content
            super().__init__()

    class ClearChat(Message):
        pass

    def on_mount(self) -> None:
        self.push_screen(StartupScreen())

    async def run_command(self, input_text: str) -> None:
        parts = input_text[1:].strip().split()
        if not parts:
            return

        cmd_name = parts[0]
        cmd_args = parts[1:]

        cmd_cls = CommandRegistry.get(cmd_name)
        if cmd_cls is None:
            from datetime import datetime

            self.message_history.append(
                {
                    "type": "error",
                    "content": f"Unknown command: {cmd_name}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            await self.post_message(self.CommandResult(f"[red]Unknown command: /{cmd_name}[/]"))
            return

        cmd = cmd_cls()
        await cmd.execute(self, cmd_args)

        from datetime import datetime

        self.message_history.append(
            {
                "type": "command",
                "content": input_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
