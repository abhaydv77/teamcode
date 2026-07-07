from __future__ import annotations

from teamcode.domain.task import Task, TaskStatus


class TaskQueue:
    def __init__(self) -> None:
        self._items: list[Task] = []

    def push(self, task: Task) -> None:
        task.status = TaskStatus.PENDING
        self._items.append(task)

    def pop(self) -> Task | None:
        for task in self._items:
            if task.status == TaskStatus.PENDING and self._deps_met(task):
                self._items.remove(task)
                return task
        return None

    def peek(self) -> Task | None:
        for task in self._items:
            if task.status == TaskStatus.PENDING and self._deps_met(task):
                return task
        return None

    def update(self, task_id: str, status: TaskStatus, result: str | None = None) -> None:
        for task in self._items:
            if task.id == task_id:
                task.status = status
                task.updated_at = __import__("datetime").datetime.utcnow()
                if result is not None:
                    task.result = result
                break

    def cancel(self, task_id: str) -> None:
        self._items[:] = [t for t in self._items if t.id != task_id]

    def clear(self) -> None:
        self._items.clear()

    def _deps_met(self, task: Task) -> bool:
        return all(
            any(t.id == dep and t.status == TaskStatus.COMPLETED for t in self._items)
            for dep in task.depends_on
        )

    @property
    def pending(self) -> list[Task]:
        return [t for t in self._items if t.status == TaskStatus.PENDING]

    @property
    def size(self) -> int:
        return len(self._items)
