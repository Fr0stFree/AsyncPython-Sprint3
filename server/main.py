import asyncio

from server.src.handlers import SendMessageHandler, BroadcastMessageHandler, UnknownActionHandler, LogoutHandler, \
    BaseErrorHandler
from server.src.server import Server
from server.src.settings import ServerSettings
from shared.schemas.actions import ActionTypes


async def main():
    settings = ServerSettings()
    server = Server(settings) \
        .on_action(ActionTypes.SEND_MESSAGE, SendMessageHandler) \
        .on_action(ActionTypes.BROADCAST_MESSAGE, BroadcastMessageHandler) \
        .on_action(ActionTypes.HELP, UnknownActionHandler) \
        .on_action(ActionTypes.LOGOUT, LogoutHandler) \
        .on_unknown_action(UnknownActionHandler) \
        .on_exception(Exception, BaseErrorHandler)

    try:
        await server.start()
        await server.serve()
    finally:
        await server.stop()


if __name__ == '__main__':
    asyncio.run(main())
