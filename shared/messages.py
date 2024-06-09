import datetime as dt

from pydantic import BaseModel


class Message(BaseModel):
    sender: str
    to: str
    text: str
    ok: bool
    time: dt.datetime
