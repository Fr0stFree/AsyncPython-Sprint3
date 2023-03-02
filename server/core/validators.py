from utils.exceptions import ValidationError

def validate_username(username: str):
    """Функция проверяет никнейм пользователя на корректность."""
    if len(username) > 15:
        raise ValidationError('Имя пользователя должно быть не длиннее 15 символов')
    if len(username) < 3:
        raise ValidationError('Имя пользователя должно быть не короче 3 символов')
    if ' ' in username:
        raise ValidationError('Имя пользователя не должно содержать пробелы')


def validate_message_delay(delay: str):
    """Функция проверяет задержку отправки сообщения на корректность."""
    if not delay.isdigit():
        raise ValidationError('Задержка должна быть целым числом')
    if int(delay) < 0:
        raise ValidationError('Задержка должна быть положительным числом')
