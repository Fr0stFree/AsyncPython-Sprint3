from typing import Callable, Awaitable, Type

from server.src.models.request import Request
from shared.schemas.actions import ActionTypes


class Router:
    def __init__(self) -> None:
        self._handlers: dict[ActionTypes, Callable[[Request], Awaitable[None]]] = {}
        self._error_handler: Callable[[Request, Exception], Awaitable[None]] | None = None
        self._unknown_handler: Callable[[Request], Awaitable[None]] | None = None

    async def handle(self, request: Request) -> None:
        handler = self._handlers.get(request.frame.type)
        if handler is None:
            await self._unknown_handler(request)  # possible None

        try:
            request.logger.info("Handling with '%s'", handler.__name__)
            await handler(request)
        except Exception as error:
            request.logger.exception("Error occurred while handling request")
            await self._error_handler(request, error)

    def on_action[T](self, action_type: ActionTypes) -> Callable[[T], T]:
        def decorator(handler: T) -> T:
            self._handlers[action_type] = handler
            return handler
        return decorator
