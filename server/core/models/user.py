import asyncio

from utils.classes import Singleton
from server.core.network import DataTransport
from server.core.exceptions import UsernameAlreadyTaken, UserDoesNotExist


class UserManager(metaclass=Singleton):
    def __init__(self):
        self._storage: dict = {}

    def create(self, reader, writer, username) -> 'User':
        if username in self._storage:
            raise UsernameAlreadyTaken
        user = User(reader, writer, username)
        self._storage[username] = user
        return user

    def get(self, username: str) -> 'User':
        try:
            return self._storage[username]
        except KeyError:
            raise UserDoesNotExist

    def all(self) -> list:
        return list(self._storage.values())

    def rename(self, user: 'User', new_username: str) -> None:
        if new_username in self._storage:
            raise UsernameAlreadyTaken
        del self._storage[user.username]
        user._username = new_username
        self._storage[new_username] = user

    async def remove(self, user: 'User') -> None:
        await user._transport.close()
        del self._storage[user.username]

    @staticmethod
    async def send(user: 'User', data: str) -> None:
        await user._transport.transfer(data)

    @staticmethod
    async def receive(user: 'User') -> str:
        return await user._transport.receive()


class User:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 username: str) -> None:
        self._transport = DataTransport(writer, reader)
        self._username = username
        self._is_banned = False

    @property
    def username(self) -> str:
        return self._username

    @property
    def is_banned(self) -> bool:
        return self._is_banned

    def __repr__(self):
        return f"User(username={self._username}, transport={self._transport})"

    def __hash__(self):
        return hash(self._username)
