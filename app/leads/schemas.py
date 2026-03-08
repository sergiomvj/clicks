from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LeadIngestItem(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    role: str | None = Field(default=None, max_length=255)
    linkedin_url: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    company_cnpj: str | None = Field(default=None, max_length=32)
    company_sector: str | None = Field(default=None, max_length=255)
    company_size: str | None = Field(default=None, max_length=64)
    company_website: str | None = Field(default=None, max_length=255)
    source: str | None = Field(default=None, max_length=64)
    campaign_id: UUID | None = None
    icp_profile_id: UUID | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()


class LeadIngestRequest(BaseModel):
    leads: list[LeadIngestItem] = Field(min_length=1, max_length=500)


class LeadInteractionResponse(BaseModel):
    id: UUID
    type: str
    occurred_at: datetime
    metadata: dict[str, object]


class LeadResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    campaign_id: UUID | None
    icp_profile_id: UUID | None
    name: str | None
    email: str | None
    email_valid: bool | None
    role: str | None
    linkedin_url: str | None
    company_name: str | None
    company_cnpj: str | None
    company_sector: str | None
    company_size: str | None
    company_website: str | None
    score: int
    funnel_stage: str
    source: str | None
    enrichment_data: dict[str, object]
    discard_reason: str | None
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    items: list[LeadResponse]


class LeadIngestResponse(BaseModel):
    inserted_count: int
    items: list[LeadResponse]


class LeadDetailResponse(BaseModel):
    lead: LeadResponse
    interactions: list[LeadInteractionResponse]


class LeadValidationResponse(BaseModel):
    lead: LeadResponse
    is_valid: bool


class LeadScoreResponse(BaseModel):
    lead: LeadResponse
    score_reason: str
