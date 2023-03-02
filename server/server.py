import asyncio
import logging.config

from settings import Settings
from utils.functions import generate_random_name
from .core.models import Gateway
from .core.network import Request, Update
from .core.handlers import Handler


settings = Settings()
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._server: asyncio.Server | None = None

    async def start(self) -> None:
        """Инициализация сервера."""
        logger.debug("Starting server on %s:%s", self._host, self._port)
        self._server = await asyncio.start_server(self._handle_connection, self._host, self._port)

    async def serve(self) -> None:
        """Запуск сервера и ожидание подключений."""
        async with self._server:
            logger.debug("Server is ready to accept connections on %s:%s", self._host, self._port)
            await self._server.serve_forever()

    async def stop(self) -> None:
        """Остановка сервера."""
        self._server.close()
        await self._server.wait_closed()
        self._server = None
        logger.debug("Server is stopped")

    @staticmethod
    async def _handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client = Gateway.objects.create(reader=reader, writer=writer, username=generate_random_name())
        logger.debug("New connection from %s", client)
        while True:
            try:
                request: Request = await Gateway.receive(client)
                logger.debug("Received request from %s.", client)
                update: Update = Handler.handle(request)
                await Gateway.send_update(update)
            except ConnectionError:
                break

        logger.debug("Connection from %s is closed", client)
        await Gateway.close(client)
