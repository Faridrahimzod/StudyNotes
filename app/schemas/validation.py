import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictBaseModel(BaseModel):
    """Базовый класс с запретом лишних полей"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PaymentValidation(StrictBaseModel):
    """Валидация платежей с Decimal и UTC"""

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3, pattern="^[A-Z]{3}$")
    occurred_at: datetime
    description: str = Field(min_length=1, max_length=500)

    @field_validator("occurred_at")
    @classmethod
    def normalize_utc(cls, v: datetime) -> datetime:
        """Нормализация времени в UTC"""
        if v.tzinfo is None:
            # Если время без зоны, считаем что UTC
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        """Проверка точности Decimal"""
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return v


def safe_json_parse(json_str: str) -> Dict[str, Any]:
    """
    Безопасный парсинг JSON с защитой от float-атак
    """
    try:
        return json.loads(json_str, parse_float=str)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"Invalid JSON: {str(e)}")
