from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class RealtimeManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[user_id].add(websocket)
        await self.broadcast_user(user_id, {"type": "presence", "status": "online", "user_id": user_id})

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        self.connections[user_id].discard(websocket)

    async def send_user(self, user_id: str, payload: dict[str, Any]) -> None:
        dead = []
        for websocket in self.connections.get(user_id, set()):
            try:
                await websocket.send_json(payload)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            self.connections[user_id].discard(websocket)

    async def broadcast_user(self, user_id: str, payload: dict[str, Any]) -> None:
        await self.send_user(user_id, payload)


realtime_manager = RealtimeManager()
