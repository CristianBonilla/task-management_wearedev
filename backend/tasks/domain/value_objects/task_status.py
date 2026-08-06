from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):

    PENDIENTE = "PENDIENTE"
    COMPLETADA = "COMPLETADA"
    POSPUESTA = "POSPUESTA"

    @classmethod
    def from_value(cls, value: str) -> "TaskStatus":
        from ..exceptions import InvalidTaskStatusError

        try:
            return cls(value)
        except ValueError as exc:
            raise InvalidTaskStatusError(value, cls.values()) from exc

    @classmethod
    def values(cls) -> list[str]:
        return [status.value for status in cls]
