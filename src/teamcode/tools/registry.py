from __future__ import annotations

from teamcode.tools.base import BaseTool


class ToolRegistry:
    _tools: dict[str, type[BaseTool]] = {}

    @classmethod
    def register(cls, name: str, tool_cls: type[BaseTool]) -> None:
        cls._tools[name] = tool_cls

    @classmethod
    def get(cls, name: str) -> type[BaseTool]:
        if name not in cls._tools:
            msg = f"Unknown tool: '{name}'. Available: {list(cls._tools)}"
            raise KeyError(msg)
        return cls._tools[name]

    @classmethod
    def all_tools(cls) -> list[str]:
        return list(cls._tools)

    @classmethod
    def clear(cls) -> None:
        cls._tools.clear()
