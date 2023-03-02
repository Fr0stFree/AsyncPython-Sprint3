import asyncio

from settings import Settings
from server.server import Server


settings = Settings()


async def main():
    server = Server(settings.SERVER_HOST, settings.SERVER_PORT)
    await server.start()
    await server.serve()
    await server.stop()


if __name__ == '__main__':
    asyncio.run(main())
