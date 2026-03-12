from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user_id, get_workspace_uuid
from app.core.database import get_database_pool
from app.core.rate_limit import enforce_multiple_rate_limits
from app.git_watcher.schemas import GitWatcherListOut, GitWatcherOut, GitWatcherUpsertRequest
from app.git_watcher.service import list_git_watchers, upsert_git_watcher

router = APIRouter(prefix='/git-watcher', tags=['git-watcher'])


@router.get('', response_model=GitWatcherListOut)
async def get_git_watchers(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> GitWatcherListOut:
    return await list_git_watchers(get_database_pool(), workspace_id)


@router.post('', response_model=GitWatcherOut)
async def post_git_watcher(
    payload: GitWatcherUpsertRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_uuid)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> GitWatcherOut:
    await enforce_multiple_rate_limits(
        [
            (f'git_watcher:{workspace_id}:{user_id}', 20, 60),
            (f'git_watcher:repo:{workspace_id}:{payload.repository_path}', 20, 60),
        ]
    )
    return await upsert_git_watcher(get_database_pool(), workspace_id, payload)
