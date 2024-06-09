import asyncio
import logging.config
import uuid

from server.src.handlers import router
from server.src.models.client import ClientManager
from server.src.models.request import Request
from server.src.settings import ServerSettings
from shared.schemas.actions import ActionFrame


class Server:
    def __new__(cls, *args, **kwargs) -> 'Server':
        logging_config = args[0].logging
        logging.config.dictConfig(logging_config)
        return super().__new__(cls)

    def __init__(self, settings: ServerSettings) -> None:
        self._server: asyncio.Server | None = None
        self._settings = settings
        self._server_logger = logging.getLogger("server")
        self._clients = ClientManager()

    async def start(self) -> None:
        self._server_logger.info("Starting server on %s:%s...", self._settings.host, self._settings.port)
        self._server = await asyncio.start_server(self._on_client_connected, self._settings.host, self._settings.port)
        self._server_logger.info("Server is started")

    async def serve(self) -> None:
        if not isinstance(self._server, asyncio.Server):
            raise RuntimeError("Server is not started")

        async with self._server:
            self._server_logger.info("Server is listening on %s:%s...", self._settings.host, self._settings.port)
            await self._server.serve_forever()

    async def stop(self) -> None:
        if not isinstance(self._server, asyncio.Server):
            raise RuntimeError("Server is not started")

        self._server.close()
        await self._server.wait_closed()
        self._server = None
        self._server_logger.debug("Server is stopped")

    async def _on_client_connected(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client = self._clients.create(reader, writer)
        self._server_logger.info("New connection from %s", client)
        while True:
            raw = await client.listen()
            request = Request(
                client=client,
                logger=logging.LoggerAdapter(self._server_logger, extra={"request_id": str(uuid.uuid4())}),
                frame=ActionFrame.model_validate_json(raw),
            )
            request.logger.debug("Received request '%s'", request)
            await router.handle(request)
            request.logger.debug("Request '%s' has been handled", request)
