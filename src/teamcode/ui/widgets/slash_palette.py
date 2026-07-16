"""Codex-style slash command palette triggered by typing /."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Label, ListItem, ListView

from teamcode.ui.commands.registry import CommandRegistry


def _fuzzy_match(query: str, target: str) -> bool:
    """Sequential-character fuzzy match."""
    qi = 0
    qlen = len(query)
    if qlen == 0:
        return True
    for tc in target.lower():
        if qi < qlen and tc == query[qi]:
            qi += 1
    return qi == qlen


class CommandSelected(Message):
    def __init__(self, command_name: str) -> None:
        self.command_name = command_name
        super().__init__()


class SlashPalette(Widget):
    """Codex-style slash command palette triggered by typing /."""

    DEFAULT_CSS = """
    SlashPalette {
        layer: overlay;
        height: auto;
        max-height: 16;
        width: 60%;
        min-width: 40;
        margin: 0 2 2 2;
        background: #151922;
        border: solid #1e2a3e;
        display: none;
    }
    SlashPalette.--visible {
        display: block;
    }
    SlashPalette > Input {
        width: 1fr;
        border: none;
        background: #151922;
        color: #c0caf5;
        margin: 0 1;
    }
    SlashPalette > ListView {
        height: auto;
        max-height: 12;
        background: #151922;
    }
    SlashPalette ListItem {
        height: 1;
        padding: 0 1;
        background: #151922;
    }
    SlashPalette ListItem > Label:first-child {
        color: #00d4aa;
        width: 18;
    }
    SlashPalette ListItem > Label:last-child {
        color: #565f89;
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(id="slash-filter", placeholder="Type to filter commands...")
        yield ListView(id="slash-list")

    def on_mount(self) -> None:
        self._populate("")

    def _populate(self, filter_text: str) -> None:
        lv = self.query_one("#slash-list", ListView)
        lv.clear()
        for cmd_cls in sorted(
            CommandRegistry.all().values(),
            key=lambda c: c.name,
        ):
            if filter_text and not _fuzzy_match(
                filter_text, f"{cmd_cls.name} {cmd_cls.description}"
            ):
                continue
            item = ListItem(
                Label(f"/{cmd_cls.name}"),
                Label(cmd_cls.description[:60]),
            )
            item.command_name = cmd_cls.name
            lv.append(item)
        if lv.children:
            lv.index = 0

    @on(Input.Changed, "#slash-filter")
    def on_input_changed(self, event: Input.Changed) -> None:
        if not event.value.strip():
            self._close()
            self.post_message(SlashPaletteClose())
            return
        self._populate(event.value.strip())

    @on(Input.Submitted, "#slash-filter")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        lv = self.query_one("#slash-list", ListView)
        if lv.index is not None and lv.children:
            selected = lv.children[lv.index]
            name = getattr(selected, "command_name", None)
            if name:
                self.post_message(CommandSelected(name))
        self._close()

    @on(ListView.Selected, "#slash-list")
    def on_list_selected(self, event: ListView.Selected) -> None:
        if event.item:
            name = getattr(event.item, "command_name", None)
            if name:
                self.post_message(CommandSelected(name))
        self._close()

    def key_tab(self) -> None:
        lv = self.query_one("#slash-list", ListView)
        if lv.index is not None and lv.children:
            selected = lv.children[lv.index]
            name = getattr(selected, "command_name", None)
            if name:
                self.post_message(SlashAutocomplete(name))
        self._close()

    def key_escape(self) -> None:
        self._close()
        self.post_message(SlashPaletteClose())

    def _close(self) -> None:
        self.remove_class("--visible")
        self.query_one("#slash-filter", Input).value = ""

    def open(self, filter_text: str = "") -> None:
        self._populate(filter_text)
        self.add_class("--visible")
        inp = self.query_one("#slash-filter", Input)
        inp.value = filter_text
        inp.focus()


class SlashAutocomplete(Message):
    def __init__(self, command_name: str) -> None:
        self.command_name = command_name
        super().__init__()


class SlashPaletteClose(Message):
    pass
