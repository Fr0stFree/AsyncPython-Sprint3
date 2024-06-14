from typing import override

from server.src.handlers.base_handler import BaseHandler


class LogoutHandler(BaseHandler):
    payload_validator = None

    @override
    async def handle(self) -> None:
        await self.clients.drop(self.client)
