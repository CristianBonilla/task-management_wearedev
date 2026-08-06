from __future__ import annotations

from django.conf import settings
from rest_framework.request import Request

def resolve_current_user(request: Request) -> str:
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return user.get_username()
    return str(getattr(settings, "DEFAULT_TASK_OWNER", "system"))
