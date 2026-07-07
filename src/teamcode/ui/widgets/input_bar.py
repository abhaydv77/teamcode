from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Input


class InputBar(Widget):
    DEFAULT_CSS = """
    InputBar {
        height: auto;
        min-height: 3;
        padding: 0 1;
    }

    InputBar > Input {
        width: 100%;
    }
    """

    def compose(self) -> list[Input]:
        return [
            Input(
                id="message-input",
                placeholder="Type a message or / for commands...",
            ),
        ]

    def focus_input(self) -> None:
        self.query_one("#message-input", Input).focus()
