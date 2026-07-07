from __future__ import annotations

import logging

from teamcode.domain.message import Message
from teamcode.memory.base import BaseMemory

log = logging.getLogger(__name__)


class SQLiteMemory(BaseMemory):
    async def add(self, message: Message) -> None:
        log.debug("SQLiteMemory.add: %s", message.id)

    async def get_context(self, session_id: str) -> list[Message]:
        log.debug("SQLiteMemory.get_context: %s", session_id)
        return []

    async def clear(self, session_id: str) -> None:
        log.debug("SQLiteMemory.clear: %s", session_id)
