from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_workspace_uuid
from app.core.database import get_database_pool
from app.kpis.schemas import KpiListOut
from app.kpis.service import list_kpis

router = APIRouter(prefix="/kpis", tags=["kpis"])


@router.get("", response_model=KpiListOut)
async def get_kpis(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> KpiListOut:
    return await list_kpis(get_database_pool(), workspace_id)
