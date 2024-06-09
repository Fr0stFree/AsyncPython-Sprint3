import asyncio
import logging.config
import uuid

from server.src.handlers import error_handler, send_message_handler, broadcast_message_handler, \
    unknown_action_handler, logout_handler
from server.src.models.client import ClientManager
from server.src.models.request import Request
from server.src.router import Router
from server.src.settings import ServerSettings
from shared.schemas.actions import ActionFrame, ActionTypes


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
        self._router = Router()
        self._setup_routes(self._router)

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
            await self._router.handle(request)
            request.logger.debug("Request '%s' has been handled", request)

    def _setup_routes(self, router: Router) -> None:
        router.register_action_handler(ActionTypes.BROADCAST_MESSAGE, broadcast_message_handler) \
            .register_action_handler(ActionTypes.SEND_MESSAGE, send_message_handler) \
            .register_action_handler(ActionTypes.LOGOUT, logout_handler) \
            .register_action_handler(ActionTypes.HELP, unknown_action_handler) \
            .register_unknown_handler(unknown_action_handler) \
            .register_error_handler(error_handler)
