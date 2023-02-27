import asyncio

from .network import Request, Response
from .validators import validate_username
from .models.user import User
from .models.message import Message
from .exceptions import UsernameAlreadyTaken, UserDoesNotExist


class RequestHandler:
    HANDLERS = {}

    @classmethod
    def register(cls, command: str):
        def decorator(func):
            cls.HANDLERS[command] = func
            return func
        return decorator

    @classmethod
    def handle(cls, request: Request) -> Response:
        if request.command not in cls.HANDLERS:
            return Response('ERROR', data=f'Unknown command "{request.command}"')

        handler = cls.HANDLERS[request.command]
        response = handler(request)
        return response

    @classmethod
    def all_handlers(cls):
        return cls.HANDLERS.values()


@RequestHandler.register('help')
def help(request: Request) -> Response:
    """help - команда возвращает описание всех существующих команд взаимодействия с сервером."""
    data = '\n'.join([handler.__doc__ for handler in RequestHandler.all_handlers()])
    return Response('OK', data)


# @RequestHandler.register('exit')
# def exit(request: Request) -> Response:
#     """exit - команда разрывает соединение между вами и сервером."""
#     data = f'[SERVER] Bye, {request.user.username}!'
#     return Response('OK', data)
#
#
# @RequestHandler.register('rename')
# def rename(request: Request) -> Response:
#     """rename {username} - команда изменяет ваш никнейм на сервере."""
#     new_username = request.data.get('value')
#     is_valid, err_msg = validate_username(new_username)
#     if not is_valid:
#         return Response('ERROR', data=err_msg)
#
#     try:
#         UserManager().rename(request.user, new_username)
#     except UsernameAlreadyTaken:
#         return Response('ERROR', data=f'User with name "{new_username}" already exists.')
#     return Response('OK', data=f'Your username changed to "{new_username}".')
#
# @RequestHandler.register('users')
# def users(request: Request) -> Response:
#     """users - команда возвращает список всех пользователей на сервере."""
#     return Response('OK', data='Active users: ' + ' '.join([f'[{user.username}]' for user in UserManager().all()]))
#
#
# @RequestHandler.register('send')
# def send(request: Request) -> Response:
#     """
#     send {message} - команда отправляет сообщение всем пользователям.
#     options: -u --username {username:str} - команда отправляет сообщение конкретному пользователю.
#              -t --time {time:int} - команда отправляет сообщение через заданное количество секунд.
#     """
#     to_username = request.data.get('username')
#     if not to_username:
#         destination = UserManager().all()
#     else:
#         try:
#             destination = UserManager().get(username=to_username)
#         except UserDoesNotExist:
#             return Response('ERROR', data=f'User with name "{to_username}" does not exist.')
#     message = Message.objects.create(text=request.data.get('value'),
#                                      sender=request.user,
#                                      destination=destination)
#     asyncio.create_task(ChatManager.get_current().send(message))
#     return Response('OK', data=f'Your message was sent to all users.')


# @RequestHandler.register('send')
# async def send(request: Request) -> None:
#     """send {username} {message} - команда отправляет сообщение конкретному пользователю."""
#     if not request.user.is_authorized:
#         response = f'[SERVER] You are not authorized. Please, use "login" command.'
#         await request.user.send(response)
#         return
#
#     username, message = request.value.split(maxsplit=1)
#     looking_user = next(filter(lambda user: user.username == username, self._users), None)
#
#     if looking_user is None:
#         response = f'[SERVER] User with name "{username}" not found.'
#         await request.user.send(response)
#         return
#
#     message = Message(text=message, sender=request.user, receiver=looking_user)
#     self._mailbox.add(message)
#     await looking_user.send(response=str(message))


#
#
#
#
# @RequestHandler.register('schedule')
# async def schedule(request: Request) -> None:
#     """
#     schedule {time} {message} - команда отправляет сообщение в общий чат через указанное
#     количество секунд. Разрешено не более одного запланированного сообщения.
#     """
#     if not request.user.is_authorized:
#         response = f'[SERVER] You are not authorized. Please, use "login" command.'
#         await request.user.send(response)
#         return
#
#     delay, message = request.value.split(maxsplit=1)
#     is_valid, err_msg = validate_message_delay(delay)
#     if not is_valid:
#         response = f'[SERVER] {err_msg}'
#         await request.user.send(response)
#         return
#
#     request.value = message
#     scheduled_message = asyncio.create_task(execute_later(self.broadcast, int(delay), request))
#     self._scheduled_messages[request.user] = scheduled_message
#     response = f'[SERVER] Message "{message}" will be sent in {delay} seconds.'
#     await request.user.send(response)
#
#
# @RequestHandler.register('cancel')
# async def cancel(request: Request) -> None:
#     """cancel - команда отменяет запланированное сообщение."""
#     if not request.user.is_authorized:
#         response = f'[SERVER] You are not authorized. Please, use "login" command.'
#         await request.user.send(response)
#         return
#
#     task = self._scheduled_messages.get(request.user)
#     if task is None or task.done() or task.cancelled():
#         response = f'[SERVER] You have no scheduled messages.'
#     else:
#         task.cancel()
#         response = f'[SERVER] Scheduled message has been cancelled.'
#     await request.user.send(response)
#
#
# @RequestHandler.register('list')
# async def list(request: Request) -> None:
#     """list - команда возвращает список всех сообщений, которые были отправлены в общем чате."""
#     messages = self._mailbox.last()
#     if messages:
#         response = '\n'.join([str(message) for message in messages])
#     else:
#         response = '[SERVER] Message history is empty.'
#     await request.user.send(response)
#
#
# @RequestHandler.register('report')
# async def report(request: Request) -> None:
#     """report {username} - пожаловаться на пользователя."""
#     if not request.user.is_authorized:
#         response = f'[SERVER] You are not authorized. Please, use "login" command.'
#         await request.user.send(response)
#         return
#
#     username = request.value
#     looking_user = next(filter(lambda user: user.username == username, self._users), None)
#
#     if looking_user is None:
#         response = f'[SERVER] User with name "{username}" not found.'
#         await request.user.send(response)
#         return
#
#     if request.user in looking_user.reported_by:
#         response = f'[SERVER] You already reported "{looking_user.username}".'
#         await request.user.send(response)
#         return
#
#     looking_user.reported_by.add(request.user)
#     response_to_reported_user = f'[SERVER] User "{request.user.username}" reported you.'
#     response_to_reporter = f'[SERVER] You reported user "{looking_user.username}".'
#     await asyncio.gather(looking_user.send(response_to_reported_user),
#                          request.user.send(response_to_reporter))
#
#

#
#
# @RequestHandler.register('unknown')
# async def unknown(request: Request) -> None:
#     """В случае, если команда не была распознана, сервер возвращает сообщение об ошибке."""
#     response = f'[SERVER] Error "{request.command}" is unknown command.'
#     await request.user.send(response)