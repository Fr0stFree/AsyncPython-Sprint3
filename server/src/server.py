import asyncio
import logging.config
import uuid
from typing import Callable, Self, Type

from server.src.handlers.base_error_handler import BaseErrorHandler
from server.src.handlers.base_handler import BaseHandler
from server.src.models import ClientManager, Client
from server.src.settings import ServerSettings
from shared.schemas.actions import ActionFrame, ActionTypes


class Server:
    def __new__(cls, *args, **kwargs) -> 'Server':
        logging_config = args[0].logging
        logging.config.dictConfig(logging_config)
        return super().__new__(cls)

    def __init__(
        self,
        settings: ServerSettings,
        client_manager_factory: Callable[[], ClientManager] = ClientManager
    ) -> None:
        self._server: asyncio.Server | None = None
        self._settings = settings
        self._server_logger = logging.getLogger("server")
        self._clients = client_manager_factory()
        self._handlers: dict[ActionTypes, Type[BaseHandler]] = {}
        self._clients = client_manager_factory()
        self._exception_handlers: dict[Type[Exception], Type[BaseErrorHandler]] = {}
        self._unknown_handler: Type[BaseHandler] | None = None

    async def start(self) -> None:
        self._server_logger.info("Starting server on %s:%s...", self._settings.host, self._settings.port)
        self._server = await asyncio.start_server(self._main_callback, self._settings.host, self._settings.port)
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

    async def _main_callback(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client = self._clients.create(reader, writer)
        self._server_logger.info("New connection from %s", client)
        while True:
            try:
                data = await client.listen()
            except ConnectionError:
                self._server_logger.error("Connection closed by %s", client)
                await self._clients.drop(client)
                break

            await self._handle_client_request(data, client)

    async def _handle_client_request(self, data: str, client: Client) -> None:
        logger = logging.LoggerAdapter(self._server_logger, extra={"request_id": str(uuid.uuid4())})
        frame = ActionFrame.model_validate_json(data)

        Handler = self._handlers.get(frame.type, self._unknown_handler)
        handler = Handler(frame.payload, client, logger)
        try:
            await handler()
        except Exception as error:
            ExcHandler = self._exception_handlers.get(type(error), BaseErrorHandler)
            exc_handler = ExcHandler(frame.payload, client, error, logger)
            await exc_handler()

    def on_action(self, action_type: ActionTypes, handler: Type[BaseHandler]) -> Self:
        self._handlers[action_type] = handler
        return self

    def on_exception(self, error: Type[Exception], handler: Type[BaseErrorHandler]) -> Self:
        self._exception_handlers[error] = handler
        return self

    def on_unknown_action(self, handler: Type[BaseHandler]) -> Self:
        self._unknown_handler = handler
        return self
