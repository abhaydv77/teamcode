from __future__ import annotations

import logging

from teamcode.providers.base import BaseProvider, CompletionRequest, CompletionResponse

log = logging.getLogger(__name__)


class LiteLLMProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "litellm"

    @property
    def supported_models(self) -> list[str]:
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "gemini/gemini-1.5-pro",
            "gemini/gemini-1.5-flash",
            "groq/llama-3.1-70b-versatile",
            "mistral/mistral-large-latest",
            "deepseek/deepseek-coder",
            "openrouter/anthropic/claude-3.5-sonnet",
        ]

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        try:
            import litellm
        except ImportError:
            msg = (
                "LiteLLM is not installed. "
                "Run: pip install teamcode[litellm] or pip install litellm"
            )
            raise ImportError(msg) from None

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.extend(request.messages)

        response = await litellm.acompletion(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return CompletionResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=dict(response.usage) if response.usage else None,
        )

    async def complete_stream(self, request: CompletionRequest):
        try:
            import litellm
        except ImportError:
            msg = (
                "LiteLLM is not installed. "
                "Run: pip install teamcode[litellm] or pip install litellm"
            )
            raise ImportError(msg) from None

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.extend(request.messages)

        response = await litellm.acompletion(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )

        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
