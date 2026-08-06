from __future__ import annotations

from datetime import datetime, timezone

from ...domain.entities import Task
from ...domain.repositories import TaskRepository

class GetExpiringTasksUseCase:
    def __init__(self, repository: TaskRepository, *, default_window_hours: int = 48) -> None:
        self._repository = repository
        self._default_window_hours = default_window_hours

    def execute(self, *, window_hours: int | None = None) -> list[Task]:
        window = window_hours if window_hours is not None else self._default_window_hours
        now = datetime.now(tz=timezone.utc)
        return self._repository.list_expiring(window_hours=window, now=now)
