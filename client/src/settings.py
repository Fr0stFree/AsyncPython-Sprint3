from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings


class ClientSettings(BaseSettings):
    host: Final[str] = Field(..., alias='SERVER_HOST')
    port: Final[int] = Field(..., alias='SERVER_PORT')
