import logging.config
import os
from datetime import datetime

def setup_logging(app):
    """
    Configura o logging estruturado para a aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'INFO',
                'formatter': 'json',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, f'app-{datetime.now().strftime("%Y-%m-%d")}.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True
            },
            'app': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False
            },
            'werkzeug': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }

    logging.config.dictConfig(logging_config)
    app.logger.info('Logging configured successfully')
