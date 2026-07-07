from __future__ import annotations

import pytest

from teamcode.orchestrator.events import (
    AgentStarted,
    EventBus,
    TeamCodeEvent,
)


@pytest.mark.asyncio
async def test_event_bus() -> None:
    EventBus.clear()
    received: list[TeamCodeEvent] = []

    @EventBus.on(AgentStarted)
    async def handler(event: AgentStarted) -> None:
        received.append(event)

    await EventBus.emit(AgentStarted(agent_name="test-agent"))
    assert len(received) == 1
    assert received[0].agent_name == "test-agent"


@pytest.mark.asyncio
async def test_event_bus_unregistered_type() -> None:
    EventBus.clear()
    received: list[TeamCodeEvent] = []

    @EventBus.on(AgentStarted)
    async def handler(event: AgentStarted) -> None:
        received.append(event)

    await EventBus.emit(AgentStarted(agent_name="alpha"))
    await EventBus.emit(AgentStarted(agent_name="beta"))
    assert len(received) == 2


@pytest.mark.asyncio
async def test_event_bus_clear() -> None:
    EventBus.clear()
    received: list[TeamCodeEvent] = []

    @EventBus.on(AgentStarted)
    async def handler(event: AgentStarted) -> None:
        received.append(event)

    await EventBus.emit(AgentStarted(agent_name="a"))
    assert len(received) == 1

    EventBus.clear()
    await EventBus.emit(AgentStarted(agent_name="b"))
    assert len(received) == 1
