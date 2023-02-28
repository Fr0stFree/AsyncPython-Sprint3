import asyncio
import getopt


async def execute_later(func: callable, delay: int, *args, **kwargs):
    await asyncio.sleep(delay)
    if asyncio.iscoroutinefunction(func):
        await func(*args, **kwargs)
    else:
        func(*args, **kwargs)


def generate_random_username() -> str:
    return 'SuperUser'


def parse_opts(query: str) -> tuple[str, str, str]:
    options = getopt.getopt(query.split(), 'u:t:', ['username=', 'time='])[0]
    options = dict(options)
    receiver_username = options.get('-u') or options.get('--username')
    delay = options.get('-t') or options.get('--time')
    message = query.replace(f'-u {receiver_username}', '').replace(f'--username {receiver_username}', '')
    message = message.replace(f'-t {delay}', '').replace(f'--time {delay}', '')
    return receiver_username, delay, message.strip()
