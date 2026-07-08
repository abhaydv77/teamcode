from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from teamcode.ui.commands.registry import CommandRegistry


class CommandPalette(Widget):
    DEFAULT_CSS = """
    CommandPalette {
        dock: bottom;
        height: auto;
        max-height: 14;
        display: none;
        border: solid #0088ff;
        background: #0d1117;
        margin: 0 1;
    }

    #palette-header {
        height: 1;
        padding: 0 1;
        background: #0088ff;
        color: #0d1117;
        text-style: bold;
    }

    CommandPalette ListView {
        height: auto;
        max-height: 11;
        background: #0d1117;
    }

    CommandPalette ListItem {
        padding: 0 1;
        height: 1;
    }

    CommandPalette ListItem > Label {
        width: 1fr;
    }

    CommandPalette ListItem > Label.description {
        color: #565f89;
        width: 2fr;
    }

    CommandPalette ListItem.--highlight {
        background: #1e2a3e;
    }
    """

    query = reactive("")

    def compose(self) -> ComposeResult:
        yield Label("  COMMANDS", id="palette-header")
        yield ListView(id="command-list")

    def watch_query(self, query: str) -> None:
        if query.startswith("/"):
            remaining = query[1:]
            self.display = bool(remaining)
            if remaining:
                self._update_items(remaining)
            else:
                list_view = self.query_one("#command-list", ListView)
                list_view.clear()
                self.display = True
        else:
            self.display = False

    def _update_items(self, search: str) -> None:
        list_view = self.query_one("#command-list", ListView)
        list_view.clear()
        commands = CommandRegistry.search(search)
        for cmd_cls in commands:
            desc = cmd_cls.description[:50]
            item = ListItem(
                Label(f"/{cmd_cls.name}"),
                Label(f"  {desc}", classes="description"),
            )
            item.command_name = cmd_cls.name
            list_view.append(item)

        if list_view.children:
            list_view.index = 0

    @property
    def selected_command_name(self) -> str | None:
        list_view = self.query_one("#command-list", ListView)
        if list_view.index is not None and list_view.children:
            item = list_view.children[list_view.index]
            return getattr(item, "command_name", None)
        return None
