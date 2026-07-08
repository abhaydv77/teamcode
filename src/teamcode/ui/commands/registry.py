from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from teamcode.ui.commands.base import BaseCommand


class CommandRegistry:
    _commands: dict[str, type[BaseCommand]] = {}

    @classmethod
    def discover(cls) -> None:
        cls._commands.clear()
        from teamcode.ui.commands.base import BaseCommand
        package_dir = os.path.dirname(__file__)
        for module_info in pkgutil.iter_modules([package_dir]):
            name = module_info.name
            if name == "base" or name == "registry":
                continue
            module = importlib.import_module(f".{name}", package="teamcode.ui.commands")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseCommand) and obj is not BaseCommand:
                    cls._commands[obj.name] = obj

    @classmethod
    def register(cls, command_cls: type[BaseCommand]) -> None:
        cls._commands[command_cls.name] = command_cls

    @classmethod
    def get(cls, name: str) -> type[BaseCommand] | None:
        return cls._commands.get(name)

    @classmethod
    def all(cls) -> dict[str, type[BaseCommand]]:
        return dict(cls._commands)

    @classmethod
    def search(cls, query: str) -> list[type[BaseCommand]]:
        q = query.lower()
        matches = [
            cmd for name, cmd in cls._commands.items() if q in name or q in cmd.description.lower()
        ]
        return sorted(matches, key=lambda c: c.name)

    @classmethod
    def clear(cls) -> None:
        cls._commands.clear()
