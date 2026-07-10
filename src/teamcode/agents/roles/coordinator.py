from teamcode.agents.base import BaseAgent
from teamcode.agents.registry import AgentRegistry
from teamcode.domain.context import SessionContext
from teamcode.providers.base import CompletionResponse


class CoordinatorAgent(BaseAgent):
    async def execute(self, context: SessionContext) -> CompletionResponse:
        return await self.provider.complete(self.build_request(context))


AgentRegistry.register("coordinator", CoordinatorAgent)
