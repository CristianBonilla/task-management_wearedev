from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from ...shared.utils.datetime import utcnow
from ..exceptions import TaskValidationError
from ..value_objects import TaskStatus

_TITLE_MAX_LENGTH = 200


@dataclass
class Task:

    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDIENTE
    due_date: datetime | None = None
    created_by: str = "system"

    id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    is_deleted: bool = False
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        self.title = (self.title or "").strip()
        self.description = (self.description or "").strip()
        if not isinstance(self.status, TaskStatus):
            self.status = TaskStatus.from_value(str(self.status))
        self._validate()

    def _validate(self) -> None:
        errors: dict[str, list[str]] = {}

        if not self.title:
            errors.setdefault("title", []).append("Title must not be empty.")
        elif len(self.title) > _TITLE_MAX_LENGTH:
            errors.setdefault("title", []).append(
                f"Title must be at most {_TITLE_MAX_LENGTH} characters."
            )

        if self.due_date is not None and self.due_date.tzinfo is None:
            errors.setdefault("due_date", []).append(
                "due_date must be timezone-aware."
            )

        if errors:
            raise TaskValidationError("The task is invalid.", errors=errors)

    def change_status(self, new_status: TaskStatus | str) -> None:
        self.status = (
            new_status
            if isinstance(new_status, TaskStatus)
            else TaskStatus.from_value(str(new_status))
        )

    def update_details(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        status: TaskStatus | str | None = None,
        _clear_due_date: bool = False,
    ) -> None:
        if title is not None:
            self.title = title.strip()
        if description is not None:
            self.description = description.strip()
        if _clear_due_date:
            self.due_date = None
        elif due_date is not None:
            self.due_date = due_date
        if status is not None:
            self.change_status(status)
        self._validate()

    def soft_delete(self, *, now: datetime | None = None) -> None:
        self.is_deleted = True
        self.deleted_at = now or utcnow()

    def is_expiring(self, *, window_hours: int, now: datetime | None = None) -> bool:
        if self.due_date is None or self.status == TaskStatus.COMPLETADA:
            return False
        reference = now or utcnow()
        return reference <= self.due_date <= reference + timedelta(hours=window_hours)
