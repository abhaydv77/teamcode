from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class StatusBar(Widget):
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $panel;
        color: $text-muted;
        layout: horizontal;
    }
    """

    project_name = reactive("none")
    session_status = reactive("idle")

    def render(self) -> Text:
        left = Text.assemble(
            (" Project: ", "dim"),
            (self.project_name, "bold"),
        )
        right = Text.assemble(
            ("  │  Session: ", "dim"),
            (self.session_status, "green" if self.session_status == "active" else "yellow"),
            ("  │  v0.1.0  ", "dim"),
        )
        text = left + Text(" " * 4) + right
        return text
