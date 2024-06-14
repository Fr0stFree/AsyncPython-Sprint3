from pydantic import BaseModel

from server.src.models.client import ClientManager, Client, LoggerLike


class BaseHandler:
    clients: ClientManager = ClientManager.get_current()
    payload_validator: BaseModel | None = None

    def __init__(self, payload: dict, client: Client, logger: LoggerLike) -> None:
        self.payload = self._get_payload(payload)
        self.client = client
        self.logger = logger

    async def __call__(self, *args, **kwargs) -> None:
        self.logger.info(f"Handling request '{self.__class__.__name__}' from '{self.client.user.id}'...")
        await self.handle()
        self.logger.info(f"Request '{self.__class__.__name__}' from '{self.client.user.id}' handled successfully")

    def _get_payload(self, payload: dict) -> BaseModel | None:
        try:
            if self.payload_validator is not None:
                return self.payload_validator.model_validate(payload)
            return None
        except AttributeError as error:
            raise NotImplementedError(f"Payload validator is not defined for '{self.__class__.__name__}'") from error

    async def handle(self) -> None:
        raise NotImplementedError
