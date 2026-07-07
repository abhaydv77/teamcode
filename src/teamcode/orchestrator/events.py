from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from teamcode.domain.context import SessionContext
    from teamcode.providers.base import CompletionResponse

EventHandler = Callable[..., Coroutine[Any, Any, None]]


class TeamCodeEvent:
    """Base class for all typed events."""

    pass


@dataclass
class SessionStarted(TeamCodeEvent):
    context: SessionContext | None = None
    session_id: str = ""


@dataclass
class SessionEnded(TeamCodeEvent):
    context: SessionContext | None = None
    session_id: str = ""


@dataclass
class AgentStarted(TeamCodeEvent):
    agent_name: str = ""


@dataclass
class AgentFinished(TeamCodeEvent):
    agent_name: str = ""
    response: CompletionResponse | None = None


@dataclass
class ToolStarted(TeamCodeEvent):
    tool_name: str = ""
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolFinished(TeamCodeEvent):
    tool_name: str = ""
    result: Any = None


@dataclass
class TaskCreated(TeamCodeEvent):
    task_id: str = ""
    description: str = ""


@dataclass
class TaskCompleted(TeamCodeEvent):
    task_id: str = ""
    result: str = ""


class EventBus:
    _handlers: dict[type[TeamCodeEvent], list[EventHandler]] = {}

    @classmethod
    def on(cls, event_type: type[TeamCodeEvent]) -> Callable[[EventHandler], EventHandler]:
        def decorator(handler: EventHandler) -> EventHandler:
            cls._handlers.setdefault(event_type, []).append(handler)
            return handler

        return decorator

    @classmethod
    async def emit(cls, event: TeamCodeEvent) -> None:
        handlers = cls._handlers.get(type(event), [])
        for handler in handlers:
            await handler(event)

    @classmethod
    def clear(cls) -> None:
        cls._handlers.clear()
