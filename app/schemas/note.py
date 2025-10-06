from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    title: str
    body: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True
