import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(eq=False)
class Subscriber:
    queue: asyncio.Queue[str] = field(default_factory=asyncio.Queue)


class RealtimeHub:
    def __init__(self) -> None:
        self._subscribers: set[Subscriber] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> Subscriber:
        subscriber = Subscriber()
        async with self._lock:
            self._subscribers.add(subscriber)
        return subscriber

    async def unsubscribe(self, subscriber: Subscriber) -> None:
        async with self._lock:
            self._subscribers.discard(subscriber)

    async def publish(self, event: str, data: dict) -> None:
        payload = json.dumps({"type": event, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()})
        async with self._lock:
            subscribers = list(self._subscribers)
        for subscriber in subscribers:
            await subscriber.queue.put(payload)

    async def stream(self, subscriber: Subscriber) -> AsyncIterator[dict]:
        try:
            while True:
                payload = await subscriber.queue.get()
                message = json.loads(payload)
                yield {"event": message["type"], "data": json.dumps(message["data"], ensure_ascii=False)}
        finally:
            with suppress(Exception):
                await self.unsubscribe(subscriber)


hub = RealtimeHub()
