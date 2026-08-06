from __future__ import annotations

import uuid

from django.db import models

from ...domain.value_objects import TaskStatus


class TaskQuerySet(models.QuerySet):
    def alive(self) -> "TaskQuerySet":
        return self.filter(is_deleted=False)

    def deleted(self) -> "TaskQuerySet":
        return self.filter(is_deleted=True)


class AliveTaskManager(models.Manager):

    def get_queryset(self) -> TaskQuerySet:
        return TaskQuerySet(self.model, using=self._db).filter(is_deleted=False)


class TaskModel(models.Model):
    STATUS_CHOICES = [(status.value, status.value) for status in TaskStatus]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=TaskStatus.PENDIENTE.value,
    )
    due_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=150, default="system")

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = AliveTaskManager()
    all_objects = models.Manager.from_queryset(TaskQuerySet)()

    class Meta:
        app_label = "tasks"
        db_table = "tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"
