from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tasks.domain.entities import Task
from tasks.domain.exceptions import InvalidTaskStatusError, TaskValidationError
from tasks.domain.value_objects import TaskStatus

def _future(hours: int) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(hours=hours)

def test_task_defaults_to_pendiente() -> None:
    task = Task(title="Write report")
    assert task.status is TaskStatus.PENDIENTE
    assert task.is_deleted is False

def test_empty_title_is_rejected() -> None:
    with pytest.raises(TaskValidationError) as exc:
        Task(title="   ")
    assert "title" in exc.value.errors

def test_naive_due_date_is_rejected() -> None:
    with pytest.raises(TaskValidationError):
        Task(title="Task", due_date=datetime(2030, 1, 1))

def test_change_status_accepts_string() -> None:
    task = Task(title="Task")
    task.change_status("COMPLETADA")
    assert task.status is TaskStatus.COMPLETADA

def test_change_status_rejects_unknown_value() -> None:
    task = Task(title="Task")
    with pytest.raises(InvalidTaskStatusError):
        task.change_status("ARCHIVADA")

def test_soft_delete_sets_markers() -> None:
    task = Task(title="Task")
    task.soft_delete()
    assert task.is_deleted is True
    assert task.deleted_at is not None

def test_is_expiring_within_window() -> None:
    task = Task(title="Task", due_date=_future(24))
    assert task.is_expiring(window_hours=48) is True

def test_is_not_expiring_outside_window() -> None:
    task = Task(title="Task", due_date=_future(72))
    assert task.is_expiring(window_hours=48) is False

def test_completed_task_is_never_expiring() -> None:
    task = Task(title="Task", status=TaskStatus.COMPLETADA, due_date=_future(1))
    assert task.is_expiring(window_hours=48) is False

def test_update_details_revalidates() -> None:
    task = Task(title="Task")
    with pytest.raises(TaskValidationError):
        task.update_details(title="")
