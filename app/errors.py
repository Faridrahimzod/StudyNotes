import logging
import re
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Настраиваем безопасный логгер
security_logger = logging.getLogger("security")


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


def mask_sensitive_data(data: Union[str, Dict, Any]) -> str:
    """
    Маскирует чувствительные данные в логах
    """
    if isinstance(data, dict):
        data_str = str(data)
    else:
        data_str = str(data)

    # Маскируем email
    data_str = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "[EMAIL_REDACTED]",
        data_str,
    )

    # Маскируем пароли (простые эвристики)
    data_str = re.sub(
        r'("password":\s*")[^"]*(")', r"\1[PASSWORD_REDACTED]\2", data_str
    )
    data_str = re.sub(r'("api_key":\s*")[^"]*(")', r"\1[API_KEY_REDACTED]\2", data_str)
    data_str = re.sub(r'("token":\s*")[^"]*(")', r"\1[TOKEN_REDACTED]\2", data_str)

    # Маскируем кредитные карты (упрощенно)
    data_str = re.sub(
        r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "[CARD_REDACTED]", data_str
    )

    return data_str


def problem_detail_handler(request: Request, exc: ProblemDetailException):
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

    # Безопасное логирование без PII
    safe_path = mask_sensitive_data(str(request.url))
    security_logger.warning(
        "ProblemDetailException: %s %s - %s - %s",
        exc.status_code,
        exc.title,
        correlation_id,
        safe_path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=problem_data,
        headers=headers,
    )


def http_exception_handler(request: Request, exc: HTTPException):
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

    # Безопасное логирование
    safe_detail = mask_sensitive_data(detail)
    security_logger.warning(
        "HTTPException: %s - %s - %s", exc.status_code, correlation_id, safe_detail
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=problem_data,
        headers=headers,
    )


def generic_exception_handler(request: Request, exc: Exception):
    """Обработчик для неожиданных исключений"""
    correlation_id = str(uuid4())

    problem_data = {
        "type": "about:blank",
        "title": "Internal Server Error",
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "detail": "An unexpected error occurred",
        "correlation_id": correlation_id,
    }

    # Безопасное логирование - не логируем полный traceback в продакшене
    security_logger.error(
        "Unhandled exception: %s - %s - %s",
        type(exc).__name__,
        correlation_id,
        mask_sensitive_data(str(request.url)),
    )

    headers = {
        "Content-Type": "application/problem+json",
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem_data,
        headers=headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации в формате RFC 7807"""
    from uuid import uuid4

    errors = exc.errors()
    error_details = []

    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        error_details.append(f"{field}: {error['msg']}")

    detail = "; ".join(error_details)

    return JSONResponse(
        status_code=422,
        content={
            "type": "/errors/validation",
            "title": "Validation Error",
            "status": 422,
            "detail": detail,
            "correlation_id": str(uuid4()),
        },
        media_type="application/problem+json",
    )
