from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label


class StartupScreen(Screen):
    DEFAULT_CSS = """
    StartupScreen {
        align: center middle;
        background: $surface;
    }

    #startup-container {
        width: 50;
        height: auto;
    }

    #startup-title {
        text-align: center;
        content-align: center middle;
        color: $accent;
    }

    #startup-subtitle {
        text-align: center;
        content-align: center middle;
        color: $text-muted;
        margin-top: 1;
    }

    #startup-version {
        text-align: center;
        content-align: center middle;
        color: $text-disabled;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(
            Text.assemble(
                ("╔═══════════════════════════════════════╗\n", "cyan"),
                ("║           T E A M C O D E            ║\n", "bold cyan"),
                ("╚═══════════════════════════════════════╝", "cyan"),
            ),
            id="startup-title",
        )
        yield Label(
            "Terminal-First AI Software Engineering Team",
            id="startup-subtitle",
        )
        yield Label(
            "v0.1.0",
            id="startup-version",
        )

    def on_mount(self) -> None:
        self.set_timer(2.0, self._switch_to_main)

    def _switch_to_main(self) -> None:
        from teamcode.ui.screens.main_screen import MainScreen

        self.app.push_screen(MainScreen())
        self.app.remove_screen(self)
