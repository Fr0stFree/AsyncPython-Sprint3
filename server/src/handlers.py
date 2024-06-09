import asyncio
from typing import Callable, Awaitable

from server.src.models.request import Request
from server.src.models.client import ClientManager
from server.src.models.messages import ServerMessage
from shared.requests import Actions, MessageTypes, SendMessageRequestData


class ActionHandler:
    def __init__(self, client_manager: ClientManager) -> None:
        self._clients = client_manager
        self._handlers: dict[Actions, Callable[[Request], Awaitable[None]]] = {
            Actions.SEND_MESSAGE: self._on_send_message,
            Actions.LOGOUT: self._on_logout,
            Actions.UNKNOWN: self._on_unknown_action,
        }

    async def handle(self, request: Request) -> None:
        handler = self._handlers.get(request.action) or self._handlers[Actions.UNKNOWN]
        try:
            request.logger.info("Handling with '%s'", handler.__name__)
            await handler(request)
        except Exception as error:
            message = ServerMessage(to=request.client.user.username, ok=False, text="Something went wrong.")
            request.logger.exception("Error occurred while handling request")
            await request.reply(message)
            raise error

    async def _on_send_message(self, request: Request) -> None:
        data = SendMessageRequestData.model_validate(request.data)

        match data.type:
            case MessageTypes.PRIVATE:
                client = self._clients.get(data.to)
                if client is None:
                    request.logger.info("User '%s' not found", data.to)
                    message = ServerMessage(
                        to=request.client.user.username, text=f"User '{data.to}' not found", ok=False
                    )
                    return await request.reply(message)

                message = ServerMessage(to=data.to, text=data.text, sender=request.client.user.username)
                await client.send(message)
                request.logger.info("Message sent to '%s'", data.to)
                return

            case MessageTypes.BROADCAST:
                message = ServerMessage(to=MessageTypes.BROADCAST, text=data.text, sender=request.client.user.username)
                tasks = [client.send(message) for client in self._clients.all()]
                await asyncio.gather(*tasks)
                request.logger.info("Message broadcasted successfully")
                return

    async def _on_logout(self, request: Request) -> None:
        await self._clients.drop(request.client)
        request.logger.info("Client '%s' dropped", request.client.user.username)

    async def _on_unknown_action(self, request: Request) -> None:
        message = ServerMessage(to=request.client.user.username, text='Unknown command', ok=False)
        await request.reply(message)
