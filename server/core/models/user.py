import asyncio

from utils.classes import Model
from server.core.network import DataTransport


class User(Model):
    transport: DataTransport
    username: str
    is_banned: bool
    
    def __init__(self):
        super().__init__()

    def __str__(self):
        return f'User({self.username})'
    
    async def remove(self) -> None:
        super().remove()
        await self.transport.close()
    
    async def send(self, data: str):
        await self.transport.transfer(data)
    
    async def receive(self) -> str:
        return await self.transport.receive()