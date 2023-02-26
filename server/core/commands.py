class CommandHandler:
    """Класс-декоратор для регистрации обработчиков команд сервера."""
    HANDLERS = {}

    @classmethod
    def register(cls, command: str):
        def decorator(func):
            cls.HANDLERS[command] = func
            return func
        
        return decorator
    
    @classmethod
    def get_handler(cls, command: str):
        return cls.HANDLERS.get(command, cls.HANDLERS['unknown'])
