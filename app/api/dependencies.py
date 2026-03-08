from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.database import get_database_pool
from app.core.security import require_workspace_id


async def get_workspace_id(
    x_workspace_id: Annotated[str, Depends(require_workspace_id)],
) -> UUID:
    try:
        workspace_id = UUID(x_workspace_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Workspace-Id must be a valid UUID.",
        ) from exc

    database_pool = get_database_pool()
    records: Sequence[object] = await database_pool.fetch(
        "SELECT id FROM workspaces WHERE id = $1",
        workspace_id,
    )
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )
    return workspace_id
