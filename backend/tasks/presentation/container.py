from __future__ import annotations

from django.conf import settings

from ..application.use_cases.change_status import ChangeTaskStatusUseCase
from ..application.use_cases.create_task import CreateTaskUseCase
from ..application.use_cases.get_expiring_tasks import GetExpiringTasksUseCase
from ..application.use_cases.get_task import GetTaskUseCase
from ..application.use_cases.list_tasks import ListTasksUseCase
from ..application.use_cases.soft_delete_task import SoftDeleteTaskUseCase
from ..application.use_cases.update_task import UpdateTaskUseCase
from ..domain.repositories import TaskRepository
from ..infrastructure.repositories import DjangoTaskRepository

class Container:

    def __init__(self, repository: TaskRepository | None = None) -> None:
        self._repository = repository or DjangoTaskRepository()

    @property
    def repository(self) -> TaskRepository:
        return self._repository

    def create_task(self) -> CreateTaskUseCase:
        return CreateTaskUseCase(self._repository)

    def update_task(self) -> UpdateTaskUseCase:
        return UpdateTaskUseCase(self._repository)

    def get_task(self) -> GetTaskUseCase:
        return GetTaskUseCase(self._repository)

    def list_tasks(self) -> ListTasksUseCase:
        return ListTasksUseCase(self._repository)

    def soft_delete_task(self) -> SoftDeleteTaskUseCase:
        return SoftDeleteTaskUseCase(self._repository)

    def change_status(self) -> ChangeTaskStatusUseCase:
        return ChangeTaskStatusUseCase(self._repository)

    def get_expiring_tasks(self) -> GetExpiringTasksUseCase:
        return GetExpiringTasksUseCase(
            self._repository,
            default_window_hours=int(getattr(settings, "EXPIRING_WINDOW_HOURS", 48)),
        )
