import datetime as dt

from server.src.models.client import ClientManager, Client, LoggerLike
from shared.schemas.notifications import ErrorNotificationPayload, ErrorNotificationFrame


class BaseErrorHandler:
    clients: ClientManager = ClientManager.get_current()

    __slots__ = ('_payload', '_client', '_logger', '_error')

    def __init__(self, payload: dict, client: Client, error: Exception, logger: LoggerLike) -> None:
        self._payload = payload
        self._client = client
        self._logger = logger
        self._error = error

    @property
    def payload(self) -> dict:
        return self._payload

    @property
    def client(self) -> Client:
        return self._client

    @property
    def logger(self) -> LoggerLike:
        return self._logger

    @property
    def error(self) -> Exception:
        return self._error

    async def __call__(self, *args, **kwargs) -> None:
        self._logger.info(f"Handling error from '{self._client.user.id}'...")
        await self.handle()
        self._logger.info(f"Error from '{self._client.user.id}' handled successfully")

    async def handle(self) -> None:
        payload = ErrorNotificationPayload(
            text=f"Something went wrong: {self._error}",
            created_at=dt.datetime.now(dt.UTC),
        )
        frame = ErrorNotificationFrame(payload=payload)
        await self._client.send(frame)
