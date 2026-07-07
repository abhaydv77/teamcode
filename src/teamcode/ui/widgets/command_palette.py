from __future__ import annotations

from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from teamcode.ui.commands.registry import CommandRegistry


class CommandPalette(Widget):
    DEFAULT_CSS = """
    CommandPalette {
        height: auto;
        max-height: 12;
        display: none;
        border: tall $secondary;
        background: $surface;
        margin: 0 1;
    }

    CommandPalette ListView {
        height: auto;
        max-height: 10;
    }

    CommandPalette ListItem {
        padding: 0 1;
    }

    CommandPalette ListItem > Label {
        width: 1fr;
    }

    CommandPalette ListItem > Label:last-child {
        color: $text-muted;
        width: 2fr;
    }

    CommandPalette ListItem.--highlight {
        background: $accent 20%;
    }
    """

    query = reactive("")

    def compose(self) -> list[ListView]:
        return [ListView(id="command-list")]

    def watch_query(self, query: str) -> None:
        if query.startswith("/"):
            remaining = query[1:]
            self.display = bool(remaining)
            if remaining:
                self._update_items(remaining)
            else:
                list_view = self.query_one("#command-list", ListView)
                list_view.clear()
        else:
            self.display = False

    def _update_items(self, search: str) -> None:
        list_view = self.query_one("#command-list", ListView)
        list_view.clear()
        commands = CommandRegistry.search(search)
        for cmd_cls in commands:
            item = ListItem(
                Label(f"[bold cyan]/{cmd_cls.name}[/]"),
                Label(f"  {cmd_cls.description}"),
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
