from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Tag(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    tags: List[str]

class NoteUpdate(NoteBase):
    tags: Optional[List[str]] = None

class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[Tag]

    class Config:
        orm_mode = True
        from_attributes = True

