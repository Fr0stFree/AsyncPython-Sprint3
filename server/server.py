import asyncio
import logging.config

from utils.settings import LOGGER
from .core.models import Gateway
from .core.network import Request, Update
from .core.handlers import Handler



logging.config.dictConfig(LOGGER)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self._host = host
        self._port = port
        self._server: asyncio.Server | None = None


    def listen(self):
        """Метод запускает сервер и ожидает подключения клиентов"""
        asyncio.run(self._start_server())
    
    async def _start_server(self):
        logger.debug("Starting server on %s:%s", self._host, self._port)
        self._server = await asyncio.start_server(self._handle_connection, self._host, self._port)
        async with self._server:
            logger.debug("Server is ready to accept connections on %s:%s", self._host, self._port)
            await self._server.serve_forever()

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client = Gateway.objects.create(reader=reader, writer=writer, username='test')
        logger.debug("New connection from %s", client)
        while True:
            try:
                request: Request = await Gateway.receive(client)
                update: Update = Handler.handle(request)
                await Gateway.send_update(update)
            except ConnectionError:
                break

        logger.debug("Connection from %s is closed", client)
        await Gateway.close(client)
