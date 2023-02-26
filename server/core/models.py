import asyncio
from typing import Self

from base.utils import DataTransport, execute_later


class User:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 username: str = 'Guest'):
        self._transport = DataTransport(writer, reader)
        self._username = username
        self._is_authorized = False
        self._is_banned = False
        self._reported_by: set[Self] = set()
        
    def __repr__(self):
        return f"User(username={self._username}, transport={self._transport})"
    
    def __hash__(self):
        return hash(self._username)

    @property
    def is_authorized(self):
        return self._is_authorized

    @property
    def username(self):
        return self._username
    
    @property
    def reported_by(self) -> set[Self]:
        return self._reported_by
    
    def authorize(self, username: str) -> None:
        self._is_authorized = True
        self._username = username
        
    async def send(self, response: str):
        await self._transport.transfer(response)
    
    async def receive(self) -> str:
        return await self._transport.receive()
        
    async def close_connection(self):
        await self._transport.close()
    



class MailBox:
    MESSAGE_LIFETIME = 60 * 60  # seconds
    MESSAGE_HISTORY_LIMIT = 20  # messages

    def __init__(self):
        self._messages: list[Message] = []
        
    def add(self, message: 'Message') -> None:
        self._messages.append(message)
        asyncio.create_task(execute_later(self._messages.remove, self.MESSAGE_LIFETIME, message))
    
    def last(self) -> list['Message']:
        messages = [*filter(lambda message: message.is_broadcast, self._messages)]
        return messages[-self.MESSAGE_HISTORY_LIMIT:]

    
class Message:
    def __init__(self, text: str, sender: User, receiver: User = None):
        self._text = text
        self._sender = sender
        self._receiver = receiver
    
    @property
    def is_broadcast(self):
        return self._receiver is None
        
    def __str__(self):
        if self.is_broadcast:
            return f"[BROADCAST] {self._sender.username} >>> {self._text}"
        return f"[PRIVATE] {self._sender.username} >>> {self._text}"
