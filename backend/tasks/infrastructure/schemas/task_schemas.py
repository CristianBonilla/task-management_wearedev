from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

from ...domain.value_objects import TaskStatus
from ...shared.utils.datetime import utcnow


class TaskOutputSerializer(serializers.Serializer):

    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    status = serializers.SerializerMethodField()
    due_date = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    created_by = serializers.CharField()
    is_expiring = serializers.SerializerMethodField()

    def get_status(self, obj) -> str:
        return obj.status.value

    def get_is_expiring(self, obj) -> bool:
        window = int(getattr(settings, "EXPIRING_WINDOW_HOURS", 48))
        return obj.is_expiring(window_hours=window, now=utcnow())


class CreateTaskSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    status = serializers.ChoiceField(
        choices=TaskStatus.values(),
        required=False,
        default=TaskStatus.PENDIENTE.value,
    )
    due_date = serializers.DateTimeField(required=False, allow_null=True)


class UpdateTaskSerializer(serializers.Serializer):

    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=TaskStatus.values(), required=False)
    due_date = serializers.DateTimeField(required=False, allow_null=True)


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=TaskStatus.values())


class ExpiringQuerySerializer(serializers.Serializer):
    window_hours = serializers.IntegerField(required=False, min_value=1, max_value=8760)
