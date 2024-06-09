import asyncio
from types import TracebackType
from typing import Self, Type

from aioconsole import ainput

from client.src.printer import Printer
from client.src.settings import ClientSettings
from shared.schemas import actions
from shared.schemas.actions import ActionTypes, ActionFrame
from shared.schemas.notifications import NotificationFrame
from shared.transport import DataTransport


class Client:
    def __init__(self, settings: ClientSettings) -> None:
        self._settings = settings
        self._printer = Printer()
        self._transport: DataTransport | None = None
        self._receiver: asyncio.Task | None = None

    async def __aenter__(self) -> Self:
        self._printer.info(f"Connecting to {self._settings.host}:{self._settings.port}...")
        try:
            reader, writer = await asyncio.open_connection(self._settings.host, self._settings.port)
        except ConnectionRefusedError as error:
            self._printer.error("Connection refused")
            raise error
        self._transport = DataTransport(writer, reader)
        self._receiver = asyncio.ensure_future(self._receive_data())
        self._printer.success("Successfully connected")
        return self

    async def __aexit__(self, exc_type: Type[BaseException], exc: BaseException, tb: TracebackType) -> None:
        self._printer.info("Disconnecting from the server...")
        self._receiver.cancel()
        await self._transport.close()
        self._printer.success("Successfully disconnected")

    async def _receive_data(self) -> None:
        while True:
            data = await self._transport.receive()
            frame = NotificationFrame.model_validate_json(data)
            self._printer.message(frame)

    async def send(self, frame: ActionFrame) -> None:
        await self._transport.transfer(frame.model_dump_json())

    async def handle_input(self) -> None:
        while True:
            statement = await ainput()
            match statement.split():
                case ["send", *text]:
                    payload = actions.BroadcastMessagePayload(text=" ".join(text))
                    frame = actions.BroadcastMessageActionFrame(payload=payload)
                    await self.send(frame)
                case ["help"]:
                    frame = ActionFrame(type=ActionTypes.HELP)
                    await self.send(frame)
                case ["exit" | "quit" | "logout"]:
                    frame = ActionFrame(type=ActionTypes.LOGOUT)
                    await self.send(frame)
                    break
                case _:
                    text = f"Unknown command: '{statement}'. Use 'help' to see available commands."
                    self._printer.error(text)
