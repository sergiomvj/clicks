from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_workspace_uuid
from app.core.database import get_database_pool
from app.spaces.schemas import SpaceBundle
from app.spaces.service import list_spaces_bundle

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get("", response_model=SpaceBundle)
async def get_spaces(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> SpaceBundle:
    return await list_spaces_bundle(get_database_pool(), workspace_id)
