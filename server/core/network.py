import asyncio
import json
from typing import Optional, Union


class DataTransport:
    def __init__(self, writer: asyncio.StreamWriter, reader: asyncio.StreamReader) -> None:
        self._writer = writer
        self._reader = reader
        self._address, self._port = writer.get_extra_info("peername")

    @staticmethod
    def _pack(data: str) -> bytes:
        return data.encode() + b"\n"
    
    @staticmethod
    def _unpack(data: bytes) -> str:
        return data.decode().strip()
    
    async def transfer(self, data: str) -> None:
        raw_data = self._pack(data)
        self._writer.write(raw_data)
        await self._writer.drain()
        
    async def receive(self) -> str:
        raw_data = await self._reader.readline()
        if not raw_data:
            raise ConnectionError("Connection is closed")
        return self._unpack(raw_data)
        
    async def close(self) -> None:
        self._writer.close()
        await self._writer.wait_closed()
    
    def __str__(self) -> str:
        return f'{self._address}:{self._port}'


class Request:
    def __init__(self, command: str, data: dict | None = None, user: 'User' = None) -> None:
        self.command = command
        self.data = data
        self.user = user
    
    @classmethod
    def from_json(cls, data: str) -> 'Request':
        data = json.loads(data)
        return cls(**data)
    
    def to_json(self) -> str:
        return json.dumps(self.__dict__)
    
    def __repr__(self):
        return f"Request(command={self.command}, value={self.data}, user={self.user})"


class Response:
    def __init__(self, status: str, data: Union[str, dict] | None) -> None:
        self.status = status
        self.data = data

    @classmethod
    def from_json(cls, data: str) -> 'Response':
        data = json.loads(data)
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def __repr__(self):
        return f"Response(status={self.status}, data={self.data})"
