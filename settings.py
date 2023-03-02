import os
from typing import Final

from pydantic import BaseSettings, Field


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    SERVER_HOST: Final[str] = Field(..., env='SERVER_HOST')
    SERVER_PORT: Final[int] = Field(..., env='SERVER_PORT')
    REPORTS_TO_BAN: Final[int] = 2
    BAN_TIME: Final[int] = 60 * 10  # seconds
    MESSAGE_TTL: Final[int] = 60 * 60  # seconds
    LOGGING: Final[dict] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '{levelname} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

    class Config:
        env_file = os.path.join(BASE_DIR, '.env')
        env_file_encoding = 'utf-8'
