import asyncio
from typing import Union, Final

from server.core.network import Response
from utils.classes import Model
from .user import User



class Message:
    text: str
    sender: User
    destination: User | list[User]
    is_broadcast: bool
    
    @property
    def destination(self) -> Union[User, list[User]]:
        return self.destination

    def to_dict(self) -> dict:
        return {'text': self.text,
                'sender': self.sender.username,
                'is_broadcast': self.is_broadcast}


