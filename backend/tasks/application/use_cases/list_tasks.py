from __future__ import annotations

from ...domain.entities import Task
from ...domain.repositories import TaskRepository
from ...domain.value_objects import TaskStatus

class ListTasksUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, *, status: str | None = None) -> list[Task]:
        parsed_status = TaskStatus.from_value(status) if status else None
        return self._repository.list(status=parsed_status)
