import asyncio
import logging.config

from base.settings import LOGGER
from base.utils import Request, execute_later
from core.models import User, Message, MailBox
from core.commands import CommandHandler
from core.validators import validate_username, validate_message_delay

logging.config.dictConfig(LOGGER)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self._host = host
        self._port = port
        self._server: asyncio.Server | None = None
        self._users: set[User] = set()
        self._mailbox: MailBox = MailBox()
        self._scheduled_messages: dict[User, asyncio.Task] = {}
    
    def listen(self):
        asyncio.run(self._start_server())
    
    async def _start_server(self):
        logger.debug("Starting server on %s:%s", self._host, self._port)
        self._server = await asyncio.start_server(self._handle_connection, self._host, self._port)
        async with self._server:
            logger.debug("Server is ready to accept connections on %s:%s", self._host, self._port)
            await self._server.serve_forever()
    
    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        user = self._open_connection(reader, writer)
        while True:
            try:
                data = await user.receive()
                request = Request.from_json(data)
                request.user = user
                logger.debug('Got request: %s', request)
                request_handler = CommandHandler.get_handler(request.command)
                await request_handler(self, request)
            except ConnectionError:
                break
        await self._close_connection(user)
    
    def _open_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> User:
        user = User(reader, writer)
        logger.info("New connection from %s", user)
        self._users.add(user)
        return user
    
    async def _close_connection(self, user: User):
        logger.info("Connection with %s has been closed", user)
        self._users.remove(user)
        await user.close_connection()

    @CommandHandler.register('help')
    async def help(self, request: Request):
        """help - команда возвращает описание всех существующих команд взаимодействия с сервером."""
        response = ('[SERVER] Possible commands:\n' +
                    '\n'.join([handler.__doc__ for handler in CommandHandler.HANDLERS.values()]))
        await request.user.send(response)
        
    @CommandHandler.register('exit')
    async def exit(self, request: Request):
        """exit - команда разрывает соединение между вами и сервером."""
        response = f'[SERVER] Bye, {request.user.username}!'
        await request.user.send(response)
        raise ConnectionError

    @CommandHandler.register('login')
    async def login(self, request: Request) -> None:
        """login {username} - команда изменяет ваш никнейм на сервере."""
        new_username = request.value
        is_valid, err_msg = validate_username(new_username)
        if not is_valid:
            response = f'[SERVER] {err_msg}'
            await request.user.send(response)
            return

        if new_username in [user.username for user in self._users]:
            response = f'[SERVER] User with name "{new_username}" already exists.'
            await request.user.send(response)
            return
    
        request.user.authorize(username=new_username)
        response = f'[SERVER] Now your name is "{new_username}".'
        await request.user.send(response)
    
    @CommandHandler.register('broadcast')
    async def broadcast(self, request: Request) -> None:
        """broadcast {message} - команда отправляет сообщение всем пользователям сервера."""
        if not request.user.is_authorized:
            response = f'[SERVER] You are not authorized. Please, use "login" command.'
            await request.user.send(response)
            return
        
        message = Message(text=request.value, sender=request.user)
        self._mailbox.add(message)

        coroutines = [user.send(response=str(message)) for user in self._users]
        await asyncio.gather(*coroutines)

    @CommandHandler.register('send')
    async def send(self, request: Request) -> None:
        """send {username} {message} - команда отправляет сообщение конкретному пользователю."""
        if not request.user.is_authorized:
            response = f'[SERVER] You are not authorized. Please, use "login" command.'
            await request.user.send(response)
            return
        
        username, message = request.value.split(maxsplit=1)
        looking_user = next(filter(lambda user: user.username == username, self._users), None)

        if looking_user is None:
            response = f'[SERVER] User with name "{username}" not found.'
            await request.user.send(response)
            return
        
        message = Message(text=message, sender=request.user, receiver=looking_user)
        self._mailbox.add(message)
        await looking_user.send(response=str(message))
        
    @CommandHandler.register('schedule')
    async def schedule(self, request: Request) -> None:
        """
        schedule {time} {message} - команда отправляет сообщение в общий чат через указанное
        количество секунд. Разрешено не более одного запланированного сообщения.
        """
        if not request.user.is_authorized:
            response = f'[SERVER] You are not authorized. Please, use "login" command.'
            await request.user.send(response)
            return
        
        delay, message = request.value.split(maxsplit=1)
        is_valid, err_msg = validate_message_delay(delay)
        if not is_valid:
            response = f'[SERVER] {err_msg}'
            await request.user.send(response)
            return

        request.value = message
        scheduled_message = asyncio.create_task(execute_later(self.broadcast, int(delay), request))
        self._scheduled_messages[request.user] = scheduled_message
        response = f'[SERVER] Message "{message}" will be sent in {delay} seconds.'
        await request.user.send(response)
        
    @CommandHandler.register('cancel')
    async def cancel(self, request: Request) -> None:
        """cancel - команда отменяет запланированное сообщение."""
        if not request.user.is_authorized:
            response = f'[SERVER] You are not authorized. Please, use "login" command.'
            await request.user.send(response)
            return
        
        task = self._scheduled_messages.get(request.user)
        if task is None or task.done() or task.cancelled():
            response = f'[SERVER] You have no scheduled messages.'
        else:
            task.cancel()
            response = f'[SERVER] Scheduled message has been cancelled.'
        await request.user.send(response)

    @CommandHandler.register('list')
    async def list(self, request: Request) -> None:
        """list - команда возвращает список всех сообщений, которые были отправлены в общем чате."""
        messages = self._mailbox.last()
        if messages:
            response = '\n'.join([str(message) for message in messages])
        else:
            response = '[SERVER] Message history is empty.'
        await request.user.send(response)
        
    @CommandHandler.register('report')
    async def report(self, request: Request) -> None:
        """report {username} - пожаловаться на пользователя."""
        if not request.user.is_authorized:
            response = f'[SERVER] You are not authorized. Please, use "login" command.'
            await request.user.send(response)
            return
        
        username = request.value
        looking_user = next(filter(lambda user: user.username == username, self._users), None)

        if looking_user is None:
            response = f'[SERVER] User with name "{username}" not found.'
            await request.user.send(response)
            return
        
        if request.user in looking_user.reported_by:
            response = f'[SERVER] You already reported "{looking_user.username}".'
            await request.user.send(response)
            return
        
        looking_user.reported_by.add(request.user)
        response_to_reported_user = f'[SERVER] User "{request.user.username}" reported you.'
        response_to_reporter = f'[SERVER] You reported user "{looking_user.username}".'
        await asyncio.gather(looking_user.send(response_to_reported_user),
                             request.user.send(response_to_reporter))
    
    @CommandHandler.register('users')
    async def users(self, request: Request) -> None:
        """users - команда возвращает список всех пользователей на сервере."""
        response = 'Active users: ' + ' '.join([f'[{user.username}]' for user in self._users])
        await request.user.send(response)
    
    @CommandHandler.register('unknown')
    async def unknown(self, request: Request) -> None:
        """В случае, если команда не была распознана, сервер возвращает сообщение об ошибке."""
        response = f'[SERVER] Error "{request.command}" is unknown command.'
        await request.user.send(response)
    

if __name__ == "__main__":
    server = Server()
    server.listen()
