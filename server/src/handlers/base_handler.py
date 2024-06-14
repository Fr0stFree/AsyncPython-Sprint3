from pydantic import BaseModel

from server.src.models.client import ClientManager, Client, LoggerLike


class BaseHandler:
    clients: ClientManager = ClientManager.get_current()
    payload_validator: BaseModel | None

    __slots__ = ('_payload', '_client', '_logger')

    def __init__(self, payload: dict, client: Client, logger: LoggerLike) -> None:
        self._payload = self._validate_payload(payload)
        self._client = client
        self._logger = logger

    @property
    def payload(self) -> BaseModel | None:
        return self._payload

    @property
    def client(self) -> Client:
        return self._client

    @property
    def logger(self) -> LoggerLike:
        return self._logger

    async def __call__(self, *args, **kwargs) -> None:
        self._logger.info(f"Handling request '{self.__class__.__name__}' from '{self.client.user.id}'...")
        await self.handle()
        self._logger.info(f"Request '{self.__class__.__name__}' from '{self.client.user.id}' handled successfully")

    def _validate_payload(self, payload: dict) -> BaseModel | None:
        try:
            return self.payload_validator.model_validate(payload) if self.payload_validator is not None else None
        except AttributeError as error:
            raise NotImplementedError(f"Payload validator is not defined for '{self.__class__.__name__}'") from error

    async def handle(self) -> None:
        raise NotImplementedError
