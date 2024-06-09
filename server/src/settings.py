from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings


class ServerSettings(BaseSettings):
    host: Final[str] = Field(..., alias='SERVER_HOST')
    port: Final[int] = Field(..., alias='SERVER_PORT')
    logging: Final[dict] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '[{levelname}] >>> {message} ',
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
