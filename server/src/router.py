from typing import Callable, Awaitable, Self

from server.src.models.request import Request
from shared.schemas.actions import ActionTypes


class Router:
    def __init__(self) -> None:
        self._handlers: dict[ActionTypes, Callable[[Request], Awaitable[None]]] = {}
        self._error_handler: Callable[[Request, Exception], Awaitable[None]] | None = None
        self._unknown_handler: Callable[[Request], Awaitable[None]] | None = None

    async def handle(self, request: Request) -> None:
        handler = self._handlers.get(request.frame.type)
        if handler is None and self._unknown_handler is not None:
            await self._unknown_handler(request)
            return

        try:
            request.logger.info("Handling with '%s'", handler.__name__)
            await handler(request)
        except Exception as error:
            request.logger.exception("Error occurred while handling request")
            await self._error_handler(request, error)

    def register_action_handler(self, action_type: ActionTypes, handler: Callable[[Request], Awaitable[None]]) -> Self:
        self._handlers[action_type] = handler
        return self

    def register_unknown_handler(self, handler: Callable[[Request], Awaitable[None]]) -> Self:
        self._unknown_handler = handler
        return self

    def register_error_handler(self, handler: Callable[[Request, Exception], Awaitable[None]]) -> Self:
        self._error_handler = handler
        return self
