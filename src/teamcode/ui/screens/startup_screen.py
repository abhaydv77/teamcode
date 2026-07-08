from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label


class StartupScreen(Screen):
    DEFAULT_CSS = """
    StartupScreen {
        align: center middle;
        background: #0a0e14;
    }

    #startup-container {
        width: 50;
        height: auto;
    }

    #startup-title {
        text-align: center;
        content-align: center middle;
    }

    #startup-subtitle {
        text-align: center;
        content-align: center middle;
        color: #565f89;
        margin-top: 1;
    }

    #startup-status {
        text-align: center;
        content-align: center middle;
        color: #565f89;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(
            Text.assemble(
                ("████████╗███████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗ ██████╗ ███████╗\n", "bold #00d4aa"),
                ("╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔════╝██╔═══██╗██╔══██╗██╔════╝\n", "#00d4aa"),
                ("   ██║   █████╗  ███████║██╔████╔██║██║     ██║   ██║██║  ██║█████╗\n", "#00d4aa"),
                ("   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║██║     ██║   ██║██║  ██║██╔══╝\n", "#00d4aa"),
                ("   ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╗╚██████╔╝██████╔╝███████╗\n", "bold #00d4aa"),
                ("   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝", "#00d4aa"),
            ),
            id="startup-title",
        )
        yield Label(
            "Terminal-first AI Software Engineering Team",
            id="startup-subtitle",
        )
        yield Label(
            "Loading Mission Control...",
            id="startup-status",
        )

    def on_mount(self) -> None:
        self.set_timer(2.0, self._switch_to_main)

    def _switch_to_main(self) -> None:
        from teamcode.ui.screens.main_screen import MainScreen

        self.app.switch_screen(MainScreen())
