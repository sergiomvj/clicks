from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_workspace_id
from app.leads.schemas import (
    LeadDetailResponse,
    LeadIngestRequest,
    LeadIngestResponse,
    LeadListResponse,
    LeadResponse,
    LeadScoreResponse,
    LeadValidationResponse,
)
from app.leads.service import LeadService, get_lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/ingest", response_model=LeadIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_leads(
    payload: LeadIngestRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> LeadIngestResponse:
    return await lead_service.ingest_leads(workspace_id, payload)


@router.get("", response_model=LeadListResponse)
async def list_leads(
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
    stage: str | None = Query(default=None),
    score_min: int | None = Query(default=None, ge=0, le=100),
    campaign_id: UUID | None = Query(default=None),
    source: str | None = Query(default=None),
) -> LeadListResponse:
    items = await lead_service.list_leads(
        workspace_id=workspace_id,
        stage=stage,
        score_min=score_min,
        campaign_id=campaign_id,
        source=source,
    )
    return LeadListResponse(items=items)


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead_detail(
    lead_id: UUID,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> LeadDetailResponse:
    try:
        return await lead_service.get_lead_detail(workspace_id, lead_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found.",
        ) from exc


@router.post("/{lead_id}/validate-email", response_model=LeadValidationResponse)
async def validate_lead_email(
    lead_id: UUID,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> LeadValidationResponse:
    try:
        return await lead_service.validate_email(workspace_id, lead_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found.",
        ) from exc


@router.post("/{lead_id}/enrich", response_model=LeadResponse)
async def enrich_lead(
    lead_id: UUID,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> LeadResponse:
    try:
        return await lead_service.enrich_lead(workspace_id, lead_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found.",
        ) from exc


@router.post("/{lead_id}/score", response_model=LeadScoreResponse)
async def score_lead(
    lead_id: UUID,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> LeadScoreResponse:
    try:
        return await lead_service.score_lead(workspace_id, lead_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found.",
        ) from exc
