import datetime as dt
from typing import override

from server.src.handlers.base_handler import BaseHandler
from server.src.models.client import Client
from shared.schemas.actions import SendMessagePayload
from shared.schemas.notifications import BroadcastMessageNotificationPayload, \
    BroadcastMessageNotificationFrame, ErrorNotificationFrame, ErrorNotificationPayload


class SendMessageHandler(BaseHandler):
    validator = SendMessagePayload

    @override
    async def handle(self) -> None:
        receiver = self.clients.get(self.payload.to)
        if receiver is None:
            await self._receiver_not_found()
        else:
            await self._send_message(receiver)

    async def _receiver_not_found(self) -> None:
        self.logger.info(f"User '{self.payload.to}' not found")
        payload = ErrorNotificationPayload(
            text=f"User '{self.payload.to}' not found",
            created_at=dt.datetime.now(dt.UTC),
        )
        frame = ErrorNotificationFrame(payload=payload)
        await self.client.send(frame)

    async def _send_message(self, client: Client) -> None:
        self.logger.info(f"Sending message to '{self.payload.to}'...")
        payload = BroadcastMessageNotificationPayload(
            text=self.payload.text,
            sender=self.client.user.id,
            created_at=dt.datetime.now(dt.UTC),
        )
        frame = BroadcastMessageNotificationFrame(payload=payload)
        await client.send(frame)
