from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from tasks.application.dtos import ChangeStatusDTO, CreateTaskDTO, UpdateTaskDTO
from tasks.application.use_cases.change_status import ChangeTaskStatusUseCase
from tasks.application.use_cases.create_task import CreateTaskUseCase
from tasks.application.use_cases.get_expiring_tasks import GetExpiringTasksUseCase
from tasks.application.use_cases.list_tasks import ListTasksUseCase
from tasks.application.use_cases.soft_delete_task import SoftDeleteTaskUseCase
from tasks.application.use_cases.update_task import UpdateTaskUseCase
from tasks.domain.entities import Task
from tasks.domain.exceptions import TaskNotFoundError
from tasks.domain.repositories import TaskRepository
from tasks.domain.value_objects import TaskStatus

class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Task] = {}

    def add(self, task: Task) -> Task:
        task.id = task.id or uuid4()
        task.created_at = datetime.now(tz=timezone.utc)
        task.updated_at = task.created_at
        self._store[task.id] = task
        return task

    def get_by_id(self, task_id: UUID) -> Task:
        task = self._store.get(task_id)
        if task is None or task.is_deleted:
            raise TaskNotFoundError(task_id)
        return task

    def list(self, *, status: TaskStatus | None = None) -> list[Task]:
        tasks = [t for t in self._store.values() if not t.is_deleted]
        if status is not None:
            tasks = [t for t in tasks if t.status is status]
        return tasks

    def update(self, task: Task) -> Task:
        task.updated_at = datetime.now(tz=timezone.utc)
        self._store[task.id] = task
        return task

    def list_expiring(self, *, window_hours: int, now: datetime) -> list[Task]:
        upper = now + timedelta(hours=window_hours)
        return [
            t
            for t in self._store.values()
            if not t.is_deleted
            and t.status is not TaskStatus.COMPLETADA
            and t.due_date is not None
            and now <= t.due_date <= upper
        ]

@pytest.fixture
def repo() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()

def test_create_task(repo: InMemoryTaskRepository) -> None:
    dto = CreateTaskDTO(
        title="New task",
        description="desc",
        status=TaskStatus.PENDIENTE.value,
        due_date=None,
        created_by="tester",
    )
    task = CreateTaskUseCase(repo).execute(dto)
    assert task.id is not None
    assert task.created_by == "tester"

def test_update_task_partial(repo: InMemoryTaskRepository) -> None:
    created = CreateTaskUseCase(repo).execute(
        CreateTaskDTO("Old", "", TaskStatus.PENDIENTE.value, None, "tester")
    )
    updated = UpdateTaskUseCase(repo).execute(
        created.id, UpdateTaskDTO(title="Renamed")
    )
    assert updated.title == "Renamed"
    assert updated.status is TaskStatus.PENDIENTE

def test_change_status(repo: InMemoryTaskRepository) -> None:
    created = CreateTaskUseCase(repo).execute(
        CreateTaskDTO("Task", "", TaskStatus.PENDIENTE.value, None, "tester")
    )
    updated = ChangeTaskStatusUseCase(repo).execute(
        created.id, ChangeStatusDTO(status=TaskStatus.COMPLETADA.value)
    )
    assert updated.status is TaskStatus.COMPLETADA

def test_soft_delete_hides_task(repo: InMemoryTaskRepository) -> None:
    created = CreateTaskUseCase(repo).execute(
        CreateTaskDTO("Task", "", TaskStatus.PENDIENTE.value, None, "tester")
    )
    SoftDeleteTaskUseCase(repo).execute(created.id)
    assert ListTasksUseCase(repo).execute() == []
    with pytest.raises(TaskNotFoundError):
        repo.get_by_id(created.id)

def test_list_filters_by_status(repo: InMemoryTaskRepository) -> None:
    CreateTaskUseCase(repo).execute(
        CreateTaskDTO("A", "", TaskStatus.PENDIENTE.value, None, "t")
    )
    CreateTaskUseCase(repo).execute(
        CreateTaskDTO("B", "", TaskStatus.COMPLETADA.value, None, "t")
    )
    pendientes = ListTasksUseCase(repo).execute(status=TaskStatus.PENDIENTE.value)
    assert len(pendientes) == 1
    assert pendientes[0].title == "A"

def test_expiring_uses_window(repo: InMemoryTaskRepository) -> None:
    now = datetime.now(tz=timezone.utc)
    CreateTaskUseCase(repo).execute(
        CreateTaskDTO("Soon", "", TaskStatus.PENDIENTE.value, now + timedelta(hours=10), "t")
    )
    CreateTaskUseCase(repo).execute(
        CreateTaskDTO("Later", "", TaskStatus.PENDIENTE.value, now + timedelta(hours=100), "t")
    )
    expiring = GetExpiringTasksUseCase(repo, default_window_hours=48).execute()
    assert [t.title for t in expiring] == ["Soon"]
