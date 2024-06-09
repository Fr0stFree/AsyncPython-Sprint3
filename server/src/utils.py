from typing import Generator


def usernames_generator() -> Generator[str, None, None]:
    usernames = {
        'Gandalf', 'Frodo', 'Aragorn', 'Legolas', 'Gimli', 'Boromir', 'Samwise',
        'Meriadoc', 'Peregrin', 'Saruman', 'Gollum', 'Sauron', 'Bilbo', 'Galadriel'
    }
    while usernames:
        yield usernames.pop()

