from __future__ import annotations

from datetime import datetime
from typing import Any

from textual.app import App
from textual.message import Message

from teamcode.config.settings import TeamCodeSettings
from teamcode.ui.commands.registry import CommandRegistry
from teamcode.ui.screens.startup_screen import StartupScreen


class TeamCodeApp(App):
    CSS_PATH = "app.tcss"

    agent_assignments: dict[str, dict] = {}

    agent_states: dict[str, dict[str, str]] = {
        "product_manager": {"status": "idle", "emoji": "🧠", "label": "Product Manager"},
        "coordinator": {"status": "ready", "emoji": "⚡", "label": "Coordinator"},
        "developer": {"status": "offline", "emoji": "💻", "label": "Developer"},
        "reviewer": {"status": "offline", "emoji": "🔍", "label": "Reviewer"},
        "architect": {"status": "idle", "emoji": "🏗️", "label": "Architect"},
    }

    timeline_entries: list[dict[str, Any]] = []

    session_state: dict[str, Any] = {
        "session_id": "",
        "status": "idle",
        "task_count": 0,
        "started_at": "",
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
    workspace_path: str = "~/Projects/app"
    git_branch: str = "main"
    active_providers: list[str] = ["OpenAI", "Anthropic"]

    class CommandResult(Message):
        def __init__(self, content: Any) -> None:
            self.content = content
            super().__init__()

    class ClearChat(Message):
        pass

    class StateChanged(Message):
        pass

    def on_mount(self) -> None:
        CommandRegistry.discover()
        self.push_screen(StartupScreen())

    def notify_state_changed(self) -> None:
        self.post_message(self.StateChanged())

    async def run_command(self, input_text: str) -> None:
        parts = input_text[1:].strip().split()
        if not parts:
            return

        cmd_name = parts[0]
        cmd_args = parts[1:]

        cmd_cls = CommandRegistry.get(cmd_name)
        if cmd_cls is None:
            self.message_history.append({
                "type": "error",
                "content": f"Unknown command: {cmd_name}",
                "timestamp": datetime.utcnow().isoformat(),
            })
            self.post_message(self.CommandResult(f"[red]Unknown command: /{cmd_name}[/]"))
            return

        cmd = cmd_cls()
        await cmd.execute(self, cmd_args)

        self.message_history.append({
            "type": "command",
            "content": input_text,
            "timestamp": datetime.utcnow().isoformat(),
        })
