from __future__ import annotations

from typing import Any
from uuid import UUID

from ...domain.entities import Task
from ...domain.repositories import TaskRepository
from ..dtos import UNSET, UpdateTaskDTO

class UpdateTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, task_id: UUID, dto: UpdateTaskDTO) -> Task:
        task = self._repository.get_by_id(task_id)

        changes: dict[str, Any] = {}
        if dto.title is not UNSET:
            changes["title"] = dto.title
        if dto.description is not UNSET:
            changes["description"] = dto.description
        if dto.status is not UNSET:
            changes["status"] = dto.status
        if dto.due_date is not UNSET:
            if dto.due_date is None:
                changes["_clear_due_date"] = True
            else:
                changes["due_date"] = dto.due_date

        task.update_details(**changes)
        return self._repository.update(task)
