import asyncio
import datetime as dt
from typing import override

from pydantic import BaseModel

from server.src.models.client import ClientManager, Client, LoggerLike
from server.src.models.request import Request
from shared.schemas.actions import BroadcastMessagePayload, SendMessagePayload
from shared.schemas.notifications import BroadcastMessageNotificationPayload, \
    BroadcastMessageNotificationFrame, ErrorNotificationFrame, ErrorNotificationPayload


# async def error_handler(request: Request, error: Exception) -> None:
#     payload = ErrorNotificationPayload(
#         text=f"Something went wrong: {error}",
#         created_at=dt.datetime.now(dt.UTC),
#     )
#     frame = ErrorNotificationFrame(payload=payload)
#     request.logger.exception("Error occurred while handling request")
#     await request.reply(frame)
#
#

#
# async def unknown_action_handler(request: Request) -> None:
#     payload = ErrorNotificationPayload(text=f"Unknown command", created_at=dt.datetime.now(dt.UTC))
#     frame = ErrorNotificationFrame(payload=payload)
#     await request.reply(frame)
#     request.logger.info("Unknown command received from '%s'", request.client.user.id)
