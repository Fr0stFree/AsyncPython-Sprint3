from enum import StrEnum
from typing import Literal, Union

from pydantic import BaseModel, Field

from shared.schemas.types import UserId


class ActionTypes(StrEnum):
    SEND_MESSAGE = 'send-message'
    BROADCAST_MESSAGE = 'broadcast-message'
    HELP = 'help'
    LOGOUT = 'logout'


class ActionFrame(BaseModel):
    type: ActionTypes
    payload: dict | None = None


class SendMessagePayload(BaseModel):
    text: str
    to: UserId


class SendMessageActionFrame(ActionFrame):
    type: Literal[ActionTypes.SEND_MESSAGE] = ActionTypes.SEND_MESSAGE
    payload: SendMessagePayload


class BroadcastMessagePayload(BaseModel):
    text: str


class BroadcastMessageActionFrame(ActionFrame):
    type: Literal[ActionTypes.BROADCAST_MESSAGE] = ActionTypes.BROADCAST_MESSAGE
    payload: BroadcastMessagePayload
