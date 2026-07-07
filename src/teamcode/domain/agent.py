from enum import StrEnum

from pydantic import BaseModel, Field


class Role(StrEnum):
    PRODUCT_MANAGER = "product_manager"
    COORDINATOR = "coordinator"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    ARCHITECT = "architect"


class AgentConfig(BaseModel):
    role: Role
    name: str
    provider: str = "openai"
    model: str = "gpt-4o"
    system_prompt: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
