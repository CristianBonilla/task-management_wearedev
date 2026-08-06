from __future__ import annotations

from ...domain.entities import Task
from ...domain.repositories import TaskRepository
from ...domain.value_objects import TaskStatus
from ..dtos import CreateTaskDTO

class CreateTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, dto: CreateTaskDTO) -> Task:
        task = Task(
            title=dto.title,
            description=dto.description,
            status=TaskStatus.from_value(dto.status),
            due_date=dto.due_date,
            created_by=dto.created_by,
        )
        return self._repository.add(task)
