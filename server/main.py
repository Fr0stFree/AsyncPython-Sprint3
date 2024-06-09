import asyncio

from server.src.settings import ServerSettings
from server.src.server import Server


async def main():
    settings = ServerSettings()
    server = Server(settings)
    try:
        await server.start()
        await server.serve()
    finally:
        await server.stop()


if __name__ == '__main__':
    asyncio.run(main())
