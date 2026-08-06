from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

UNSET: Final = object()


@dataclass(frozen=True, slots=True)
class CreateTaskDTO:
    title: str
    description: str
    status: str
    due_date: datetime | None
    created_by: str


@dataclass(frozen=True, slots=True)
class UpdateTaskDTO:

    title: str | object = UNSET
    description: str | object = UNSET
    status: str | object = UNSET
    due_date: datetime | None | object = UNSET


@dataclass(frozen=True, slots=True)
class ChangeStatusDTO:
    status: str
