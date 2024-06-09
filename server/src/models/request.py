import logging
from logging import Logger
from typing import TYPE_CHECKING, Mapping

from shared.requests import Actions
from shared.messages import Message
if TYPE_CHECKING:
    from server.src.models.client import Client


type LoggerLike = Logger | logging.LoggerAdapter


class Request:
    __slots__ = ("_client", "_logger", "_data", "_action")

    def __init__(self, client: 'Client', logger: LoggerLike, action: Actions, data: dict) -> None:
        self._client = client
        self._logger = logger
        self._action = action
        self._data = data

    @property
    def client(self) -> 'Client':
        return self._client

    @property
    def logger(self) -> LoggerLike:
        return self._logger

    @property
    def action(self) -> Actions:
        return self._action

    @property
    def data(self) -> Mapping:
        return self._data

    async def reply(self, message: Message) -> None:
        await self._client.send(message)

    def __str__(self) -> str:
        return f'Request(client={self._client.user.username}, action={self._action.value}, data={self._data})'
