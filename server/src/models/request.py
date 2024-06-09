import logging
from logging import Logger
from typing import TYPE_CHECKING

from shared.schemas.actions import ActionFrame
from shared.schemas.notifications import NotificationFrame

if TYPE_CHECKING:
    from server.src.models.client import Client

type LoggerLike = Logger | logging.LoggerAdapter


class Request:
    __slots__ = ("_client", "_logger", "_frame")

    def __init__(self, client: 'Client', logger: LoggerLike, frame: ActionFrame) -> None:
        self._client = client
        self._logger = logger
        self._frame = frame

    @property
    def client(self) -> 'Client':
        return self._client

    @property
    def logger(self) -> LoggerLike:
        return self._logger

    @property
    def frame(self) -> ActionFrame:
        return self._frame

    async def reply(self, message: NotificationFrame) -> None:
        await self._client.send(message)

    def __str__(self) -> str:
        return f'Request(client={self._client.user.id}, action={self._frame.type.value})'
