from collections import defaultdict
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class WorkspaceWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, workspace_id: str) -> None:
        await websocket.accept()
        self._connections[workspace_id].add(websocket)

    def disconnect(self, websocket: WebSocket, workspace_id: str) -> None:
        connections = self._connections.get(workspace_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(workspace_id, None)

    async def send_snapshot(self, websocket: WebSocket, workspace_id: str) -> None:
        await websocket.send_json({"event": "connected", "workspaceId": workspace_id})

    async def broadcast(self, workspace_id: str, event: str, payload: dict[str, Any]) -> None:
        connections = list(self._connections.get(workspace_id, set()))
        if not connections:
            return
        stale: list[WebSocket] = []
        message = {"event": event, "workspaceId": workspace_id, "payload": payload}
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except (RuntimeError, WebSocketDisconnect):
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket, workspace_id)


workspace_manager = WorkspaceWebSocketManager()
