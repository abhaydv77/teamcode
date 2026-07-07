from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from teamcode.plugins.base import BasePlugin


class PluginRegistry:
    _plugins: dict[str, BasePlugin] = {}

    @classmethod
    def register(cls, plugin: BasePlugin) -> None:
        cls._plugins[plugin.name] = plugin

    @classmethod
    def get(cls, name: str) -> BasePlugin | None:
        return cls._plugins.get(name)

    @classmethod
    def all(cls) -> dict[str, BasePlugin]:
        return dict(cls._plugins)

    @classmethod
    def clear(cls) -> None:
        cls._plugins.clear()
