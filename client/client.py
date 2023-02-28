import asyncio
import logging.config

from aioconsole import ainput

from server.core.network import DataTransport, Request, Update
from utils.settings import LOGGER
from utils.functions import print_update


logging.config.dictConfig(LOGGER)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, server_host: str = "127.0.0.1", server_port: int = 8000):
        self._server_host = server_host
        self._server_port = server_port
        self._transport: DataTransport | None = None
    
    async def __aenter__(self) -> 'Client':
        reader, writer = await asyncio.open_connection(self._server_host, self._server_port)
        self._transport = DataTransport(writer, reader)
        logger.debug("Connected to %s:%s", self._server_host, self._server_port)
        asyncio.ensure_future(self._receive_data())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._transport.close()
        logger.info("Connection to %s:%s is closed", self._server_host, self._server_port)
    
    async def _receive_data(self) -> None:
        while True:
            try:
                data = await self._transport.receive()
                update = Update.from_json(data)
                print_update(update)
            except ConnectionError:
                break
    
    async def execute(self, statement: str) -> None:
        command, *value = statement.split()
        request = Request(command, data=' '.join(value)).to_json()
        await self._transport.transfer(request)


async def init_client():
    async with Client() as client:
        while True:
            statement = await ainput()
            if statement == 'exit':
                await client.execute(statement)
                break
            asyncio.create_task(client.execute(statement))
