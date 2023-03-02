import asyncio

import getopt

from settings import Settings
from utils.functions import parse_opts, execute_later
from .models import Gateway, Message
from .network import Request, Update
from .validators import validate_username, validate_message_delay
from utils.exceptions import ValidationError, ObjectDoesNotExist


settings = Settings()


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
            return Update('ERROR', data=f'Unknown command "{request.command}"',
                          target=request.client)

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
def exit(request: Request) -> None:
    """exit - команда разрывает соединение между вами и сервером."""
    raise ConnectionError


@Handler.register('rename')
def rename(request: Request) -> Update:
    """rename {username} - команда изменяет ваш никнейм на сервере."""
    new_username = request.data
    try:
        validate_username(new_username)
    except ValidationError as err:
        error_message = str(err)
        return Update('ERROR', data=error_message, target=request.client)
    try:
        Gateway.objects.get(username=new_username)
    except ObjectDoesNotExist:
        request.client.update(username=new_username)
        return Update('OK', data=f'Your username changed to "{new_username}".',
                      target=request.client)

    return Update('ERROR', data=f'User with name "{new_username}" already exists.',
                  target=request.client)


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
    message = request.data
    receiver_username = None
    delay = None
    target = Gateway.BROADCAST
    
    if request.client.is_banned:
        return Update('ERROR', data=f'You are still banned!', target=request.client)
    
    try:
        receiver_username, delay, message = parse_opts(message)
    except getopt.GetoptError as err:
        return Update('ERROR', data=f'Invalid options: {err}', target=request.client)

    if receiver_username:
        try:
            target = Gateway.objects.get(username=receiver_username)
        except ObjectDoesNotExist:
            return Update('ERROR', data=f'User with name "{receiver_username}" does not exist.',
                          target=request.client)
    if delay:
        try:
            validate_message_delay(delay)
            delay = int(delay)
        except ValidationError as err:
            return Update('ERROR', data=str(err), target=request.client)

    Message.objects.create(text=message, sender=request.client, target=target).send(delay=delay)
    return Update('OK', data=f'Message has been created.', target=request.client)


@Handler.register('cancel')
def cancel(request: Request) -> Update:
    """cancel - команда отменяет последнее запланированное сообщение."""
    try:
        message = Message.objects.get(sender=request.client, status='PENDING')
    except ObjectDoesNotExist:
        return Update('ERROR', data='You have no scheduled messages.', target=request.client)
    message.cancel()
    return Update('OK', data=f'Message "{message.text}" has been canceled.', target=request.client)


@Handler.register('history')
def history(request: Request) -> Update:
    """history - команда возвращает список всех сообщений, которые были отправлены в общем чате."""
    messages = Message.objects.filter(target=any([Gateway.BROADCAST, request.client]),
                                      status='FINISHED')[:20]
    if messages:
        message = '\n'.join([str(msg) for msg in messages])
    else:
        message = 'Message history is empty.'
    return Update('OK', data=message, target=request.client)


@Handler.register('report')
def report(request: Request) -> Update:
    """report {username:str} - пожаловаться на пользователя."""
    username = request.data
    try:
        intruder = Gateway.objects.get(username=username)
    except ObjectDoesNotExist:
        return Update('ERROR', data=f'User with name "{username}" does not exist.',
                      target=request.client)
    if request.client in intruder.reported_by:
        return Update('ERROR', data=f'You have already reported user "{username}".',
                      target=request.client)
    reporters = intruder.reported_by
    reporters.add(request.client)
    if len(reporters) >= settings.REPORTS_TO_BAN:
        intruder.ban()
        ban_notification = Update('ERROR', data=f'You have been banned for {settings.BAN_TIME} seconds.',
                                  target=intruder)
        asyncio.create_task(Gateway.send_update(ban_notification))
        
        unban_task = asyncio.create_task(execute_later(func=intruder.unban, delay=settings.BAN_TIME))
        unban_notification = Update('OK', data=f'You able to send messages again.', target=intruder)
        unban_task.add_done_callback(
            lambda task: asyncio.create_task(Gateway.send_update(unban_notification))
        )
    else:
        intruder.update(reported_by=reporters)
    return Update('OK', data=f'User "{username}" has been reported.', target=request.client)
