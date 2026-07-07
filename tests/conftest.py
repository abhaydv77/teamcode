from __future__ import annotations

import pytest

from teamcode.domain.agent import AgentConfig, Role


@pytest.fixture
def agent_config() -> AgentConfig:
    return AgentConfig(
        role=Role.DEVELOPER,
        name="test-developer",
        provider="openai",
        model="gpt-4o",
    )
