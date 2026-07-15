"""Searchable model picker widget for selecting AI models."""

from __future__ import annotations

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Label, ListItem, ListView


class ModelSelected(Message):
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        super().__init__()


class ModelPicker(Widget):
    """Overlay widget for searching and selecting AI models."""

    DEFAULT_CSS = """
    ModelPicker {
        layer: overlay;
        height: auto;
        max-height: 20;
        width: 70%;
        min-width: 50;
        margin: 1 2;
        background: #151922;
        border: solid #1e2a3e;
        display: none;
    }
    ModelPicker.--visible {
        display: block;
    }
    ModelPicker > Input {
        width: 1fr;
        border: none;
        background: #151922;
        color: #c0caf5;
        margin: 0 1;
    }
    ModelPicker > ListView {
        height: auto;
        max-height: 16;
        background: #151922;
    }
    ModelPicker ListItem {
        height: 1;
        padding: 0 1;
        background: #151922;
    }
    ModelPicker ListItem > Label:first-child {
        color: #00d4aa;
        width: 1fr;
    }
    ModelPicker ListItem > Label:last-child {
        color: #565f89;
        width: auto;
    }
    """

    def __init__(self, models: list[dict[str, Any]], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._models = models

    def compose(self) -> ComposeResult:
        yield Input(id="picker-input", placeholder="Type to filter models...")
        yield ListView(id="picker-list")

    def on_mount(self) -> None:
        self._populate("")
        self.query_one("#picker-input", Input).focus()

    def _populate(self, filter_text: str) -> None:
        lv = self.query_one("#picker-list", ListView)
        lv.clear()
        filter_lower = filter_text.lower()
        for m in self._models:
            mid = m.get("id", "")
            name = m.get("name", "")
            ctx = m.get("context_length", 0)
            suffix = f"  {ctx // 1000}k ctx" if ctx else ""
            if filter_text:
                if filter_lower not in mid.lower() and filter_lower not in name.lower():
                    continue
            item = ListItem(
                Label(mid),
                Label(f"{name}{suffix}"),
            )
            item.model_id = mid
            lv.append(item)
        if lv.children:
            lv.index = 0

    @on(Input.Changed, "#picker-input")
    def on_input_changed(self, event: Input.Changed) -> None:
        self._populate(event.value.strip())

    @on(Input.Submitted, "#picker-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        lv = self.query_one("#picker-list", ListView)
        if lv.index is not None and lv.children:
            selected = lv.children[lv.index]
            mid = getattr(selected, "model_id", None)
            if mid:
                self.post_message(ModelSelected(mid))
        self._close()

    @on(ListView.Selected, "#picker-list")
    def on_list_selected(self, event: ListView.Selected) -> None:
        if event.item:
            mid = getattr(event.item, "model_id", None)
            if mid:
                self.post_message(ModelSelected(mid))
        self._close()

    def _close(self) -> None:
        self.remove_class("--visible")
        self.query_one("#picker-input", Input).value = ""

    def open(self) -> None:
        self._populate("")
        self.add_class("--visible")
        self.query_one("#picker-input", Input).focus()
