from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_workspace_uuid
from app.core.database import get_database_pool
from app.core.rate_limit import enforce_rate_limit
from app.crm.schemas import DealFeedbackOut, DealFeedbackUpdate, DealListOut, DealOut, DealStageMetaOut, DealStageUpdate
from app.crm.service import create_upstream_feedback, list_deals, list_stage_meta, update_deal_stage

router = APIRouter(prefix="/deals", tags=["crm"])


@router.get("", response_model=DealListOut)
async def get_deals(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> DealListOut:
    return await list_deals(get_database_pool(), workspace_id)


@router.get("/meta", response_model=DealStageMetaOut)
async def get_deal_meta() -> DealStageMetaOut:
    return list_stage_meta()


@router.patch("/{deal_id}/stage", response_model=DealOut)
async def patch_deal_stage(deal_id: str, payload: DealStageUpdate, workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> DealOut:
    await enforce_rate_limit(f'deals:stage:{workspace_id}', limit=40, window_seconds=60)
    try:
        return await update_deal_stage(get_database_pool(), workspace_id, UUID(deal_id), payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("/{deal_id}/feedback", response_model=DealFeedbackOut)
async def post_deal_feedback(deal_id: str, payload: DealFeedbackUpdate, workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> DealFeedbackOut:
    await enforce_rate_limit(f'deals:feedback:{workspace_id}', limit=20, window_seconds=60)
    try:
        return await create_upstream_feedback(get_database_pool(), workspace_id, UUID(deal_id), payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
