from teamcode.domain.task import Task, TaskStatus


class TestTask:
    def test_create_pending_task(self) -> None:
        task = Task(id="task-1", description="Write tests")
        assert task.status == TaskStatus.PENDING
        assert task.id == "task-1"
        assert task.depends_on == []
