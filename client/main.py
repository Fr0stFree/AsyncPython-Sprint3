import asyncio

from client.src.client import Client
from client.src.settings import ClientSettings


async def main():
    settings = ClientSettings()
    async with Client(settings) as client:
        await client.handle_input()


if __name__ == '__main__':
    asyncio.run(main())
