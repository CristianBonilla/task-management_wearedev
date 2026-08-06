from __future__ import annotations

from uuid import UUID

from ...domain.entities import Task
from ...domain.repositories import TaskRepository
from ..dtos import ChangeStatusDTO

class ChangeTaskStatusUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, task_id: UUID, dto: ChangeStatusDTO) -> Task:
        task = self._repository.get_by_id(task_id)
        task.change_status(dto.status)
        return self._repository.update(task)
