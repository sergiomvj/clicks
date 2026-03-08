from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class IntelligenceReportResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    campaign_id: UUID | None
    insights: str | None
    generated_at: datetime
    content: dict[str, object]
