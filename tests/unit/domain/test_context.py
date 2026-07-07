from teamcode.domain.context import SessionContext
from teamcode.domain.task import Task


class TestSessionContext:
    def test_create_context(self) -> None:
        task = Task(id="task-1", description="Build feature")
        ctx = SessionContext(session_id="session-1", task=task)
        assert ctx.session_id == "session-1"
        assert ctx.messages == []
        assert ctx.state == {}
