from __future__ import annotations

import logging
from typing import Any

from django.http import Http404
from rest_framework import status as http_status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from ..domain.exceptions import DomainError

logger = logging.getLogger(__name__)

PROBLEM_JSON_CONTENT_TYPE = "application/problem+json"
_DEFAULT_TYPE = "about:blank"

def _build_problem(
    *,
    status_code: int,
    title: str,
    detail: str,
    instance: str,
    error_type: str = _DEFAULT_TYPE,
    errors: dict[str, Any] | None = None,
) -> Response:
    body: dict[str, Any] = {
        "type": error_type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
    }
    if errors:
        body["errors"] = errors
    return Response(body, status=status_code, content_type=PROBLEM_JSON_CONTENT_TYPE)

def problem_details_handler(exc: Exception, context: dict[str, Any]) -> Response:
    request = context.get("request")
    instance = getattr(request, "path", "") if request else ""

    if isinstance(exc, DomainError):
        return _build_problem(
            status_code=exc.status_code,
            title=exc.title,
            detail=exc.detail,
            instance=instance,
            error_type=exc.error_type,
            errors=exc.errors or None,
        )

    if isinstance(exc, Http404):
        return _build_problem(
            status_code=http_status.HTTP_404_NOT_FOUND,
            title="Not Found",
            detail=str(exc) or "The requested resource was not found.",
            instance=instance,
        )

    if isinstance(exc, ValidationError):
        return _build_problem(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation Error",
            detail="One or more fields are invalid.",
            instance=instance,
            error_type="https://api.taskmanager/errors/validation",
            errors=exc.detail if isinstance(exc.detail, dict) else {"non_field_errors": exc.detail},
        )

    if isinstance(exc, APIException):
        detail = exc.detail
        return _build_problem(
            status_code=exc.status_code,
            title=exc.default_code.replace("_", " ").title(),
            detail=detail if isinstance(detail, str) else str(detail),
            instance=instance,
        )

    drf_response = drf_exception_handler(exc, context)
    if drf_response is not None:
        return drf_response

    logger.exception("Unhandled exception while processing request", exc_info=exc)
    return _build_problem(
        status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        title="Internal Server Error",
        detail="An unexpected error occurred.",
        instance=instance,
    )
