from __future__ import annotations

from teamcode.domain.context import SessionContext
from teamcode.domain.task import Task, TaskStatus


class TaskScheduler:
    _queue: list[Task] = []

    def enqueue(self, task: Task) -> None:
        task.status = TaskStatus.PENDING
        self._queue.append(task)

    def next_task(self, context: SessionContext) -> Task | None:
        for task in self._queue:
            if task.status == TaskStatus.PENDING:
                all_deps_met = all(
                    any(t.id == dep and t.status == TaskStatus.COMPLETED for t in self._queue)
                    for dep in task.depends_on
                )
                if not task.depends_on or all_deps_met:
                    return task
        return None

    def clear(self) -> None:
        self._queue.clear()
