def validate_username(username: str) -> tuple[bool, str]:
    """Функция проверяет никнейм пользователя на корректность."""
    if len(username) > 15:
        return False, 'Имя пользователя не должно превышать 25 символов'
    if len(username) < 3:
        return False, 'Имя пользователя должно быть не короче 3 символов'
    if ' ' in username:
        return False, 'Имя пользователя не должно содержать пробелы'
    return True, 'OK'


def validate_message_delay(delay: str) -> tuple[bool, str]:
    """Функция проверяет задержку отправки сообщения на корректность."""
    if not delay.isdigit():
        return False, 'Задержка должна быть целым числом'
    if int(delay) < 0:
        return False, 'Задержка не может быть отрицательной'
    return True, 'OK'
