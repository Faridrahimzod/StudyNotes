from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validation import StrictBaseModel


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class NoteBase(StrictBaseModel):
    title: str = Field(
        ..., min_length=1, max_length=200, pattern="^[a-zA-Z0-9\\s\\-\\.\\,]+$"
    )
    body: str = Field(..., min_length=1, max_length=10000)
    priority: Decimal = Field(
        default=Decimal("1.0"), ge=Decimal("0.1"), le=Decimal("10.0")
    )


class NoteCreate(NoteBase):
    @field_validator("title")
    @classmethod
    def validate_title_content(cls, v):
        """Защита от потенциально опасного контента в заголовке"""
        forbidden_patterns = ["<script>", "javascript:", "onload="]
        for pattern in forbidden_patterns:
            if pattern in v.lower():
                raise ValueError(f"Title contains forbidden pattern: {pattern}")
        return v


class NoteUpdate(StrictBaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = Field(None, min_length=1, max_length=10000)
    priority: Optional[Decimal] = Field(None, ge=Decimal("0.1"), le=Decimal("10.0"))


class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)
