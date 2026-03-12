from datetime import datetime

from pydantic import BaseModel


class FbrEcosystemCallback(BaseModel):
    workspace_id: str
    source_system: str
    event_type: str
    status: str
    reference_id: str
    related_entity_id: str | None = None
    occurred_at: datetime
