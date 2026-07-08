from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Input, Label

from teamcode.ui.app import TeamCodeApp
from teamcode.ui.widgets.command_palette import CommandPalette
from teamcode.ui.widgets.header import Header
from teamcode.ui.widgets.input_bar import InputBar
from teamcode.ui.widgets.task_timeline import TaskTimeline
from teamcode.ui.widgets.team_roster import TeamRoster


class MainScreen(Screen):
    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
    }

    #body {
        height: 1fr;
    }

    #sidebar {
        width: 25%;
        min-width: 22;
        border-right: solid #1e2a3e;
    }

    #canvas {
        width: 75%;
    }

    #command-palette {
        dock: bottom;
    }

    #shortcut-legend {
        dock: bottom;
        height: 1;
        background: #0d1117;
        color: #565f89;
        padding: 0 3;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(id="app-header")
        with Horizontal(id="body"):
            yield TeamRoster(id="sidebar")
            yield TaskTimeline(id="canvas")
        yield CommandPalette(id="command-palette")
        yield InputBar(id="input-bar")
        yield Label(
            " [Tab] Switch Agent  |  [/] Commands  |  [Ctrl+K] Clear   ",
            id="shortcut-legend",
        )

    def on_mount(self) -> None:
        self.query_one("#input-bar", InputBar).focus_input()

    @on(Input.Changed, "#message-input")
    async def on_input_changed(self, event: Input.Changed) -> None:
        palette = self.query_one("#command-palette", CommandPalette)
        palette.query = event.value

    @on(Input.Submitted, "#message-input")
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return

        palette = self.query_one("#command-palette", CommandPalette)

        if palette.display:
            selected = palette.selected_command_name
            if selected:
                event.input.value = ""
                palette.query = ""
                await self._dispatch_command(f"/{selected}")
                self.query_one("#input-bar", InputBar).focus_input()
                return

        event.input.value = ""
        palette.query = ""

        if text.startswith("/"):
            await self._dispatch_command(text)
        else:
            await self._handle_message(text)

        self.query_one("#input-bar", InputBar).focus_input()

    @on(TeamCodeApp.CommandResult)
    def handle_command_result(self, event: TeamCodeApp.CommandResult) -> None:
        canvas = self.query_one("#canvas", TaskTimeline)
        canvas.add_message(event.content)
        event.stop()

    @on(TeamCodeApp.ClearChat)
    def handle_clear(self, event: TeamCodeApp.ClearChat) -> None:
        canvas = self.query_one("#canvas", TaskTimeline)
        canvas.clear()
        event.stop()

    @on(TeamCodeApp.StateChanged)
    def handle_state_changed(self, event: TeamCodeApp.StateChanged) -> None:
        self.query_one("#app-header", Header).refresh_meta()
        self.query_one("#sidebar", TeamRoster).refresh()
        event.stop()

    def key_escape(self) -> None:
        palette = self.query_one("#command-palette", CommandPalette)
        if palette.display:
            palette.query = ""
            self.query_one("#message-input", Input).value = ""
            self.query_one("#input-bar", InputBar).focus_input()
        else:
            self.app.action_quit()

    async def _dispatch_command(self, text: str) -> None:
        if hasattr(self.app, "run_command"):
            await self.app.run_command(text)

    async def _handle_message(self, text: str) -> None:
        canvas = self.query_one("#canvas", TaskTimeline)
        canvas.add_message(f"[bold #c0caf5]You:[/] {text}")

        self._update_history("message", text)

    def _update_history(self, msg_type: str, content: str) -> None:
        from datetime import datetime

        if hasattr(self.app, "message_history"):
            self.app.message_history.append({
                "type": msg_type,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            })
