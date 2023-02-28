import asyncio

from utils.functions import execute_later
from utils.classes import Model
from server.core.network import DataTransport, Request, Update


class Gateway(Model):
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    username: str
    is_banned: bool
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transport = DataTransport(writer=self.writer, reader=self.reader)

    def __str__(self):
        return f'client({self.username} transport={self.transport})'

    @classmethod
    async def close(cls, self):
        await self.transport.close()
        self.remove()

    @classmethod
    async def receive(cls, self) -> Request:
        data = await self.transport.receive()
        request = Request.from_json(data)
        request.client = self
        return request

    @classmethod
    async def send_update(cls, update: Update) -> None:
        if update.target == Gateway.BROADCAST:
            tasks = [client.transport.transfer(update.to_json()) for client in cls.objects.all()]
            await asyncio.gather(*tasks)
        else:
            client = update.target
            await client.transport.transfer(update.to_json())

    class BROADCAST:
        pass



class Message(Model):
    text: str
    sender: Gateway
    target: Gateway | Gateway.BROADCAST

    def __str__(self):
        return f'Message({self.sender.username} >> {self.target} text={self.text})'

    def to_dict(self) -> dict:
        return {'text': self.text,
                'sender': self.sender.username,
                'target': str(self.target)}

    @classmethod
    def send(cls, message: 'Message', delay: int | None) -> asyncio.Task:
        update = Update(status='MSG', data=message.to_dict(), target=message.target)
        if delay is None:
            return asyncio.create_task(Gateway.send_update(update))
        return asyncio.create_task(execute_later(Gateway.send_update, update=update, delay=delay))
