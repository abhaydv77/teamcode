from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str
    sender: str
    recipient: str | None = None
    content: str
    message_type: str = "text"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)
