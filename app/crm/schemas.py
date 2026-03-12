from uuid import UUID

from pydantic import BaseModel, Field


class DealOut(BaseModel):
    id: UUID
    company_name: str
    contact_name: str | None = None
    contact_email: str | None = None
    stage: str
    origin_badge: str
    score: float | None = None


class DealStageUpdate(BaseModel):
    stage: str = Field(min_length=1)
    reason_code: str | None = None
    reason_notes: str | None = None


class DealFeedbackUpdate(BaseModel):
    outcome: str = Field(pattern="^(won|lost)$")
    reason_code: str = Field(min_length=1)
    reason_notes: str | None = None


class DealStageEventOut(BaseModel):
    external_reference: str | None = None
    deal_id: str
    event_type: str
    stage: str
    previous_stage: str | None = None
    outcome: str | None = None
    reason_code: str | None = None
    reason_notes: str | None = None
    changed_at: str
    changed_by_type: str
    upstream_system: str


class DealFeedbackOut(BaseModel):
    deal_id: str
    outcome: str
    reason_code: str
    reason_notes: str | None = None
    upstream_system: str
    upstream_payload: dict[str, object]
    delivery: dict[str, object] = Field(default_factory=dict)


class DealStageMetaOut(BaseModel):
    stages: list[str] = Field(default_factory=list)
    transitions: dict[str, list[str]] = Field(default_factory=dict)
    loss_reasons: list[str] = Field(default_factory=list)
    win_reasons: list[str] = Field(default_factory=list)


class DealListOut(BaseModel):
    deals: list[DealOut] = Field(default_factory=list)
