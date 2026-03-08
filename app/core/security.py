from fastapi import Header, HTTPException, status


async def require_agent_id(x_agent_id: str | None = Header(default=None)) -> str:
    if x_agent_id is None or not x_agent_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Agent-Id header is required.",
        )
    return x_agent_id


async def require_workspace_id(x_workspace_id: str | None = Header(default=None)) -> str:
    if x_workspace_id is None or not x_workspace_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Workspace-Id header is required.",
        )
    return x_workspace_id
