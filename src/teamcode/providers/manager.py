from __future__ import annotations

import asyncio
import logging

from teamcode.config.settings import TeamCodeSettings
from teamcode.providers.base import BaseProvider, CompletionRequest, CompletionResponse
from teamcode.providers.litellm import LiteLLMProvider
from teamcode.providers.registry import ProviderRegistry

log = logging.getLogger(__name__)


class ProviderManager:
    def __init__(self, settings: TeamCodeSettings) -> None:
        self._settings = settings
        self._default = LiteLLMProvider()
        ProviderRegistry.register("litellm", LiteLLMProvider)

    async def complete(
        self,
        request: CompletionRequest,
        max_retries: int = 3,
    ) -> CompletionResponse:
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                return await self._default.complete(request)
            except Exception as exc:
                last_error = exc
                log.warning(
                    "Provider call failed (attempt %d/%d): %s",
                    attempt + 1,
                    max_retries,
                    exc,
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)

        raise last_error  # type: ignore[misc]

    def get_provider(self, name: str = "litellm") -> BaseProvider:
        if name == "litellm":
            return self._default
        provider_cls = ProviderRegistry.get(name)
        return provider_cls()
