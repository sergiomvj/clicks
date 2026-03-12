from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MessageOut(BaseModel):
    id: UUID
    channel_id: UUID
    author_type: str
    author_id: str
    body: str
    source_system: str | None = None
    created_at: datetime


class MessageCreate(BaseModel):
    channel_id: str
    body: str = Field(min_length=1)


class MessageListOut(BaseModel):
    messages: list[MessageOut] = Field(default_factory=list)
