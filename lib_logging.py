import logging
import logging.handlers
import os
from logging.config import dictConfig

def setup_logging(app):
    """Configure logging for the application."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': app.config['LOG_FORMAT']
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join('logs', app.config['LOG_FILE']),
                'maxBytes': 1024 * 1024 * 100,  # 100 MB
                'backupCount': 5,
                'formatter': 'standard',
                'level': app.config['LOG_LEVEL']
            },
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'standard',
                'level': app.config['LOG_LEVEL']
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': app.config['LOG_LEVEL'],
                'propagate': True
            }
        }
    }

    dictConfig(logging_config)
    app.logger.info('Logging setup completed')
