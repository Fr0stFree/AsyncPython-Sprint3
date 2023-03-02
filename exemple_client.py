import asyncio

from settings import Settings
from client.client import Client


settings = Settings()


async def main():
    async with Client(settings.SERVER_HOST, settings.SERVER_PORT) as client:
        await client.handle_input()


if __name__ == '__main__':
    asyncio.run(main())
