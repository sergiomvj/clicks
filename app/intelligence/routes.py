from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_workspace_id
from app.intelligence.schemas import IntelligenceReportResponse
from app.intelligence.service import IntelligenceService, get_intelligence_service

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/report", response_model=IntelligenceReportResponse)
async def get_latest_report(
    workspace_id: Annotated[UUID, Depends(get_workspace_id)],
    intelligence_service: Annotated[IntelligenceService, Depends(get_intelligence_service)],
) -> IntelligenceReportResponse:
    try:
        return await intelligence_service.get_latest_report(workspace_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        ) from exc
