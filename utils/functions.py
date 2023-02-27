import asyncio


async def execute_later(func: callable, delay: int, *args, **kwargs):
    await asyncio.sleep(delay)
    if asyncio.iscoroutinefunction(func):
        await func(*args, **kwargs)
    else:
        func(*args, **kwargs)


def generate_random_username() -> str:
    return 'SuperUser'