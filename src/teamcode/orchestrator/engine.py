from __future__ import annotations

import logging
from datetime import datetime

from teamcode.agents.base import BaseAgent
from teamcode.domain.context import SessionContext
from teamcode.domain.message import Message
from teamcode.domain.task import TaskStatus
from teamcode.orchestrator.events import (
    AgentFinished,
    AgentStarted,
    EventBus,
    SessionEnded,
    SessionStarted,
)
from teamcode.orchestrator.router import AgentRouter
from teamcode.orchestrator.scheduler import TaskScheduler

log = logging.getLogger(__name__)


class Orchestrator:
    def __init__(
        self,
        agents: list[BaseAgent] | None = None,
        router: AgentRouter | None = None,
        scheduler: TaskScheduler | None = None,
    ) -> None:
        self.agents = agents or []
        self.router = router or AgentRouter()
        self.scheduler = scheduler or TaskScheduler()
        self.event_bus = EventBus()

    async def run(self, context: SessionContext) -> SessionContext:
        context.task.status = TaskStatus.IN_PROGRESS
        await self.event_bus.emit(SessionStarted(context=context, session_id=context.session_id))

        for agent in self.agents:
            await self.event_bus.emit(AgentStarted(agent_name=agent.config.name))

            response = await agent.execute(context)

            msg = Message(
                id=f"msg-{len(context.messages) + 1}",
                sender=agent.config.name,
                content=response.content,
                message_type="agent_response",
                timestamp=datetime.utcnow(),
            )
            context.messages.append(msg)
            context.state[agent.config.name] = response.content

            await self.event_bus.emit(
                AgentFinished(agent_name=agent.config.name, response=response)
            )

        routed = self.router.next_agent(context)
        if routed:
            log.debug("Router suggests next: %s", routed)

        next_task = self.scheduler.next_task(context)
        if next_task:
            context.task = next_task
            return await self.run(context)

        context.task.status = TaskStatus.COMPLETED
        context.task.updated_at = datetime.utcnow()
        await self.event_bus.emit(SessionEnded(context=context, session_id=context.session_id))
        return context
