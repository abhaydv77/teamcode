from teamcode.domain.agent import AgentConfig, Role


class TestAgentConfig:
    def test_create_developer(self) -> None:
        config = AgentConfig(role=Role.DEVELOPER, name="dev-1")
        assert config.role == Role.DEVELOPER
        assert config.name == "dev-1"
        assert config.provider == "openai"
        assert config.model == "gpt-4o"

    def test_role_values(self) -> None:
        roles = {r.value for r in Role}
        expected = {
            "product_manager",
            "coordinator",
            "developer",
            "reviewer",
            "tester",
            "architect",
        }
        assert roles == expected
