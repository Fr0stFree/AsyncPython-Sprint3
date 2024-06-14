import asyncio
import datetime as dt
from typing import override

from server.src.handlers.base_handler import BaseHandler
from shared.schemas.actions import BroadcastMessagePayload
from shared.schemas.notifications import BroadcastMessageNotificationPayload, \
    BroadcastMessageNotificationFrame


class BroadcastMessageHandler(BaseHandler):
    payload_validator = BroadcastMessagePayload

    @override
    async def handle(self) -> None:
        payload = BroadcastMessageNotificationPayload(
            text=self.payload.text,
            sender=self.client.user.id,
            created_at=dt.datetime.now(dt.UTC),
        )
        frame = BroadcastMessageNotificationFrame(payload=payload)
        tasks = [client.send(frame) for client in self.clients.all()]
        await asyncio.gather(*tasks)
