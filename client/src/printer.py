from enum import StrEnum

from shared.messages import Message


class Colors(StrEnum):
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'


class Printer:
    def __init__(self) -> None:
        pass

    def message(self, message: Message) -> None:
        color = Colors.BLUE if message.ok else Colors.RED
        print(self._with_color(f'{message.sender}: {message.text}', color))

    def info(self, text: str) -> None:
        print(self._with_color(text, Colors.YELLOW))

    def error(self, text: str) -> None:
        print(self._with_color(text, Colors.RED))

    def success(self, text: str) -> None:
        print(self._with_color(text, Colors.GREEN))

    def _with_color(self, text: str, color: Colors = Colors.GREEN) -> str:
        return f'{color}{text}{Colors.RESET}'
