from __future__ import annotations

import pytest

from teamcode.providers.base import BaseProvider, CompletionRequest, CompletionResponse
from teamcode.providers.registry import ProviderRegistry


class TestProviderRegistry:
    def test_register_and_get(self) -> None:
        ProviderRegistry.clear()

        class FakeProvider(BaseProvider):
            @property
            def name(self) -> str:
                return "fake"

            @property
            def supported_models(self) -> list[str]:
                return ["fake-model"]

            async def complete(self, request: CompletionRequest) -> CompletionResponse: ...

        ProviderRegistry.register("fake", FakeProvider)
        cls = ProviderRegistry.get("fake")
        assert cls is FakeProvider

    def test_get_unknown_raises(self) -> None:
        ProviderRegistry.clear()
        with pytest.raises(KeyError, match="Unknown provider"):
            ProviderRegistry.get("nonexistent")
