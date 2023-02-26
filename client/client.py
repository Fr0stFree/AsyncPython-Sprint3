import asyncio
import logging.config
from typing import Self

from aioconsole import ainput

from base.settings import LOGGER
from base.utils import DataTransport, Request


logging.config.dictConfig(LOGGER)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, server_host="127.0.0.1", server_port=8000):
        self._server_host = server_host
        self._server_port = server_port
        self._data_queue = asyncio.Queue()
        self._transport: DataTransport | None = None
    
    async def __aenter__(self) -> Self:
        logger.debug("Connecting to %s:%s", self._server_host, self._server_port)
        reader, writer = await asyncio.open_connection(self._server_host, self._server_port)
        self._transport = DataTransport(writer, reader)
        logger.debug("Connected to %s:%s", self._server_host, self._server_port)
        asyncio.ensure_future(self._receive_data())
        asyncio.ensure_future(self._transfer_data())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._transport.close()
        logger.info("Connection to %s:%s is closed", self._server_host, self._server_port)
    
    async def _receive_data(self) -> None:
        while True:
            try:
                data = await self._transport.receive()
                print(data)
            except ConnectionError:
                break
    
    async def _transfer_data(self) -> None:
        while True:
            data = await self._data_queue.get()
            await self._transport.transfer(data)
            self._data_queue.task_done()
    
    def send_statement(self, statement: str) -> None:
        command, *value = statement.split()
        value = ' '.join(value)
        data = Request(command, value).to_json()
        self._data_queue.put_nowait(data)
    

async def init_client():
    async with Client() as client:
        while True:
            statement = await ainput("")
            client.send_statement(statement)
