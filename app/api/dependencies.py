from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.database import get_database_pool
from app.core.security import decode_agent_access_token, require_bearer_token, require_user_id, require_workspace_id


async def get_current_user_id(x_user_id: Annotated[str, Depends(require_user_id)]) -> UUID:
    try:
        return UUID(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='X-User-Id must be a valid UUID.') from exc


async def get_workspace_uuid(x_workspace_id: Annotated[str, Depends(require_workspace_id)]) -> UUID:
    try:
        workspace_id = UUID(x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='X-Workspace-Id must be a valid UUID.') from exc

    pool = get_database_pool()
    records: Sequence[object] = await pool.fetch('SELECT id FROM workspaces WHERE id = $1', workspace_id)
    if not records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Workspace not found.')
    return workspace_id


async def get_agent_context(
    token: Annotated[str, Depends(require_bearer_token)],
    workspace_id: Annotated[UUID, Depends(get_workspace_uuid)],
) -> dict[str, object]:
    payload = decode_agent_access_token(token)
    token_workspace_id = payload.get('workspace_id')
    if token_workspace_id != str(workspace_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Agent token does not belong to this workspace.')

    try:
        agent_id = UUID(str(payload.get('sub')))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid agent token subject.') from exc

    return {
        'agent_id': agent_id,
        'workspace_id': workspace_id,
        'slug': str(payload.get('slug')),
        'scope_actions': [str(item) for item in payload.get('scope_actions', [])],
        'approval_required_actions': [str(item) for item in payload.get('approval_required_actions', [])],
    }
