import asyncio
import getopt
import random


async def execute_later(func: callable, delay: int, *args, **kwargs):
    await asyncio.sleep(delay)
    if asyncio.iscoroutinefunction(func):
        await func(*args, **kwargs)
    else:
        func(*args, **kwargs)


def generate_random_name() -> str:
    usernames = ('Gandalf', 'Frodo', 'Aragorn', 'Legolas', 'Gimli', 'Boromir', 'Samwise',
                 'Meriadoc', 'Peregrin', 'Saruman', 'Gollum', 'Sauron', 'Bilbo', 'Galadriel')
    return random.choice(usernames)
    

def parse_opts(query: str) -> tuple[str, str, str]:
    options = getopt.getopt(query.split(), 'u:t:', ['username=', 'time='])[0]
    options = dict(options)
    receiver_username = options.get('-u') or options.get('--username')
    delay = options.get('-t') or options.get('--time')
    message = query.replace(f'-u {receiver_username}', '').replace(f'--username {receiver_username}', '')
    message = message.replace(f'-t {delay}', '').replace(f'--time {delay}', '')
    return receiver_username, delay, message.strip()


def print_update(update: 'Update'):
    match update.status:
        case 'ERROR':
            message = f'\033[1;31;40m[ERROR]: {update.data["message"]}'
        case 'OK':
            message = f'\033[1;32;40m{update.data["message"]}'
        case 'MSG':
            from_user = update.data['sender']
            target = update.data['target']
            text = update.data['text']
            if target == 'BROADCAST':
                message = f'\033[1;34;40m[BROADCAST] {from_user} >>> {text}'
            else:
                message = f'\033[1;35;40m[PRIVATE] {from_user} >>> {text}'
    print(message)
