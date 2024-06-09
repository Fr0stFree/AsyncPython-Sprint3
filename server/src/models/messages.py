import datetime as dt

from pydantic import Field

from shared.messages import Message


class ServerMessage(Message):
    sender: str = 'SERVER'
    ok: bool = True
    time: dt.datetime = Field(default_factory=dt.datetime.now)
