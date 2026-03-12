from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user_id, get_workspace_uuid
from app.core.database import get_database_pool
from app.core.rate_limit import enforce_multiple_rate_limits
from app.tasks.schemas import TaskCreate, TaskListOut, TaskOut
from app.tasks.service import create_task, list_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListOut)
async def get_tasks(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> TaskListOut:
    return await list_tasks(get_database_pool(), workspace_id)


@router.post("", response_model=TaskOut)
async def post_task(
    payload: TaskCreate,
    workspace_id: Annotated[UUID, Depends(get_workspace_uuid)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskOut:
    rules = [(f'tasks:{workspace_id}:{user_id}', 30, 60)]
    if payload.channel_id:
        rules.append((f'tasks:channel:{workspace_id}:{payload.channel_id}', 60, 60))
    await enforce_multiple_rate_limits(rules)
    return await create_task(get_database_pool(), workspace_id, payload)
