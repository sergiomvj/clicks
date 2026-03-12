from uuid import UUID

from pydantic import BaseModel, Field


class SpaceOut(BaseModel):
    id: UUID
    workspace_id: UUID
    slug: str
    name: str


class ChannelOut(BaseModel):
    id: UUID
    workspace_id: UUID
    space_id: UUID
    slug: str
    name: str
    channel_type: str


class SpaceBundle(BaseModel):
    spaces: list[SpaceOut] = Field(default_factory=list)
    channels: list[ChannelOut] = Field(default_factory=list)
