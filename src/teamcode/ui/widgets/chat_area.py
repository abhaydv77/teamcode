from __future__ import annotations

from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog


class ChatArea(Widget):
    messages: list[dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        return [
            RichLog(id="chat-log", highlight=True, markup=True, wrap=True, min_width=40),
        ]

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        self._write_welcome(log)

    def add_message(self, content: Any) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(content)
        self.messages.append({"content": content})

    def clear(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        self.messages.clear()

    def _write_welcome(self, log: RichLog) -> None:
        log.write(
            Text.assemble(
                ("TeamCode ", "bold cyan"),
                ("v0.1.0", "dim"),
            )
        )
        log.write(
            Text("Terminal-first AI software engineering team", "italic dim"),
        )
        log.write("")
        log.write(
            Text.assemble(
                "Type ",
                ("/help", "bold cyan"),
                (" to see available commands.", ""),
            )
        )
        log.write("")
