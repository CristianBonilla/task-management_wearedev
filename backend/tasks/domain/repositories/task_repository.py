from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from ..entities import Task
from ..value_objects import TaskStatus


class TaskRepository(ABC):

    @abstractmethod
    def add(self, task: Task) -> Task:
        ...

    @abstractmethod
    def get_by_id(self, task_id: UUID) -> Task:
        ...

    @abstractmethod
    def list(self, *, status: TaskStatus | None = None) -> list[Task]:
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        ...

    @abstractmethod
    def list_expiring(self, *, window_hours: int, now: datetime) -> list[Task]:
        ...
