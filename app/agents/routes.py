from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from starlette.websockets import WebSocketDisconnect

from app.agents.schemas import (
    AgentControlOut,
    AgentControlUpdateRequest,
    AgentListOut,
    AgentRegistrationOut,
    AgentRegistrationRequest,
    AgentTokenOut,
    AgentTokenRequest,
    AgentValidationOut,
    AgentValidationRequest,
    ApprovalCreateRequest,
    ApprovalDecisionRequest,
    ApprovalListOut,
    ApprovalOut,
    AuditLogListOut,
)
from app.agents.service import (
    create_approval,
    decide_approval,
    get_agent_control,
    issue_agent_token,
    list_agents,
    list_approvals,
    list_audit_logs,
    register_agent,
    set_kill_switch,
    validate_agent_repository,
)
from app.agents.websocket import workspace_manager
from app.api.dependencies import get_current_user_id, get_workspace_uuid
from app.core.database import get_database_pool
from app.core.rate_limit import enforce_rate_limit

router = APIRouter(prefix='/agents', tags=['agents'])


@router.get('', response_model=AgentListOut)
async def get_agents(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> AgentListOut:
    return await list_agents(get_database_pool(), workspace_id)


@router.get('/control', response_model=AgentControlOut)
async def get_agents_control(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> AgentControlOut:
    return await get_agent_control(workspace_id)


@router.post('/control/kill-switch', response_model=AgentControlOut)
async def post_kill_switch(
    payload: AgentControlUpdateRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_uuid)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> AgentControlOut:
    await enforce_rate_limit(f'agents:kill_switch:{workspace_id}:{user_id}', limit=10, window_seconds=60)
    control = await set_kill_switch(workspace_id, user_id, payload)
    return control


@router.post('/validate', response_model=AgentValidationOut)
async def validate_agent(payload: AgentValidationRequest) -> AgentValidationOut:
    return validate_agent_repository(payload.repository_path)


@router.post('', response_model=AgentRegistrationOut)
async def post_agent(payload: AgentRegistrationRequest, workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> AgentRegistrationOut:
    try:
        return await register_agent(get_database_pool(), workspace_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post('/tokens', response_model=AgentTokenOut)
async def post_agent_token(
    payload: AgentTokenRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_uuid)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> AgentTokenOut:
    await enforce_rate_limit(f'agents:tokens:{workspace_id}:{user_id}', limit=20, window_seconds=60)
    try:
        return await issue_agent_token(get_database_pool(), workspace_id, user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get('/approvals', response_model=ApprovalListOut)
async def get_approvals(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> ApprovalListOut:
    return await list_approvals(get_database_pool(), workspace_id)


@router.post('/approvals', response_model=ApprovalOut)
async def post_approval(
    payload: ApprovalCreateRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_uuid)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> ApprovalOut:
    await enforce_rate_limit(f'agents:approvals:{workspace_id}:{user_id}', limit=20, window_seconds=60)
    try:
        return await create_approval(get_database_pool(), workspace_id, user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.patch('/approvals/{approval_id}', response_model=ApprovalOut)
async def patch_approval(
    approval_id: str,
    payload: ApprovalDecisionRequest,
    workspace_id: Annotated[UUID, Depends(get_workspace_uuid)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> ApprovalOut:
    await enforce_rate_limit(f'agents:approval_decisions:{workspace_id}:{user_id}', limit=20, window_seconds=60)
    try:
        return await decide_approval(get_database_pool(), workspace_id, UUID(approval_id), user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get('/audit-logs', response_model=AuditLogListOut)
async def get_audit_logs(workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> AuditLogListOut:
    return await list_audit_logs(get_database_pool(), workspace_id)


@router.websocket('/ws/workspaces/{workspace_id}')
async def workspace_socket(websocket: WebSocket, workspace_id: str) -> None:
    await workspace_manager.connect(websocket, workspace_id)
    await workspace_manager.send_snapshot(websocket, workspace_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        workspace_manager.disconnect(websocket, workspace_id)
