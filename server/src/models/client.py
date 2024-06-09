import asyncio
import logging
from logging import Logger
from typing import Set

from server.src.models.user import User
from server.src.utils import usernames_generator
from shared.messages import Message
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
        return f'Client(username={self._user.username} address={self._transport})'

    async def close(self):
        await self._transport.close()

    async def listen(self) -> str:
        return await self._transport.receive()

    async def send(self, message: Message) -> None:
        await self._transport.transfer(message.model_dump_json())


class ClientManager:
    def __init__(self) -> None:
        self._clients: Set[Client] = set()
        self._free_usernames = usernames_generator()

    def create(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> Client:
        user = User(username=next(self._free_usernames))
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
