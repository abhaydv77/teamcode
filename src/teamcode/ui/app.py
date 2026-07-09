"""TeamCode — Clean Chat-Centric Terminal UI."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Input, Label, ListItem, ListView, RichLog

from teamcode.config.settings import TeamCodeSettings
from teamcode.ui.commands.registry import CommandRegistry

# ═══════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════

VERSION = "0.1.0"

LOGO_TEXT = Text.assemble(
    ("████████╗███████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗ ██████╗ ███████╗\n", "bold #00d4aa"),
    ("╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔════╝██╔═══██╗██╔══██╗██╔════╝\n", "#00d4aa"),
    ("   ██║   █████╗  ███████║██╔████╔██║██║     ██║   ██║██║  ██║█████╗\n", "#00d4aa"),
    ("   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║██║     ██║   ██║██║  ██║██╔══╝\n", "#00d4aa"),
    ("   ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╗╚██████╔╝██████╔╝███████╗\n", "bold #00d4aa"),
    ("   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝", "#00d4aa"),
)

# ═══════════════════════════════════════════════════════════════
# Messages
# ═══════════════════════════════════════════════════════════════


class CommandResult(Message):
    def __init__(self, content: Any) -> None:
        self.content = content
        super().__init__()


class ClearChat(Message):
    pass


# ═══════════════════════════════════════════════════════════════
# Widgets
# ═══════════════════════════════════════════════════════════════


class Logo(Widget):
    """Centered TEAMCODE logo banner."""

    DEFAULT_CSS = """
    Logo {
        height: 7;
        content-align: center middle;
        margin: 1 0 0 0;
    }
    """

    def render(self) -> Text:
        return LOGO_TEXT


class CommandLauncher(Widget):
    """Inline </ command area. Expands with command list when input starts with /."""

    DEFAULT_CSS = """
    CommandLauncher {
        height: auto;
        margin: 0 4 0 4;
        min-height: 2;
    }

    #launcher-prompt {
        content-align: center middle;
        color: #565f89;
        text-style: bold;
        height: 1;
    }

    #launcher-prompt.active {
        color: #0088ff;
    }

    #launcher-list {
        display: none;
        height: auto;
        max-height: 12;
        margin: 0 8 0 8;
        border: solid #1e2a3e;
        background: #0d1117;
    }

    #launcher-list.--visible {
        display: block;
    }

    CommandLauncher ListItem {
        height: 1;
        padding: 0 1;
        background: #0d1117;
    }

    CommandLauncher ListItem > Label:first-child {
        color: #00d4aa;
        width: 16;
    }

    CommandLauncher ListItem > Label:last-child {
        color: #565f89;
        width: 1fr;
    }

    CommandLauncher ListItem.--highlight {
        background: #1e2a3e;
    }
    """

    query = reactive("")

    def compose(self) -> ComposeResult:
        yield Label("</  type a command", id="launcher-prompt")
        yield ListView(id="launcher-list")

    def watch_query(self, q: str) -> None:
        prompt = self.query_one("#launcher-prompt", Label)
        lv = self.query_one("#launcher-list", ListView)

        if q.startswith("/"):
            prompt.update(f"</ {q}")
            prompt.set_classes("active")
            remaining = q[1:]
            lv.display = True
            if remaining:
                self._populate(remaining)
            else:
                lv.clear()
        else:
            prompt.update("</  type a command")
            prompt.set_classes("")
            lv.display = False

    def _populate(self, search: str) -> None:
        lv = self.query_one("#launcher-list", ListView)
        lv.clear()
        for cmd in CommandRegistry.search(search):
            item = ListItem(
                Label(f"/{cmd.name}"),
                Label(cmd.description[:60]),
            )
            item.cmd_name = cmd.name
            lv.append(item)
        if lv.children:
            lv.index = 0

    @property
    def selected_cmd_name(self) -> str | None:
        lv = self.query_one("#launcher-list", ListView)
        if lv.index is not None and lv.children:
            return getattr(lv.children[lv.index], "cmd_name", None)
        return None


class ConversationArea(Widget):
    """Large scrollable conversation / log area."""

    DEFAULT_CSS = """
    ConversationArea {
        height: 1fr;
        border-top: solid #1e2a3e;
        margin: 0 1;
    }

    ConversationArea > RichLog {
        height: 1fr;
        background: #0d1117;
    }
    """

    def compose(self) -> ComposeResult:
        return [RichLog(id="chat-log", highlight=True, markup=True, wrap=True, min_width=40)]

    def on_mount(self) -> None:
        self._welcome()

    def add(self, content: Any) -> None:
        self.query_one("#chat-log", RichLog).write(content)

    def clear(self) -> None:
        self.query_one("#chat-log", RichLog).clear()
        self._welcome()

    def _welcome(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(Text.assemble(("TEAMCODE ", "bold #00d4aa"), (f"v{VERSION}", "dim #565f89")))
        log.write(Text("Terminal-first AI software engineering", "italic #565f89"))
        log.write("")
        log.write(Text.assemble(
            "Type ", ("/help", "bold #0088ff"), " for commands.",
        ))
        log.write("")


class InputBar(Widget):
    """Fixed bottom input bar with ❯ prompt."""

    DEFAULT_CSS = """
    InputBar {
        dock: bottom;
        height: 1;
        background: #0d1117;
        border-top: solid #1e2a3e;
        layout: horizontal;
    }

    #input-prompt {
        width: 3;
        content-align: center middle;
        text-style: bold;
        color: #00d4aa;
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
        yield Label("❯", id="input-prompt")
        yield Input(id="message-input", placeholder="Type a message or / for commands...")

    def focus_input(self) -> None:
        self.query_one("#message-input", Input).focus()


# ═══════════════════════════════════════════════════════════════
# Main Screen
# ═══════════════════════════════════════════════════════════════

SCREEN_CSS = """
MainScreen {
    layout: vertical;
    background: #0a0e14;
}

#shortcut-legend {
    dock: bottom;
    height: 1;
    background: #0d1117;
    color: #565f89;
    padding: 0 3;
}
"""


class MainScreen(Screen):
    DEFAULT_CSS = SCREEN_CSS

    def compose(self) -> ComposeResult:
        yield Logo()
        yield CommandLauncher(id="launcher")
        yield ConversationArea(id="conversation")
        yield InputBar(id="input-bar")
        yield Label(
            " [Tab] Switch Mode  |  [/] Commands  |  [Ctrl+K] Clear  |  [Esc] Quit",
            id="shortcut-legend",
        )

    def on_mount(self) -> None:
        self.query_one("#input-bar", InputBar).focus_input()
        CommandRegistry.discover()

    # ── Input changed → update command launcher ──

    @on(Input.Changed, "#message-input")
    def on_input_changed(self, event: Input.Changed) -> None:
        self.query_one("#launcher", CommandLauncher).query = event.value

    # ── Input submitted → dispatch ──

    @on(Input.Submitted, "#message-input")
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return

        launcher = self.query_one("#launcher", CommandLauncher)
        if launcher.query.startswith("/"):
            selected = launcher.selected_cmd_name
            if selected:
                event.input.value = ""
                launcher.query = ""
                await self._run_cmd(f"/{selected}")
                self._focus()
                return

        event.input.value = ""
        launcher.query = ""

        if text.startswith("/"):
            await self._run_cmd(text)
        else:
            await self._chat(text)

        self._focus()

    def _focus(self) -> None:
        self.query_one("#input-bar", InputBar).focus_input()

    # ── Dispatch ──

    async def _run_cmd(self, text: str) -> None:
        await self.app.run_command(text)  # type: ignore[arg-type]

    async def _chat(self, text: str) -> None:
        self.query_one("#conversation", ConversationArea).add(f"[bold #c0caf5]You:[/] {text}")

    # ── Message handlers ──

    @on(CommandResult)
    def handle_result(self, event: CommandResult) -> None:
        self.query_one("#conversation", ConversationArea).add(event.content)
        event.stop()

    @on(ClearChat)
    def handle_clear(self, event: ClearChat) -> None:
        self.query_one("#conversation", ConversationArea).clear()
        event.stop()

    def key_escape(self) -> None:
        self.app.action_quit()


# ═══════════════════════════════════════════════════════════════
# Application
# ═══════════════════════════════════════════════════════════════

CSS_GLOBALS = """
Screen { background: #0a0e14; }
* { scrollbar-size-vertical: 1; scrollbar-color: #1e2a3e; }
RichLog { background: #0d1117; color: #c0caf5; }
RichLog > * { background: #0d1117; }
Input { background: #0d1117; color: #c0caf5; border: none; }
Input:focus { border: none; }
ListView { background: #0d1117; }
ListItem { background: #0d1117; }
Label { background: transparent; }
"""


class TeamCodeApp(App):
    CSS = CSS_GLOBALS

    CommandResult = CommandResult
    ClearChat = ClearChat

    def post_message(self, message: Message) -> bool:
        if self.screen is not None and isinstance(message, (CommandResult, ClearChat)):
            return self.screen.post_message(message)
        return super().post_message(message)

    message_history: list[dict[str, Any]] = []
    session_state: dict[str, Any] = {}
    usage_stats: dict[str, Any] = {}
    agent_assignments: dict[str, dict] = {}
    settings: TeamCodeSettings = TeamCodeSettings()

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

    async def run_command(self, input_text: str) -> None:
        parts = input_text[1:].strip().split()
        if not parts:
            return
        name, args = parts[0], parts[1:]

        cmd_cls = CommandRegistry.get(name)
        if cmd_cls is None:
            self.post_message(CommandResult(f"[red]Unknown command: /{name}[/]"))
            return

        cmd = cmd_cls()
        await cmd.execute(self, args)

        self.message_history.append({
            "type": "command",
            "content": input_text,
            "timestamp": datetime.utcnow().isoformat(),
        })
