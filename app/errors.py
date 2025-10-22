from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class ProblemDetailException(HTTPException):
    """Исключение с деталями проблемы в формате RFC 7807"""

    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str,
        error_type: str = "about:blank",
        extra_headers: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.title = title
        self.error_type = error_type
        self.extra_headers = extra_headers or {}
        self.additional_data = additional_data or {}


def problem_detail_handler(request, exc: ProblemDetailException):
    """Обработчик для ProblemDetailException"""
    correlation_id = str(uuid4())

    problem_data = {
        "type": exc.error_type,
        "title": exc.title,
        "status": exc.status_code,
        "detail": exc.detail,
        "correlation_id": correlation_id,
    }

    # Добавляем дополнительные данные если есть
    if exc.additional_data:
        problem_data.update(exc.additional_data)

    headers = {"Content-Type": "application/problem+json", **exc.extra_headers}

    return JSONResponse(
        status_code=exc.status_code,
        content=problem_data,
        headers=headers,
    )


def http_exception_handler(request, exc: HTTPException):
    """Обработчик для стандартных HTTPException"""
    correlation_id = str(uuid4())

    # Нормализуем детали ошибки
    if isinstance(exc.detail, dict):
        detail = exc.detail.get("detail", str(exc.detail))
    else:
        detail = str(exc.detail)

    problem_data = {
        "type": "about:blank",
        "title": "HTTP Error",
        "status": exc.status_code,
        "detail": detail,
        "correlation_id": correlation_id,
    }

    headers = {
        "Content-Type": "application/problem+json",
    }

    return JSONResponse(
        status_code=exc.status_code,
        content=problem_data,
        headers=headers,
    )


def generic_exception_handler(request, exc: Exception):
    """Обработчик для неожиданных исключений"""
    correlation_id = str(uuid4())

    problem_data = {
        "type": "about:blank",
        "title": "Internal Server Error",
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "detail": "An unexpected error occurred",
        "correlation_id": correlation_id,
    }

    print(f"Unhandled exception: {exc}")

    headers = {
        "Content-Type": "application/problem+json",
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem_data,
        headers=headers,
    )
