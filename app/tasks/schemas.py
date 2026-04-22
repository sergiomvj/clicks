from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


PRIORITY_ALIASES = {
    'urgent': 'p0',
    'critical': 'p0',
    'p0': 'p0',
    'high': 'p1',
    'p1': 'p1',
    'medium': 'p2',
    'normal': 'p2',
    'p2': 'p2',
    'low': 'p3',
    'backlog': 'p3',
    'p3': 'p3',
}


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
    priority: str = "p2"
    source: str = "human"

    @field_validator('priority')
    @classmethod
    def normalize_priority(cls, value: str) -> str:
        normalized = PRIORITY_ALIASES.get(value.strip().lower())
        if not normalized:
            raise ValueError('priority must be one of p0, p1, p2 or p3.')
        return normalized


class TaskListOut(BaseModel):
    tasks: list[TaskOut] = Field(default_factory=list)
