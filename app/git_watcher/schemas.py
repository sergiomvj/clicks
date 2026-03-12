from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GitWatcherOut(BaseModel):
    id: UUID
    workspace_id: UUID
    agent_id: UUID | None = None
    repository_path: str
    branch: str
    status: str
    last_seen_commit: str | None = None
    last_synced_at: datetime | None = None
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime


class GitWatcherListOut(BaseModel):
    watchers: list[GitWatcherOut] = Field(default_factory=list)


class GitWatcherUpsertRequest(BaseModel):
    agent_id: UUID | None = None
    repository_path: str = Field(min_length=1)
    branch: str = Field(default='main', min_length=1)
    status: str = Field(default='idle', min_length=1)
    last_seen_commit: str | None = None
    last_synced_at: datetime | None = None
    last_error: str | None = None
