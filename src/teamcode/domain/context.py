from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from teamcode.domain.message import Message
from teamcode.domain.task import Task


class SessionContext(BaseModel):
    session_id: str
    task: Task
    messages: list[Message] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)
