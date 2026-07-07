from __future__ import annotations

from teamcode.domain.message import Message
from teamcode.memory.base import BaseMemory


class ConversationManager:
    def __init__(self, memory: BaseMemory | None = None) -> None:
        self._memory = memory

    async def add(self, message: Message) -> None:
        if self._memory:
            await self._memory.add(message)

    async def history(self, session_id: str) -> list[Message]:
        if self._memory:
            return await self._memory.get_context(session_id)
        return []

    def format_for_provider(self, messages: list[Message]) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for m in messages:
            role = "assistant" if m.message_type == "agent_response" else "user"
            result.append({"role": role, "content": m.content})
        return result

    def count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def trim(self, messages: list[Message], max_tokens: int = 8192) -> list[Message]:
        total = 0
        trimmed: list[Message] = []
        for m in reversed(messages):
            tokens = self.count_tokens(m.content)
            if total + tokens > max_tokens:
                break
            trimmed.insert(0, m)
            total += tokens
        return trimmed
