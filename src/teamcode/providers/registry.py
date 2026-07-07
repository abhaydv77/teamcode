from __future__ import annotations

from teamcode.providers.base import BaseProvider


class ProviderRegistry:
    _providers: dict[str, type[BaseProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: type[BaseProvider]) -> None:
        cls._providers[name] = provider_cls

    @classmethod
    def get(cls, name: str) -> type[BaseProvider]:
        if name not in cls._providers:
            msg = f"Unknown provider: {name}. Available: {list(cls._providers)}"
            raise KeyError(msg)
        return cls._providers[name]

    @classmethod
    def list_providers(cls) -> list[str]:
        return list(cls._providers)

    @classmethod
    def clear(cls) -> None:
        cls._providers.clear()
