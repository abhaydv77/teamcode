"""TeamCode — Clean Chat-Centric Terminal UI."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any
from uuid import uuid4

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Input, Label, ListItem, ListView, RichLog

from teamcode.agents.registry import AgentRegistry
from teamcode.config.settings import TeamCodeSettings
from teamcode.domain.agent import AgentConfig, Role
from teamcode.domain.context import SessionContext
from teamcode.domain.message import Message as DomainMessage
from teamcode.domain.task import Task
from teamcode.orchestrator.engine import Orchestrator
from teamcode.orchestrator.events import AgentFinished, AgentStarted, AgentTokenEvent
from teamcode.providers.litellm import LiteLLMProvider
from teamcode.ui.commands.registry import CommandRegistry

# ═══════════════════════════════════════════════════════════════
# Messages
# ═══════════════════════════════════════════════════════════════


class CommandResult(Message):
    def __init__(self, content: Any) -> None:
        self.content = content
        super().__init__()


class ClearChat(Message):
    pass


class OverlayCommand(Message):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__()


# ═══════════════════════════════════════════════════════════════
# Widgets
# ═══════════════════════════════════════════════════════════════


class Header(Widget):
    DEFAULT_CSS = """
    Header {
        height: 1;
        padding: 0 2;
        background: #0a0e14;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("", id="header-text")

    def update_info(self, model: str, branch: str) -> None:
        label = self.query_one("#header-text", Label)
        label.update(f">_ TeamCode  ·  {model}  ·  {branch}")


class ConversationArea(Widget):
    DEFAULT_CSS = """
    ConversationArea {
        height: 1fr;
        margin: 0 2;
    }
    ConversationArea > RichLog {
        height: 1fr;
        background: #0a0e14;
    }
    """

    def compose(self) -> ComposeResult:
        yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)

    def on_mount(self) -> None:
        self._show_empty_state()

    def _show_empty_state(self) -> None:
        self._showing_empty = True
        log = self.query_one("#chat-log", RichLog)
        log.write(Text("\nReady.\n", style="italic #565f89"))
        log.write(Text("Try:"))
        log.write(Text('  \u2022 Build a FastAPI API'))
        log.write(Text('  \u2022 Explain this repository'))
        log.write(Text('  \u2022 Review my code'))
        log.write(Text('  \u2022 Configure an AI provider'))

    def add(self, content: Any) -> None:
        log = self.query_one("#chat-log", RichLog)
        if self._showing_empty:
            log.clear()
            self._showing_empty = False
        log.write(content)

    def clear(self) -> None:
        self.query_one("#chat-log", RichLog).clear()
        self._show_empty_state()


class InputBar(Widget):
    DEFAULT_CSS = """
    InputBar {
        height: 1;
        layout: horizontal;
        padding: 0 2;
        background: #0a0e14;
    }
    #prompt {
        width: 2;
        color: #c0caf5;
        text-style: bold;
    }
    #message-input {
        width: 1fr;
        border: none;
        background: #0a0e14;
        color: #c0caf5;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(">", id="prompt")
        yield Input(id="message-input", placeholder="Type your task...")

    def focus_input(self) -> None:
        self.query_one("#message-input", Input).focus()


class InputArea(Widget):
    DEFAULT_CSS = """
    InputArea {
        dock: bottom;
        height: auto;
        background: #0a0e14;
    }
    """

    def compose(self) -> ComposeResult:
        yield InputBar(id="input-bar")
        yield FooterBar()


class FooterBar(Widget):
    DEFAULT_CSS = """
    FooterBar {
        height: 1;
        layout: horizontal;
        padding: 0 2;
        background: #0a0e14;
        color: #565f89;
    }
    #workspace {
        width: 1fr;
    }
    #shortcuts {
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("", id="workspace")
        yield Label("Ctrl+K Commands · Esc Cancel", id="shortcuts")

    def update_workspace(self, path: str) -> None:
        self.query_one("#workspace", Label).update(f"workspace: {path}")


class CommandOverlay(Widget):
    """Compact command palette opened by Ctrl+K."""

    DEFAULT_CSS = """
    CommandOverlay {
        layer: overlay;
        height: auto;
        max-height: 16;
        width: 60%;
        min-width: 40;
        margin: 1 2;
        background: #151922;
        border: solid #1e2a3e;
        display: none;
    }
    CommandOverlay.--visible {
        display: block;
    }
    CommandOverlay > Input {
        width: 1fr;
        border: none;
        background: #151922;
        color: #c0caf5;
        margin: 0 1;
    }
    CommandOverlay > ListView {
        height: auto;
        max-height: 12;
        background: #151922;
    }
    CommandOverlay ListItem {
        height: 1;
        padding: 0 1;
        background: #151922;
    }
    CommandOverlay ListItem > Label:first-child {
        color: #00d4aa;
        width: 18;
    }
    CommandOverlay ListItem > Label:last-child {
        color: #565f89;
        width: 1fr;
    }
    """

    COMMANDS = [
        ("Chat", "Resume chat mode"),
        ("Session", "View session info"),
        ("Roles", "Manage agent roles"),
        ("AI Config", "Configure AI provider"),
        ("Guide", "Show help guide"),
        ("Exit", "Exit the application"),
    ]

    def compose(self) -> ComposeResult:
        yield Input(id="overlay-input", placeholder="Type to filter commands...")
        yield ListView(id="overlay-list")

    def on_mount(self) -> None:
        self._populate("")

    def _populate(self, filter_text: str) -> None:
        lv = self.query_one("#overlay-list", ListView)
        lv.clear()
        filter_lower = filter_text.lower()
        for name, desc in self.COMMANDS:
            if filter_text and filter_lower not in name.lower() \
                    and filter_lower not in desc.lower():
                continue
            item = ListItem(
                Label(name),
                Label(desc),
            )
            item.cmd_name = name
            lv.append(item)
        if lv.children:
            lv.index = 0

    @on(Input.Changed, "#overlay-input")
    def on_input_changed(self, event: Input.Changed) -> None:
        self._populate(event.value.strip())

    @on(Input.Submitted, "#overlay-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        lv = self.query_one("#overlay-list", ListView)
        if lv.index is not None and lv.children:
            selected = lv.children[lv.index]
            name = getattr(selected, "cmd_name", None)
            if name:
                self.post_message(OverlayCommand(name))
        self._close()

    @on(ListView.Selected, "#overlay-list")
    def on_list_selected(self, event: ListView.Selected) -> None:
        if event.item:
            name = getattr(event.item, "cmd_name", None)
            if name:
                self.post_message(OverlayCommand(name))
        self._close()

    def _close(self) -> None:
        self.remove_class("--visible")
        self.query_one("#overlay-input", Input).value = ""


# ═══════════════════════════════════════════════════════════════
# Main Screen
# ═══════════════════════════════════════════════════════════════


class MainScreen(Screen):
    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
        background: #0a0e14;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield ConversationArea(id="conversation")
        yield InputArea()
        yield CommandOverlay(id="command-overlay")

    def on_mount(self) -> None:
        CommandRegistry.discover()
        header = self.query_one(Header)
        model = self.app.settings.default_model or "\u2014"
        header.update_info(model, "main")
        footer = self.query_one(FooterBar)
        try:
            footer.update_workspace(os.getcwd())
        except OSError:
            footer.update_workspace("\u2014")
        self.query_one("#message-input", Input).focus()

    @on(Input.Submitted, "#message-input")
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""
        if text.startswith("/"):
            await self._run_cmd(text)
        else:
            await self._chat(text)
        self._focus()

    def _focus(self) -> None:
        self.query_one("#input-bar", InputBar).focus_input()

    async def _run_cmd(self, text: str) -> None:
        await self.app.run_command(text)

    async def _chat(self, text: str) -> None:
        conversation = self.query_one("#conversation", ConversationArea)
        conversation.add(f"[bold #c0caf5]You:[/] {text}")

        context = SessionContext(
            session_id=str(uuid4()),
            task=Task(id=str(uuid4()), description=text),
            messages=[
                DomainMessage(
                    id=str(uuid4()),
                    sender="user",
                    content=text,
                ),
            ],
        )

        provider = LiteLLMProvider()
        agents = []
        for role_key in self.app.TEAM_PIPELINE:
            config = AgentConfig(
                role=Role(role_key),
                name=role_key.replace("_", " ").title(),
                model=self.app.settings.default_model,
            )
            agent = AgentRegistry.create(role_key, config, provider)
            agents.append(agent)

        orchestrator = Orchestrator(agents=agents)

        current_agent = ""
        agent_buffer = ""

        async def on_agent_started(event: AgentStarted) -> None:
            nonlocal current_agent, agent_buffer
            current_agent = event.agent_name
            agent_buffer = ""
            label = event.agent_name.replace("_", " ").title()
            conversation.add(f"\n[bold #00d4aa]\u25cf {label}[/]")

        async def on_agent_token(event: AgentTokenEvent) -> None:
            nonlocal agent_buffer
            agent_buffer += event.token
            if len(agent_buffer) >= 40:
                conversation.add(agent_buffer)
                agent_buffer = ""

        async def on_agent_finished(event: AgentFinished) -> None:
            nonlocal current_agent, agent_buffer
            if agent_buffer:
                conversation.add(agent_buffer)
            label = current_agent.replace("_", " ").title()
            conversation.add(f"[dim #565f89]\u2713 {label}[/]")
            current_agent = ""
            agent_buffer = ""

        orchestrator.event_bus.on(AgentStarted)(on_agent_started)
        orchestrator.event_bus.on(AgentTokenEvent)(on_agent_token)
        orchestrator.event_bus.on(AgentFinished)(on_agent_finished)

        try:
            await orchestrator.run(context)
        except Exception as exc:
            conversation.add(f"\n[bold red]Error:[/] {exc}")

    @on(CommandResult)
    def handle_result(self, event: CommandResult) -> None:
        self.query_one("#conversation", ConversationArea).add(event.content)
        event.stop()

    @on(ClearChat)
    def handle_clear(self, event: ClearChat) -> None:
        self.query_one("#conversation", ConversationArea).clear()
        event.stop()

    def key_ctrl_k(self) -> None:
        overlay = self.query_one("#command-overlay", CommandOverlay)
        if overlay.has_class("--visible"):
            overlay.remove_class("--visible")
            self._focus()
        else:
            overlay.add_class("--visible")
            overlay.query_one("#overlay-input", Input).focus()

    def key_escape(self) -> None:
        overlay = self.query_one("#command-overlay", CommandOverlay)
        if overlay.has_class("--visible"):
            overlay.remove_class("--visible")
            self._focus()
        else:
            self.app.action_quit()

    @on(OverlayCommand)
    async def handle_overlay_command(self, event: OverlayCommand) -> None:
        command_map = {
            "Chat": None,
            "Session": "/session",
            "Roles": "/agents",
            "AI Config": "/config",
            "Guide": "/help",
            "Exit": "/exit",
        }
        cmd = command_map.get(event.name)
        if cmd:
            await self._run_cmd(cmd)
        self._focus()


# ═══════════════════════════════════════════════════════════════
# Application
# ═══════════════════════════════════════════════════════════════

CSS_GLOBALS = """
Screen { background: #0a0e14; }
* { scrollbar-size-vertical: 1; scrollbar-color: #1e2a3e; }
RichLog { background: #0a0e14; color: #c0caf5; }
RichLog > * { background: #0a0e14; }
Input { background: #0a0e14; color: #c0caf5; border: none; }
Input:focus { border: none; }
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

    TEAM_PIPELINE: list[str] = [
        "coordinator",
        "product_manager",
        "architect",
        "developer",
        "reviewer",
        "tester",
        "coordinator",
    ]

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
