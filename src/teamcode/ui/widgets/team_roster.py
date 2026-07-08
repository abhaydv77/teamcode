from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

STATUS_COLORS: dict[str, str] = {
    "idle": "#00d4aa",
    "ready": "#00d4aa",
    "thinking": "#0088ff",
    "planning": "#ffaa00",
    "coding": "#00d4aa",
    "reviewing": "#ffaa00",
    "offline": "#565f89",
    "writing": "#0088ff",
}

STATUS_INDICATORS: dict[str, str] = {
    "idle": "🟢",
    "ready": "🟢",
    "thinking": "🟡",
    "planning": "🟡",
    "coding": "🔵",
    "reviewing": "🟡",
    "offline": "⚪",
    "writing": "🔵",
}


class TeamRoster(Widget):
    DEFAULT_CSS = """
    TeamRoster {
        height: 1fr;
        background: #0d1117;
        border-right: solid #1e2a3e;
        padding: 0 1;
        overflow: auto;
    }

    TeamRoster > #roster-title {
        height: 1;
        padding: 0 1;
        text-style: bold;
        color: #565f89;
    }
    """

    def render(self) -> Text:
        app = self.app
        lines: list[Text] = []

        lines.append(Text(" TEAM ROSTER", style="bold #565f89"))
        lines.append(Text("─" * 28, style="#1e2a3e"))

        for key, info in app.agent_states.items():
            status = info.get("status", "offline")
            emoji = info.get("emoji", "  ")
            label = info.get("label", key)
            color = STATUS_COLORS.get(status, "#565f89")
            indicator = STATUS_INDICATORS.get(status, "⚪")

            line = Text.assemble(
                (f" {emoji} ", ""),
                (f"{label:<16}", "#c0caf5"),
                (f" {indicator}", ""),
                (f" {status:<10}", color),
            )
            lines.append(Text(""))
            lines.append(line)

        lines.append(Text(""))
        lines.append(Text("─" * 28, style="#1e2a3e"))

        result = Text("")
        for line in lines:
            result.append(line)
            result.append("\n")

        return result
