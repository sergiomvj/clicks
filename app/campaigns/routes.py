from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.agents.action_logger import ActionLogger, get_action_logger
from app.api.dependencies import get_workspace_id
from app.campaigns.schemas import (
    CampaignCreateRequest,
    CampaignDispatchRequest,
    CampaignDispatchResponse,
    CampaignListResponse,
    CampaignResponse,
    GeneratedEmailResponse,
)
from app.campaigns.service import CampaignService, get_campaign_service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    campaign_service: Annotated[CampaignService, Depends(get_campaign_service)],
) -> CampaignListResponse:
    items = await campaign_service.list_campaigns(workspace_id)
    return CampaignListResponse(items=items)


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreateRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    campaign_service: Annotated[CampaignService, Depends(get_campaign_service)],
    action_logger: Annotated[ActionLogger, Depends(get_action_logger)],
    x_agent_id: str = Header(alias="X-Agent-Id"),
) -> CampaignResponse:
    campaign = await campaign_service.create_campaign(workspace_id, payload)
    await action_logger.log_action(
        workspace_id=workspace_id,
        agent_id=x_agent_id,
        team="redator",
        action_type="campaign.create",
        trigger_type="manual",
        payload=payload.model_dump(mode="json"),
        result=campaign.model_dump(mode="json"),
    )
    return campaign


@router.post("/{campaign_id}/write-email", response_model=GeneratedEmailResponse)
async def write_campaign_email(
    campaign_id: UUID,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    campaign_service: Annotated[CampaignService, Depends(get_campaign_service)],
    action_logger: Annotated[ActionLogger, Depends(get_action_logger)],
    x_agent_id: str = Header(alias="X-Agent-Id"),
) -> GeneratedEmailResponse:
    try:
        response = await campaign_service.write_email(workspace_id, campaign_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found.",
        ) from exc
    await action_logger.log_action(
        workspace_id=workspace_id,
        agent_id=x_agent_id,
        team="redator",
        action_type="campaign.write_email",
        trigger_type="manual",
        payload={"campaign_id": str(campaign_id)},
        result=response.model_dump(mode="json"),
    )
    return response


@router.post("/{campaign_id}/dispatch", response_model=CampaignDispatchResponse)
async def dispatch_campaign(
    campaign_id: UUID,
    payload: CampaignDispatchRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    campaign_service: Annotated[CampaignService, Depends(get_campaign_service)],
    action_logger: Annotated[ActionLogger, Depends(get_action_logger)],
    x_agent_id: str = Header(alias="X-Agent-Id"),
) -> CampaignDispatchResponse:
    try:
        response = await campaign_service.dispatch_campaign(workspace_id, campaign_id, payload)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    await action_logger.log_action(
        workspace_id=workspace_id,
        agent_id=x_agent_id,
        team="cadenciador",
        action_type="campaign.dispatch",
        trigger_type="manual",
        payload=payload.model_dump(mode="json") | {"campaign_id": str(campaign_id)},
        result=response.model_dump(mode="json"),
    )
    return response
