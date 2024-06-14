import asyncio
import datetime as dt
from typing import override

from server.src.handlers.base_handler import BaseHandler
from shared.schemas.actions import BroadcastMessagePayload
from shared.schemas.notifications import BroadcastMessageNotificationPayload, \
    BroadcastMessageNotificationFrame


class LogoutHandler(BaseHandler):
    payload_validator = None

    @override
    async def handle(self) -> None:
        await self.clients.drop(self.client)

