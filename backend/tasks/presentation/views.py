from __future__ import annotations

from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from ..application.dtos import UNSET, ChangeStatusDTO, CreateTaskDTO, UpdateTaskDTO
from ..infrastructure.schemas import (
    ChangeStatusSerializer,
    CreateTaskSerializer,
    ExpiringQuerySerializer,
    TaskOutputSerializer,
    UpdateTaskSerializer,
)
from .container import Container
from .identity import resolve_current_user

class TaskViewSet(viewsets.ViewSet):

    lookup_value_regex = "[0-9a-f-]{36}"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.container = Container()

    def list(self, request: Request) -> Response:
        status_filter = request.query_params.get("status")
        tasks = self.container.list_tasks().execute(status=status_filter)
        return Response(TaskOutputSerializer(tasks, many=True).data)

    def create(self, request: Request) -> Response:
        serializer = CreateTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        dto = CreateTaskDTO(
            title=data["title"],
            description=data.get("description", ""),
            status=data["status"],
            due_date=data.get("due_date"),
            created_by=resolve_current_user(request),
        )
        task = self.container.create_task().execute(dto)
        return Response(TaskOutputSerializer(task).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request: Request, pk: str) -> Response:
        task = self.container.get_task().execute(UUID(pk))
        return Response(TaskOutputSerializer(task).data)

    def partial_update(self, request: Request, pk: str) -> Response:
        serializer = UpdateTaskSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        dto = UpdateTaskDTO(
            title=data["title"] if "title" in data else UNSET,
            description=data["description"] if "description" in data else UNSET,
            status=data["status"] if "status" in data else UNSET,
            due_date=data["due_date"] if "due_date" in data else UNSET,
        )
        task = self.container.update_task().execute(UUID(pk), dto)
        return Response(TaskOutputSerializer(task).data)

    def destroy(self, request: Request, pk: str) -> Response:
        self.container.soft_delete_task().execute(UUID(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="status")
    def change_status(self, request: Request, pk: str) -> Response:
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto = ChangeStatusDTO(status=serializer.validated_data["status"])
        task = self.container.change_status().execute(UUID(pk), dto)
        return Response(TaskOutputSerializer(task).data)

    @action(detail=False, methods=["get"])
    def expiring(self, request: Request) -> Response:
        query = ExpiringQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        window = query.validated_data.get("window_hours")
        tasks = self.container.get_expiring_tasks().execute(window_hours=window)
        return Response(TaskOutputSerializer(tasks, many=True).data)
