import asyncio

import getopt

from utils.functions import parse_opts
from .models import Gateway, Message
from .network import Request, Update
from .validators import validate_username, validate_message_delay
from utils.exceptions import ValidationError, ObjectDoesNotExist, ObjectAlreadyExist


class Handler:
    objects = {}

    @classmethod
    def register(cls, command: str):
        def decorator(func):
            cls.objects[command] = func
            return func
        return decorator

    @classmethod
    def handle(cls, request: Request) -> Update:
        if request.command not in cls.objects:
            return Update('ERROR', data=f'Unknown command "{request.command}"', target=request.client)

        handler = cls.objects[request.command]
        return handler(request)

    @classmethod
    def all(cls) -> list[callable]:
        return list(cls.objects.values())


@Handler.register('help')
def help(request: Request) -> Update:
    """help - команда возвращает описание всех существующих команд взаимодействия с сервером."""
    message = '\n'.join([handler.__doc__ for handler in Handler.all()])
    return Update('OK', data=message, target=request.client)


@Handler.register('exit')
def exit(request: Request) -> Update:
    """exit - команда разрывает соединение между вами и сервером."""
    return Update('OK', data=f'Bye, {request.client.username}!', target=request.client)


@Handler.register('rename')
def rename(request: Request) -> Update:
    """rename {username} - команда изменяет ваш никнейм на сервере."""
    new_username = request.data.get('value')
    try:
        validate_username(new_username)
    except ValidationError as err:
        error_message = str(err)
        return Update('ERROR', data=dict(error_message), target=request.client)
    try:
        Gateway.objects.get(username=new_username)
    except ObjectDoesNotExist:
        request.client.update(username=new_username)
        return Update('OK', data=f'Your username changed to "{new_username}".', target=request.client)

    return Update('ERROR', data=f'User with name "{new_username}" already exists.', target=request.client)


@Handler.register('users')
def users(request: Request) -> Update:
    """users - команда возвращает список всех пользователей на сервере."""
    message = 'Active users: ' + ' '.join([f'[{user.username}]' for user in Gateway.objects.all()])
    return Update('OK', data=message, target=request.client)


@Handler.register('send')
def send(request: Request) -> Update:
    """
    send {message} - команда отправляет сообщение всем пользователям.
    options: -u --username {username:str} - команда отправляет сообщение конкретному пользователю.
             -t --time {time:int} - команда отправляет сообщение через заданное количество секунд.
    """
    message = request.data['value']
    receiver_username = None
    delay = None
    target = Gateway.BROADCAST

    try:
        receiver_username, delay, message = parse_opts(message)
    except getopt.GetoptError as err:
        return Update('ERROR', data=f'Invalid options: {err}', target=request.client)

    if receiver_username:
        try:
            target = Gateway.objects.get(username=receiver_username)
        except ObjectDoesNotExist:
            return Update('ERROR', data=f'User with name "{receiver_username}" does not exist.', target=request.client)

    if delay:
        try:
            validate_message_delay(delay)
            delay = int(delay)
        except ValidationError as err:
            return Update('ERROR', data=str(err), target=request.client)

    message = Message.objects.create(text=message, sender=request.client, target=target)
    task = Message.send(message, delay=delay)

    return Update('OK', data=f'Message has been created.', target=request.client)



# @RequestHandler.register('cancel')
# def cancel(request: Request) -> None:
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


@Handler.register('history')
def history(request: Request) -> Update:
    """history - команда возвращает список всех сообщений, которые были отправлены в общем чате."""
    messages = Message.objects.all()[::-1]
    if messages:
        message = {'message': [msg.to_dict() for msg in messages]}
    else:
        message = 'Message history is empty.'
    return Update('OK', data=message, target=request.client)


# @RequestHandler.register('report')
# def report(request: Request) -> None:
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