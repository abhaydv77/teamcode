from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class Header(Widget):
    DEFAULT_CSS = """
    Header {
        dock: top;
        height: 3;
        background: #0d1117;
        border-bottom: solid #1e2a3e;
    }

    #header-logo {
        width: 1fr;
        padding: 0 1;
        text-style: bold;
    }

    #header-meta {
        width: 1fr;
        padding: 0 1;
        color: #565f89;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(id="header-logo")
        yield Label(id="header-meta")

    def on_mount(self) -> None:
        self._update_logo()
        self._update_meta()

    def _update_logo(self) -> None:
        logo = self.query_one("#header-logo", Label)
        logo.update(
            Text.assemble(
                ("████████╗███████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗ ██████╗ ███████╗", "bold #00d4aa"),
                ("  ", "dim"),
                ("v0.1.0", "dim #565f89"),
            )
        )

    def _update_meta(self) -> None:
        meta = self.query_one("#header-meta", Label)
        app = self.app
        session_status = app.session_state.get("status", "idle")
        status_color = "#00d4aa" if session_status == "active" else "#565f89"
        meta.update(
            Text.assemble(
                ("Workspace: ", "#565f89"),
                (app.workspace_path, "#c0caf5"),
                ("  │  Git: ", "#565f89"),
                (app.git_branch, "#c0caf5"),
                ("  │  Providers: ", "#565f89"),
                (", ".join(app.active_providers), "#c0caf5"),
                ("  │  Session: ", "#565f89"),
                (session_status, status_color),
            )
        )

    def refresh_meta(self) -> None:
        self._update_meta()
