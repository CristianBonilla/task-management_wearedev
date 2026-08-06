from __future__ import annotations

from ...domain.entities import Task
from ...domain.repositories import TaskRepository
from ...shared.utils.datetime import utcnow

class GetExpiringTasksUseCase:
    def __init__(self, repository: TaskRepository, *, default_window_hours: int = 48) -> None:
        self._repository = repository
        self._default_window_hours = default_window_hours

    def execute(self, *, window_hours: int | None = None) -> list[Task]:
        window = window_hours if window_hours is not None else self._default_window_hours
        return self._repository.list_expiring(window_hours=window, now=utcnow())
