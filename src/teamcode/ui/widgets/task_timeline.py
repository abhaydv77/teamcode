from __future__ import annotations

from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog


class TaskTimeline(Widget):
    DEFAULT_CSS = """
    TaskTimeline {
        height: 1fr;
        background: #0d1117;
        padding: 0 1;
    }

    TaskTimeline > RichLog {
        height: 1fr;
        background: #0d1117;
    }
    """

    def compose(self) -> ComposeResult:
        return [
            RichLog(id="timeline-log", highlight=True, markup=True, wrap=True, min_width=40),
        ]

    def on_mount(self) -> None:
        log = self.query_one("#timeline-log", RichLog)
        self._write_welcome(log)

    def add_message(self, content: Any) -> None:
        log = self.query_one("#timeline-log", RichLog)
        log.write(content)

    def add_timeline_entry(self, agent_emoji: str, agent_name: str, message: str, status: str = "") -> None:
        log = self.query_one("#timeline-log", RichLog)
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        entry = Text.assemble(
            (f"[{ts}] ", "dim #565f89"),
            (f"{agent_emoji} ", ""),
            (f"{agent_name} ", "bold #c0caf5"),
            ("→ ", "dim #565f89"),
            (message, "#c0caf5"),
        )
        log.write(entry)

    def add_progress(self, label: str, current: int, total: int, width: int = 30) -> None:
        log = self.query_one("#timeline-log", RichLog)
        pct = (current / total * 100) if total > 0 else 0
        filled = int(width * current / total) if total > 0 else 0
        empty = width - filled

        bar = Text.assemble(
            ("  ", ""),
            ("▓" * filled, "#00d4aa"),
            ("░" * empty, "#1e2a3e"),
            (f" {current}/{total} ({pct:.0f}%)", "#565f89"),
            (f"  {label}", "#c0caf5"),
        )
        log.write(bar)

    def clear(self) -> None:
        log = self.query_one("#timeline-log", RichLog)
        log.clear()

    def _write_welcome(self, log: RichLog) -> None:
        log.write(
            Text.assemble(
                ("TEAMCODE ", "bold #00d4aa"),
                ("Mission Control", "dim #565f89"),
            )
        )
        log.write(
            Text("Terminal-first AI software engineering team", "italic #565f89"),
        )
        log.write("")
        log.write(
            Text.assemble(
                "Type ",
                ("/help", "bold #0088ff"),
                (" to see available commands. ", ""),
                ("/session start", "bold #00d4aa"),
                (" to begin a session.", ""),
            )
        )
        log.write("")
