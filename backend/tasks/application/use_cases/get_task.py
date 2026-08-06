from __future__ import annotations

from uuid import UUID

from ...domain.entities import Task
from ...domain.repositories import TaskRepository

class GetTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, task_id: UUID) -> Task:
        return self._repository.get_by_id(task_id)
