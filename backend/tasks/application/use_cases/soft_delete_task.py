from __future__ import annotations

from uuid import UUID

from ...domain.repositories import TaskRepository

class SoftDeleteTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, task_id: UUID) -> None:
        task = self._repository.get_by_id(task_id)
        task.soft_delete()
        self._repository.update(task)
