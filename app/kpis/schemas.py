from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KpiOut(BaseModel):
    id: UUID
    workspace_id: UUID
    space_id: UUID | None = None
    slug: str
    name: str
    unit: str
    target_value: float
    current_value: float
    status: str
    source: str
    updated_at: datetime


class KpiListOut(BaseModel):
    kpis: list[KpiOut] = Field(default_factory=list)
