from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input

from teamcode.ui.app import TeamCodeApp
from teamcode.ui.commands.registry import CommandRegistry
from teamcode.ui.widgets.chat_area import ChatArea
from teamcode.ui.widgets.command_palette import CommandPalette
from teamcode.ui.widgets.input_bar import InputBar
from teamcode.ui.widgets.status_bar import StatusBar


class MainScreen(Screen):
    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
    }

    #chat-area {
        height: 1fr;
        min-height: 10;
        border-bottom: solid $primary 50%;
    }

    #command-palette {
        dock: bottom;
    }

    #input-bar {
        dock: bottom;
    }

    #status-bar {
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield ChatArea(id="chat-area")
            yield CommandPalette(id="command-palette")
            yield InputBar(id="input-bar")
            yield StatusBar(id="status-bar")

    def on_mount(self) -> None:
        self.query_one("#input-bar", InputBar).focus_input()
        CommandRegistry.discover()

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
        chat = self.query_one("#chat-area", ChatArea)
        chat.add_message(event.content)
        event.stop()

    @on(TeamCodeApp.ClearChat)
    def handle_clear(self, event: TeamCodeApp.ClearChat) -> None:
        chat = self.query_one("#chat-area", ChatArea)
        chat.clear()
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
        chat = self.query_one("#chat-area", ChatArea)
        chat.add_message(f"[bold]You:[/] {text}")

        self._update_history("message", text)

    def _update_history(self, msg_type: str, content: str) -> None:
        from datetime import datetime

        if hasattr(self.app, "message_history"):
            self.app.message_history.append(
                {
                    "type": msg_type,
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
