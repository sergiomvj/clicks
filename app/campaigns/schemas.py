from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CampaignCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    icp_profile_id: UUID | None = None


class CampaignDispatchRequest(BaseModel):
    lead_ids: list[UUID] = Field(min_length=1, max_length=200)


class CampaignResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    icp_profile_id: UUID | None
    name: str
    status: str
    created_at: datetime
    updated_at: datetime


class CampaignListResponse(BaseModel):
    items: list[CampaignResponse]


class GeneratedEmailResponse(BaseModel):
    campaign: CampaignResponse
    subject: str
    body: str


class DispatchItemResponse(BaseModel):
    lead_id: UUID
    domain_id: UUID
    status: str


class CampaignDispatchResponse(BaseModel):
    campaign: CampaignResponse
    dispatched: list[DispatchItemResponse]
