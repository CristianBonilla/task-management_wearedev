from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from ...domain.entities import Task
from ...domain.exceptions import TaskNotFoundError
from ...domain.repositories import TaskRepository
from ...domain.value_objects import TaskStatus
from ..mappers import TaskMapper
from ..models import TaskModel


class DjangoTaskRepository(TaskRepository):
    def add(self, task: Task) -> Task:
        model = TaskMapper.apply_to_model(task, TaskModel())
        if task.id is not None:
            model.id = task.id
        model.save()
        return TaskMapper.to_domain(model)

    def get_by_id(self, task_id: UUID) -> Task:
        model = TaskModel.objects.filter(pk=task_id).first()
        if model is None:
            raise TaskNotFoundError(task_id)
        return TaskMapper.to_domain(model)

    def list(self, *, status: TaskStatus | None = None) -> list[Task]:
        queryset = TaskModel.objects.all()
        if status is not None:
            queryset = queryset.filter(status=status.value)
        return [TaskMapper.to_domain(model) for model in queryset]

    def update(self, task: Task) -> Task:
        if task.id is None:
            raise TaskNotFoundError("None")
        model = TaskModel.all_objects.filter(pk=task.id).first()
        if model is None:
            raise TaskNotFoundError(task.id)
        TaskMapper.apply_to_model(task, model)
        model.save()
        return TaskMapper.to_domain(model)

    def list_expiring(self, *, window_hours: int, now: datetime) -> list[Task]:
        upper_bound = now + timedelta(hours=window_hours)
        queryset = (
            TaskModel.objects.filter(
                due_date__gte=now,
                due_date__lte=upper_bound,
            )
            .exclude(status=TaskStatus.COMPLETADA.value)
            .order_by("due_date")
        )
        return [TaskMapper.to_domain(model) for model in queryset]
