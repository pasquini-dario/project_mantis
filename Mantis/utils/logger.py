import logging
import logging.config
import coloredlogs

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s\t%(name)s\t%(module)s\t%(levelname)s\t%(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': './app.log',
            'formatter': 'default',
        },
    },
    'root': { 
        'handlers': ['console', 'file'],
        'level': logging.INFO,
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("Mantis")
coloredlogs.install(level='DEBUG', logger=logger)