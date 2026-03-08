from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PostalWebhookPayload(BaseModel):
    event: str
    lead_id: UUID
    email_send_id: UUID | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class FbrClickWebhookPayload(BaseModel):
    event: str
    lead_id: UUID | None = None
    campaign_id: UUID | None = None
    reason: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class WebhookAckResponse(BaseModel):
    status: str
    processed_at: datetime
