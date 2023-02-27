import asyncio
from typing import Union

from server.core.network import Response
from utils.classes import Singleton
from .user import User


class ChatManager(metaclass=Singleton):
    MESSAGE_LIFETIME = 60 * 60  # seconds
    MESSAGE_HISTORY_LIMIT = 20  # messages

    def __init__(self, gateway: asyncio.Queue):
        self._storage: list[Message] = []
        self._gateway = gateway

    async def send(self, message: 'Message') -> None:
        self._storage.append(message)
        response = Response('MSG', data=message.to_dict())
        await self._gateway.put((message.destination, response))
        await asyncio.sleep(self.MESSAGE_LIFETIME)
        self._storage.remove(message)

    def last(self) -> list['Message']:
        return self._storage[-self.MESSAGE_HISTORY_LIMIT:]

    @classmethod
    def get_current(cls) -> 'ChatManager':
        return cls._instances[cls]


class Message:
    def __init__(self, text: str, sender: User, destination: Union[User, list[User]]):
        self._text = text
        self._sender = sender
        self._destination = destination
        self._is_broadcast = isinstance(destination, list)

    @property
    def destination(self) -> Union[User, list[User]]:
        return self._destination

    def to_dict(self) -> dict:
        return {'text': self._text, 'sender': self._sender.username, 'is_broadcast': self._is_broadcast}


