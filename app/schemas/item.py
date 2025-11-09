from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    created_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        # Запрещаем потенциально опасные символы
        dangerous_chars = ["<", ">", "script", "javascript:"]
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"Name contains dangerous characters: {char}")
        return v

    @field_validator("created_at", mode="before")
    @classmethod
    def set_utc_default(cls, v):
        # Нормализация времени в UTC
        if v is None:
            return datetime.now(timezone.utc).replace(tzinfo=None)
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v
