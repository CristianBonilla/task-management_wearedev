from __future__ import annotations

from typing import Any
from uuid import UUID

class DomainError(Exception):

    status_code: int = 400
    error_type: str = "about:blank"
    title: str = "Domain Error"

    def __init__(self, detail: str, *, errors: dict[str, Any] | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        self.errors = errors or {}

class TaskValidationError(DomainError):

    status_code = 422
    error_type = "https://api.taskmanager/errors/validation"
    title = "Validation Error"

class InvalidTaskStatusError(DomainError):

    status_code = 422
    error_type = "https://api.taskmanager/errors/invalid-status"
    title = "Invalid Task Status"

    def __init__(self, value: str, allowed: list[str]) -> None:
        super().__init__(
            detail=f"'{value}' is not a valid status. Allowed values: {', '.join(allowed)}.",
            errors={"status": [f"Must be one of: {', '.join(allowed)}."]},
        )

class TaskNotFoundError(DomainError):

    status_code = 404
    error_type = "https://api.taskmanager/errors/not-found"
    title = "Task Not Found"

    def __init__(self, task_id: UUID | str) -> None:
        super().__init__(detail=f"Task with id '{task_id}' was not found.")
