from dataclasses import dataclass

from shared.schemas.types import UserId


@dataclass
class User:
    id: UserId
