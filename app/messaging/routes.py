from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies import get_current_user_id, get_workspace_uuid
from app.core.database import get_database_pool
from app.core.rate_limit import enforce_multiple_rate_limits
from app.messaging.schemas import MessageCreate, MessageListOut, MessageOut
from app.messaging.service import create_message, list_messages
from app.messaging.websocket import manager

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/{channel_id}", response_model=MessageListOut)
async def get_messages(channel_id: str, workspace_id: Annotated[UUID, Depends(get_workspace_uuid)]) -> MessageListOut:
    return await list_messages(get_database_pool(), workspace_id, UUID(channel_id))


@router.post("", response_model=MessageOut)
async def post_message(
    payload: MessageCreate,
    workspace_id: Annotated[UUID, Depends(get_workspace_uuid)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> MessageOut:
    await enforce_multiple_rate_limits(
        [
            (f'messages:{workspace_id}:{user_id}', 30, 60),
            (f'messages:channel:{workspace_id}:{payload.channel_id}', 80, 60),
        ]
    )
    return await create_message(get_database_pool(), workspace_id, user_id, payload)


@router.websocket("/ws/channels/{channel_id}")
async def channel_socket(websocket: WebSocket, channel_id: str) -> None:
    await manager.connect(websocket, channel_id)
    await manager.send_snapshot(websocket, channel_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id)
