from collections import defaultdict
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ChannelWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, channel_id: str) -> None:
        await websocket.accept()
        self._connections[channel_id].add(websocket)

    def disconnect(self, websocket: WebSocket, channel_id: str) -> None:
        connections = self._connections.get(channel_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(channel_id, None)

    async def send_snapshot(self, websocket: WebSocket, channel_id: str) -> None:
        await websocket.send_json({"event": "connected", "channelId": channel_id})

    async def broadcast(self, channel_id: str, event: str, payload: dict[str, Any]) -> None:
        connections = list(self._connections.get(channel_id, set()))
        if not connections:
            return
        stale: list[WebSocket] = []
        message = {"event": event, "channelId": channel_id, "payload": payload}
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except (RuntimeError, WebSocketDisconnect):
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket, channel_id)


manager = ChannelWebSocketManager()
