import asyncio
import logging.config

from utils.settings import LOGGER
from utils.functions import generate_random_username
from .core.models.user import  UserManager
from .core.models.message import ChatManager
from .core.network import Request
from .core.handlers import RequestHandler


logging.config.dictConfig(LOGGER)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self._host = host
        self._port = port
        self._server: asyncio.Server | None = None
        self._incoming_queue: asyncio.Queue = asyncio.Queue()
        self._outgoing_queue: asyncio.Queue = asyncio.Queue()
        self._user_manager = UserManager()
        self._chat_manager = ChatManager(gateway=self._outgoing_queue)

    def listen(self):
        """Метод запускает сервер и ожидает подключения клиентов"""
        asyncio.run(self._start_server())
    
    async def _start_server(self):
        logger.debug("Starting server on %s:%s", self._host, self._port)
        self._server = await asyncio.start_server(self._handle_connection, self._host, self._port)
        async with self._server:
            logger.debug("Server is ready to accept connections on %s:%s", self._host, self._port)
            asyncio.ensure_future(self._handle_incoming_data())
            asyncio.ensure_future(self._handle_outgoing_data())
            await self._server.serve_forever()

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        user = self._user_manager.create(reader, writer, username=generate_random_username())
        while True:
            try:
                data = await self._user_manager.receive(user)
            except ConnectionError:
                break
            await self._incoming_queue.put((user, data))

        await self._user_manager.remove(user)

    async def _handle_incoming_data(self):
        while True:
            user, data = await self._incoming_queue.get()
            request = Request.from_json(data)
            request.user = user
            logger.debug('Got request: %s ', request)
            response = RequestHandler.handle(request)
            await self._outgoing_queue.put((user, response))
            self._incoming_queue.task_done()

    async def _handle_outgoing_data(self):
        while True:
            destination, data = await self._outgoing_queue.get()
            json_data = data.to_json()
            if isinstance(destination, list):
                tasks = [self._user_manager.send(user, json_data) for user in destination]
                await asyncio.gather(*tasks)
            else:
                await self._user_manager.send(destination, json_data)
            self._outgoing_queue.task_done()
