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
from textual.widgets import Input, Label, RichLog

from teamcode.agents.registry import AgentRegistry
from teamcode.config.manager import ROLE_NAMES as CM_ROLE_NAMES
from teamcode.config.manager import ConfigManager
from teamcode.config.settings import TeamCodeSettings
from teamcode.domain.agent import AgentConfig, Role
from teamcode.domain.context import SessionContext
from teamcode.domain.message import Message as DomainMessage
from teamcode.domain.task import Task
from teamcode.orchestrator.engine import Orchestrator
from teamcode.orchestrator.events import AgentFinished, AgentStarted, AgentTokenEvent
from teamcode.providers.litellm import LiteLLMProvider
from teamcode.ui.commands.registry import CommandRegistry
from teamcode.ui.widgets.model_picker import ModelPicker, ModelSelected
from teamcode.ui.widgets.slash_palette import (
    CommandSelected,
    SlashAutocomplete,
    SlashPalette,
    SlashPaletteClose,
)

MENTION_ALIASES: dict[str, str] = {
    "pm": "product_manager",
    "coord": "coordinator",
    "arch": "architect",
    "dev": "developer",
    "rev": "reviewer",
    "tst": "tester",
}

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
        yield Label("/cmd · Esc Cancel", id="shortcuts")

    def update_workspace(self, path: str) -> None:
        self.query_one("#workspace", Label).update(f"workspace: {path}")

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
        yield SlashPalette(id="slash-palette")
        yield ModelPicker(id="model-picker", models=[])

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

    @on(Input.Changed, "#message-input")
    def on_message_changed(self, event: Input.Changed) -> None:
        value = event.value
        if value.startswith("/") and len(value) > 1:
            palette = self.query_one("#slash-palette", SlashPalette)
            event.input.value = ""
            palette.open(value[1:])

    @on(Input.Submitted, "#message-input")
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""

        if self.app.config_pending_action == "key":
            cm = self.app.config_manager
            if cm:
                if cm.validate_api_key(text):
                    cm.set_api_key(text)
                    self.query_one("#conversation", ConversationArea).add(
                        "[green]\u2713 API key saved[/]"
                    )
                    self.query_one("#conversation", ConversationArea).add(
                        self._build_config_display()
                    )
                else:
                    self.query_one("#conversation", ConversationArea).add(
                        "[bold red]Error:[/] Invalid API key format. Expected sk-or-v1-..."
                    )
            self.app.config_pending_action = None
            self.query_one("#message-input", Input).placeholder = "Type your task..."
            self._focus()
            return

        if self.app.roles_pending_action == "prompt":
            cm = self.app.config_manager
            role_name = getattr(self, "_roles_editing_name", None)
            if cm and role_name:
                role_cfg = cm.get_role_config(role_name)
                role_cfg["system_prompt"] = text
                cm.set_role_config(role_name, role_cfg)
                self.query_one("#conversation", ConversationArea).add(
                    f"[green]\u2713 Prompt updated for {role_name.replace('_', ' ').title()}[/]"
                )
                from teamcode.ui.commands.roles import _build_role_edit
                self.query_one("#conversation", ConversationArea).add(
                    _build_role_edit(cm, role_name)
                )
            self.app.roles_pending_action = None
            self.query_one("#message-input", Input).placeholder = "Type your task..."
            self._focus()
            return

        if text.startswith("/"):
            await self._run_cmd(text)
        else:
            await self._chat(text)
        self._focus()

    def _focus(self) -> None:
        self.query_one("#input-bar", InputBar).focus_input()

    async def _run_cmd(self, text: str) -> None:
        await self.app.run_command(text)

    def _parse_mention(self, text: str) -> tuple[str | None, str]:
        if not text.startswith("@"):
            return None, text
        rest = text[1:]
        mention = ""
        for ch in rest:
            if ch.isalnum() or ch == "_":
                mention += ch
            else:
                break
        if not mention:
            return None, text
        mention = mention.lower()
        role_key = MENTION_ALIASES.get(mention, mention)
        remainder = rest[len(mention):].strip()
        if role_key not in CM_ROLE_NAMES:
            return mention, text
        return role_key, remainder

    async def _chat(self, text: str) -> None:
        conversation = self.query_one("#conversation", ConversationArea)
        cm = self.app.config_manager

        role_key, message_text = self._parse_mention(text)
        if role_key and role_key not in CM_ROLE_NAMES:
            conversation.add(f"[bold red]Error:[/] Unknown role '@{role_key}'")
            return
        display_text = message_text or text
        conversation.add(f"[bold #c0caf5]You:[/] {display_text}")

        context = SessionContext(
            session_id=str(uuid4()),
            task=Task(id=str(uuid4()), description=display_text),
            messages=[
                DomainMessage(
                    id=str(uuid4()),
                    sender="user",
                    content=display_text,
                ),
            ],
        )

        provider = LiteLLMProvider()
        agents = []

        def _build_agent(rk: str) -> Any:
            cfg_data = cm.get_role_config(rk) if cm else {}
            model = cfg_data.get("model", self.app.settings.default_model)
            system_prompt = cfg_data.get("system_prompt")
            agent_cfg = AgentConfig(
                role=Role(rk),
                name=rk.replace("_", " ").title(),
                model=model,
                system_prompt=system_prompt,
            )
            return AgentRegistry.create(rk, agent_cfg, provider)

        if role_key and role_key in CM_ROLE_NAMES:
            agents.append(_build_agent(role_key))
        else:
            for rk in self.app.TEAM_PIPELINE:
                agents.append(_build_agent(rk))

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

    def key_escape(self) -> None:
        if self.app.config_pending_action:
            self.app.config_pending_action = None
            self.query_one("#message-input", Input).placeholder = "Type your task..."
            self._focus()
            return
        if self.app.roles_pending_action:
            self.app.roles_pending_action = None
            self.query_one("#message-input", Input).placeholder = "Type your task..."
            self._focus()
            return
        if self.app.roles_mode:
            if self.app.roles_view == "edit":
                self.app.roles_view = "list"
                self.app.roles_editing_role = None
                from teamcode.ui.commands.roles import _build_role_list
                cm = self.app.config_manager
                if cm:
                    self.query_one("#conversation", ConversationArea).add(
                        _build_role_list(cm, self.app.roles_active_index)
                    )
            else:
                self.app.roles_mode = False
            self._focus()
            return
        if self.app.config_mode:
            self.app.config_mode = False
            self._focus()
            return
        palette = self.query_one("#slash-palette", SlashPalette)
        if palette.has_class("--visible"):
            palette._close()
            self._focus()
        else:
            self.app.action_quit()

    @on(CommandSelected)
    async def handle_slash_command(self, event: CommandSelected) -> None:
        await self._run_cmd(f"/{event.command_name}")
        self._focus()

    @on(SlashAutocomplete)
    def handle_slash_autocomplete(self, event: SlashAutocomplete) -> None:
        inp = self.query_one("#message-input", Input)
        inp.value = f"/{event.command_name} "
        inp.focus()

    @on(SlashPaletteClose)
    def handle_slash_palette_close(self, event: SlashPaletteClose) -> None:
        self._focus()

    # ── Config mode handlers ──

    def key_e(self) -> None:
        if not self.app.config_mode:
            return
        if self.app.config_pending_action:
            return
        cm = self.app.config_manager
        if cm is None:
            return
        inp = self.query_one("#message-input", Input)
        inp.placeholder = "Paste your OpenRouter API key..."
        inp.value = ""
        inp.focus()
        self.app.config_pending_action = "key"

    def key_f5(self) -> None:
        if not self.app.config_mode:
            return
        if self.app.config_pending_action:
            return
        cm = self.app.config_manager
        if cm is None:
            return
        conversation = self.query_one("#conversation", ConversationArea)
        conversation.add("[yellow]Testing connection...[/]")
        ok = cm.test_connection()
        if ok:
            conversation.add("[green]\u2713 Connected to OpenRouter[/]")
        else:
            conversation.add(
                "[bold red]Error:[/] Connection failed. Check your API key and network."
            )
        conversation.add(self._build_config_display())

    def key_d(self) -> None:
        if not self.app.config_mode:
            return
        if self.app.config_pending_action:
            return
        cm = self.app.config_manager
        if cm is None:
            return
        models = cm.get_cached_models()
        if not models:
            conversation = self.query_one("#conversation", ConversationArea)
            conversation.add("[yellow]No cached models — press r to fetch first[/]")
            return
        picker = self.query_one("#model-picker", ModelPicker)
        self._model_picker_target = "default"
        picker._models = models
        picker.open()

    def key_r(self) -> None:
        cm = self.app.config_manager
        if cm is None:
            return
        conversation = self.query_one("#conversation", ConversationArea)
        if self.app.config_mode and not self.app.config_pending_action:
            try:
                models = cm.refresh_models()
                conversation.add(f"[green]\u2713 Cached {len(models)} models from OpenRouter[/]")
            except ValueError as exc:
                conversation.add(f"[bold red]Error:[/] {exc}")
            except Exception as exc:
                conversation.add(f"[bold red]Error:[/] Failed to fetch models: {exc}")
            conversation.add(self._build_config_display())
            return
        if self.app.roles_mode:
            if self.app.roles_view == "edit" and self.app.roles_editing_role:
                role_name = self.app.roles_editing_role
                cm.reset_role(role_name)
                conversation.add(
                    f"[yellow]\u21ba {role_name.replace('_', ' ').title()} reset to default[/]"
                )
                from teamcode.ui.commands.roles import _build_role_edit
                conversation.add(_build_role_edit(cm, role_name))
            elif self.app.roles_view == "list":
                from teamcode.ui.commands.roles import ROLE_ORDER, _build_role_list
                idx = self.app.roles_active_index
                if 0 <= idx < len(ROLE_ORDER):
                    role_name = ROLE_ORDER[idx]
                    cm.reset_role(role_name)
                    conversation.add(
                        f"[yellow]\u21ba {role_name.replace('_', ' ').title()} reset to default[/]"
                    )
                    conversation.add(
                        _build_role_list(cm, self.app.roles_active_index)
                    )
            return

    @on(ModelSelected)
    def handle_model_selected(self, event: ModelSelected) -> None:
        cm = self.app.config_manager
        if cm is None:
            return
        model_id = event.model_id
        target = getattr(self, "_model_picker_target", "default")
        conversation = self.query_one("#conversation", ConversationArea)
        if target == "default":
            cm.set_default_model(model_id)
            conversation.add(f"[green]\u2713 Default model set to {model_id}[/]")
            conversation.add(self._build_config_display())
        elif target and target.startswith("role:"):
            role_name = target[5:]
            role_cfg = cm.get_role_config(role_name)
            role_cfg["model"] = model_id
            cm.set_role_config(role_name, role_cfg)
            label = role_name.replace("_", " ").title()
            conversation.add(f"[green]\u2713 {label} model set to {model_id}[/]")
            if self.app.roles_mode and self.app.roles_view == "edit":
                from teamcode.ui.commands.roles import _build_role_edit
                conversation.add(_build_role_edit(cm, role_name))
        self._focus()

    def _build_config_display(self) -> Any:
        from teamcode.ui.commands.config import _build_config_display as _bcd
        cm = self.app.config_manager
        return _bcd(cm) if cm else "[dim]Configuration unavailable[/]"

    # ── Roles mode handlers ──

    def key_up(self) -> None:
        if not self.app.roles_mode or self.app.roles_view != "list":
            return
        from teamcode.ui.commands.roles import _build_role_list
        cm = self.app.config_manager
        if not cm:
            return
        self.app.roles_active_index = max(0, self.app.roles_active_index - 1)
        self.query_one("#conversation", ConversationArea).add(
            _build_role_list(cm, self.app.roles_active_index, self.app.roles_editing_role)
        )

    def key_down(self) -> None:
        if not self.app.roles_mode or self.app.roles_view != "list":
            return
        from teamcode.ui.commands.roles import ROLE_ORDER, _build_role_list
        cm = self.app.config_manager
        if not cm:
            return
        count = len(ROLE_ORDER)
        self.app.roles_active_index = min(count - 1, self.app.roles_active_index + 1)
        self.query_one("#conversation", ConversationArea).add(
            _build_role_list(cm, self.app.roles_active_index, self.app.roles_editing_role)
        )

    def key_enter(self) -> None:
        if not self.app.roles_mode:
            return
        if self.app.roles_view == "edit":
            cm = self.app.config_manager
            if cm and self.app.roles_editing_role:
                label = self.app.roles_editing_role.replace("_", " ").title()
                self.query_one("#conversation", ConversationArea).add(
                    f"[green]\u2713 {label} saved[/]"
                )
            self.app.roles_view = "list"
            self.app.roles_editing_role = None
            self._focus()
            return
        if self.app.roles_view == "list":
            from teamcode.ui.commands.roles import ROLE_ORDER, _build_role_edit
            cm = self.app.config_manager
            if not cm:
                return
            idx = self.app.roles_active_index
            if 0 <= idx < len(ROLE_ORDER):
                role_name = ROLE_ORDER[idx]
                self.app.roles_view = "edit"
                self.app.roles_editing_role = role_name
                self.query_one("#conversation", ConversationArea).add(
                    _build_role_edit(cm, role_name)
                )

    def key_m(self) -> None:
        if not self.app.roles_mode or self.app.roles_view != "edit":
            return
        if not self.app.roles_editing_role:
            return
        cm = self.app.config_manager
        if cm is None:
            return
        models = cm.get_cached_models()
        if not models:
            self.query_one("#conversation", ConversationArea).add(
                "[yellow]No cached models — press r in /config to fetch first[/]"
            )
            return
        picker = self.query_one("#model-picker", ModelPicker)
        self._model_picker_target = f"role:{self.app.roles_editing_role}"
        picker._models = models
        picker.open()

    def key_p(self) -> None:
        if not self.app.roles_mode or self.app.roles_view != "edit":
            return
        if not self.app.roles_editing_role:
            return
        self._roles_editing_name = self.app.roles_editing_role
        self.app.roles_pending_action = "prompt"
        inp = self.query_one("#message-input", Input)
        inp.placeholder = "Enter new system prompt..."
        inp.value = ""
        inp.focus()

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
    config_manager: ConfigManager | None = None
    config_mode: bool = False
    config_pending_action: str | None = None
    roles_mode: bool = False
    roles_view: str = "list"
    roles_active_index: int = 0
    roles_editing_role: str | None = None
    roles_pending_action: str | None = None

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
        self.config_manager = ConfigManager(settings=self.settings)
        key = self.config_manager.get_api_key()
        if key:
            os.environ["OPENROUTER_API_KEY"] = key
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
