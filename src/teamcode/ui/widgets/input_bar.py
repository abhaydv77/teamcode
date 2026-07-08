from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Label


class InputBar(Widget):
    DEFAULT_CSS = """
    InputBar {
        dock: bottom;
        height: 1;
        background: #0d1117;
        layout: horizontal;
    }

    #input-prefix {
        width: 3;
        content-align: center middle;
        text-style: bold;
        color: #00d4aa;
        background: #0d1117;
    }

    #message-input {
        width: 1fr;
        border: none;
        background: #0d1117;
        color: #c0caf5;
        padding: 0 0;
    }

    #message-input:focus {
        border: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("❯", id="input-prefix")
        yield Input(
            id="message-input",
            placeholder="Type a message or / for commands...",
        )

    def focus_input(self) -> None:
        self.query_one("#message-input", Input).focus()
