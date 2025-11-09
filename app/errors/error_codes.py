"""
Карта ошибок приложения для централизованного управления
"""

from enum import Enum
from typing import Any, Dict


class ErrorCode(Enum):
    """Коды ошибок приложения"""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND_ERROR = "NOT_FOUND_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


ERROR_MAP: Dict[ErrorCode, Dict[str, Any]] = {
    ErrorCode.VALIDATION_ERROR: {
        "type": "/errors/validation",
        "title": "Validation Error",
        "status": 422,
    },
    ErrorCode.AUTHENTICATION_ERROR: {
        "type": "/errors/authentication",
        "title": "Authentication Error",
        "status": 401,
    },
    ErrorCode.AUTHORIZATION_ERROR: {
        "type": "/errors/authorization",
        "title": "Authorization Error",
        "status": 403,
    },
    ErrorCode.NOT_FOUND_ERROR: {
        "type": "/errors/not-found",
        "title": "Not Found",
        "status": 404,
    },
    ErrorCode.RATE_LIMIT_ERROR: {
        "type": "/errors/rate-limit",
        "title": "Rate Limit Exceeded",
        "status": 429,
    },
    ErrorCode.INTERNAL_ERROR: {
        "type": "/errors/internal",
        "title": "Internal Server Error",
        "status": 500,
    },
    ErrorCode.EXTERNAL_SERVICE_ERROR: {
        "type": "/errors/external-service",
        "title": "External Service Error",
        "status": 502,
    },
}


def create_problem_detail(
    error_code: ErrorCode, detail: str, **kwargs
) -> Dict[str, Any]:
    """
    Создает детали проблемы в формате RFC 7807 на основе кода ошибки
    """
    base = ERROR_MAP[error_code].copy()
    base["detail"] = detail
    base.update(kwargs)
    return base
