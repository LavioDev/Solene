from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websockets.ws_manager import ws_manager

ws_router = APIRouter(prefix="/ws", tags=["WebSockets"])


@ws_router.websocket("/telemetry")
async def ws_telemetry(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket, channel="telemetry")
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast received telemetry to all connected client monitors
            await ws_manager.broadcast_json(data, channel="telemetry")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="telemetry")


@ws_router.websocket("/vision")
async def ws_vision(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket, channel="vision")
    try:
        while True:
            # Receive binary frame from ESP32 camera
            frame_bytes = await websocket.receive_bytes()
            # Broadcast frame to frontend monitors
            await ws_manager.broadcast_bytes(frame_bytes, channel="vision")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="vision")


@ws_router.websocket("/voice")
async def ws_voice(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket, channel="voice")
    try:
        while True:
            audio_bytes = await websocket.receive_bytes()
            # In future: Route to VAD/STT pipeline
            await ws_manager.broadcast_bytes(audio_bytes, channel="voice")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="voice")


@ws_router.websocket("/display")
async def ws_display(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket, channel="display")
    try:
        while True:
            display_payload = await websocket.receive_bytes()
            await ws_manager.broadcast_bytes(display_payload, channel="display")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="display")
