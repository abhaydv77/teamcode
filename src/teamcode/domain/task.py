from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class Task(BaseModel):
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    result: str | None = None
    artifacts: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
