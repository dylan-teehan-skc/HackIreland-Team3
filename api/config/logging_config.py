import logging
import logging.handlers
import os
from logging.config import dictConfig
from api.config import get_settings

def setup_logging():
    """Configure logging for the FastAPI application."""
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': settings.LOG_FORMAT
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join('logs', settings.LOG_FILE),
                'maxBytes': 1024 * 1024 * 100,  # 100 MB
                'backupCount': 5,
                'formatter': 'standard',
                'level': settings.LOG_LEVEL
            },
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'standard',
                'level': settings.LOG_LEVEL
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': settings.LOG_LEVEL,
                'propagate': True
            }
        }
    }

    dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.info('Logging setup completed')
