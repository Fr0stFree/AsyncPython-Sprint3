from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Actions(StrEnum):
    SEND_MESSAGE = 'send'
    HELP = 'help'
    LOGOUT = 'logout'
    UNKNOWN = 'unknown'


class MessageTypes(StrEnum):
    PRIVATE = 'private'
    BROADCAST = 'broadcast'


class RequestData(BaseModel):
    action: Actions


class SendMessageRequestData(RequestData):
    action: Actions = Actions.SEND_MESSAGE
    type: MessageTypes
    text: str = Field(..., min_length=1, max_length=100)
    to: int | Literal[MessageTypes.BROADCAST]
