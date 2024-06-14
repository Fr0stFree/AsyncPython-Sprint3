import datetime as dt

from server.src.models.client import ClientManager, Client, LoggerLike
from shared.schemas.notifications import ErrorNotificationPayload, ErrorNotificationFrame


class BaseErrorHandler:
    clients: ClientManager = ClientManager.get_current()

    def __init__(self, payload: dict, client: Client, error: Exception, logger: LoggerLike) -> None:
        self.payload = payload
        self.client = client
        self.logger = logger
        self.error = error

    async def __call__(self, *args, **kwargs) -> None:
        self.logger.info(f"Handling error from '{self.client.user.id}'...")
        await self.handle()
        self.logger.info(f"Error from '{self.client.user.id}' handled successfully")

    async def handle(self) -> None:
        payload = ErrorNotificationPayload(
            text=f"Something went wrong: {self.error}",
            created_at=dt.datetime.now(dt.UTC),
        )
        frame = ErrorNotificationFrame(payload=payload)
        await self.client.send(frame)
