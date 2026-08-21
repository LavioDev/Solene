from typing import Dict, List, Set
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "telemetry": set(),
            "vision": set(),
            "voice": set(),
            "display": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str = "telemetry") -> None:
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "telemetry") -> None:
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)

    async def broadcast_json(self, data: dict, channel: str = "telemetry") -> None:
        if channel in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(data)
                except Exception:
                    dead_connections.append(connection)
            for dead in dead_connections:
                self.disconnect(dead, channel)

    async def broadcast_bytes(self, data: bytes, channel: str = "vision") -> None:
        if channel in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_bytes(data)
                except Exception:
                    dead_connections.append(connection)
            for dead in dead_connections:
                self.disconnect(dead, channel)


ws_manager = WebSocketManager()
