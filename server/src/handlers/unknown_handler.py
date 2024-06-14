import datetime as dt
from typing import override

from pydantic import TypeAdapter

from server.src.handlers.base_handler import BaseHandler
from shared.schemas.notifications import ErrorNotificationFrame, ErrorNotificationPayload


class UnknownActionHandler(BaseHandler):
    validator = TypeAdapter(dict)

    @override
    async def handle(self) -> None:
        payload = ErrorNotificationPayload(text=f"Unknown command", created_at=dt.datetime.now(dt.UTC))
        frame = ErrorNotificationFrame(payload=payload)
        await self.client.send(frame)
        self.logger.info("Unknown command received from '%s'", self.client.user.id)
