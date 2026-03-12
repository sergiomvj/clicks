from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TaskOut(BaseModel):
    id: UUID
    title: str
    status: str
    priority: str
    source: str
    due_at: datetime | None = None


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    deal_id: str | None = None
    channel_id: str | None = None
    priority: str = "medium"
    source: str = "human"


class TaskListOut(BaseModel):
    tasks: list[TaskOut] = Field(default_factory=list)
