import asyncio
import logging
from logging import Logger
from typing import Set, Self

from server.src.models.user import User
from server.src.utils import usernames_generator
from shared.schemas.notifications import NotificationFrame
from shared.schemas.types import UserId
from shared.transport import DataTransport

type LoggerLike = Logger | logging.LoggerAdapter


class Client:
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        user: User
    ) -> None:
        self._transport = DataTransport(writer=writer, reader=reader)
        self._user = user

    @property
    def user(self) -> User:
        return self._user

    def __str__(self):
        return f'Client(username={self._user.id} address={self._transport})'

    async def close(self):
        await self._transport.close()

    async def listen(self) -> str:
        return await self._transport.receive()

    async def send(self, frame: NotificationFrame) -> None:
        await self._transport.transfer(frame.model_dump_json())


class ClientManager:
    _instance: Self | None = None

    def __init__(self) -> None:
        self._clients: Set[Client] = set()
        self._free_usernames = usernames_generator()

    def __new__(cls) -> 'ClientManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_current(cls) -> Self:
        if cls._instance is None:
            return cls()
        return cls._instance

    def create(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> Client:
        generated_id = UserId(next(self._free_usernames))
        user = User(id=generated_id)
        client = Client(reader=reader, writer=writer, user=user)
        self._clients.add(client)
        return client

    def get(self, username: str) -> Client | None:
        return next(filter(lambda client: client.user.username == username, self._clients), None)

    async def drop(self, client: Client) -> None:
        await client.close()
        self._clients.remove(client)

    def all(self) -> Set[Client]:
        return self._clients
