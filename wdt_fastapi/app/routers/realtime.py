import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse

from ..services.realtime import hub

router = APIRouter(tags=["realtime"])


@router.get("/api/realtime/events")
async def realtime_events() -> EventSourceResponse:
    subscriber = await hub.subscribe()
    return EventSourceResponse(hub.stream(subscriber))


@router.websocket("/ws/realtime")
async def realtime_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    subscriber = await hub.subscribe()
    try:
        while True:
            message = await subscriber.queue.get()
            await websocket.send_text(message)
    except WebSocketDisconnect:
        await hub.unsubscribe(subscriber)
    except Exception:
        await hub.unsubscribe(subscriber)
        raise
