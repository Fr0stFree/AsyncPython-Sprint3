import asyncio
from types import TracebackType
from typing import Self, Type

from aioconsole import ainput

from client.src.printer import Printer
from client.src.settings import ClientSettings
from shared.messages import Message
from shared.requests import Actions, RequestData, SendMessageRequestData, MessageTypes
from shared.transport import DataTransport


class Client:
    def __init__(self, settings: ClientSettings) -> None:
        self._settings = settings
        self._printer = Printer()
        self._transport: DataTransport | None = None
        self._request_queue: asyncio.Queue = asyncio.Queue()
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
        await self._request_queue.join()
        self._receiver.cancel()
        await self._transport.close()
        self._printer.success("Successfully disconnected")

    async def _receive_data(self) -> None:
        while True:
            data = await self._transport.receive()
            message = Message.model_validate_json(data)
            self._printer.message(message)

    async def send(self, data: RequestData) -> None:
        await self._transport.transfer(data.model_dump_json())

    async def handle_input(self) -> None:
        while True:
            statement = await ainput()
            match statement.split():
                case [Actions.SEND_MESSAGE.value, *text]:
                    data = SendMessageRequestData(
                        text=" ".join(text), type=MessageTypes.BROADCAST, to=MessageTypes.BROADCAST
                    )
                    await self.send(data)

                case [Actions.HELP.value]:
                    await self.send(RequestData(action=Actions.HELP))

                case [Actions.LOGOUT.value]:
                    await self.send(RequestData(action=Actions.LOGOUT))
                    break
                case _:
                    self._printer.error(f"Unknown command: '{statement}'. Use 'help' to see available commands.")
