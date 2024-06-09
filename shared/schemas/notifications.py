import datetime as dt
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.types import UserId


class NotificationTypes(StrEnum):
    PRIVATE_MESSAGE = 'private-message'
    BROADCAST_MESSAGE = 'broadcast-message'
    ERROR = 'error'


class NotificationFrame(BaseModel):
    type: NotificationTypes
    payload: dict | None = None


class PrivateMessageNotificationPayload(BaseModel):
    text: str
    sender: UserId
    to: UserId
    created_at: dt.datetime


class PrivateMessageNotificationFrame(NotificationFrame):
    type: Literal[NotificationTypes.PRIVATE_MESSAGE] = NotificationTypes.PRIVATE_MESSAGE
    payload: PrivateMessageNotificationPayload


class BroadcastMessageNotificationPayload(BaseModel):
    text: str
    sender: UserId
    created_at: dt.datetime


class BroadcastMessageNotificationFrame(NotificationFrame):
    type: Literal[NotificationTypes.BROADCAST_MESSAGE] = NotificationTypes.BROADCAST_MESSAGE
    payload: BroadcastMessageNotificationPayload


class ErrorNotificationPayload(BaseModel):
    text: str
    created_at: dt.datetime


class ErrorNotificationFrame(NotificationFrame):
    type: Literal[NotificationTypes.ERROR] = NotificationTypes.ERROR
    payload: ErrorNotificationPayload
