from enum import StrEnum

from shared.schemas.notifications import NotificationFrame, NotificationTypes, PrivateMessageNotificationPayload, \
    BroadcastMessageNotificationPayload, ErrorNotificationPayload


class Colors(StrEnum):
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'


class Printer:
    def message(self, frame: NotificationFrame) -> None:
        match NotificationTypes(frame.type):
            case NotificationTypes.PRIVATE_MESSAGE:
                payload = PrivateMessageNotificationPayload.model_validate(frame.payload)
                text = f'{payload.sender} >>> {payload.text}'
                print(self._with_color(text, Colors.BLUE))

            case NotificationTypes.BROADCAST_MESSAGE:
                payload = BroadcastMessageNotificationPayload.model_validate(frame.payload)
                text = f'{payload.sender} >>> {payload.text}'
                print(self._with_color(text, Colors.GREEN))

            case NotificationTypes.ERROR:
                payload = ErrorNotificationPayload.model_validate(frame.payload)
                text = f'Error: {payload.text}'
                print(self._with_color(text, Colors.RED))

    def info(self, text: str) -> None:
        print(self._with_color(text, Colors.YELLOW))

    def error(self, text: str) -> None:
        print(self._with_color(text, Colors.RED))

    def success(self, text: str) -> None:
        print(self._with_color(text, Colors.GREEN))

    def _with_color(self, text: str, color: Colors = Colors.GREEN) -> str:
        return f'{color}{text}{Colors.RESET}'
