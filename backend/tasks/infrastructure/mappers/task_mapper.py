from __future__ import annotations

from ...domain.entities import Task
from ...domain.value_objects import TaskStatus
from ..models import TaskModel


class TaskMapper:
    @staticmethod
    def to_domain(model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status),
            due_date=model.due_date,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def apply_to_model(entity: Task, model: TaskModel) -> TaskModel:
        model.title = entity.title
        model.description = entity.description
        model.status = entity.status.value
        model.due_date = entity.due_date
        model.created_by = entity.created_by
        model.is_deleted = entity.is_deleted
        model.deleted_at = entity.deleted_at
        return model
