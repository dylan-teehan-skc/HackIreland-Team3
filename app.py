from flask import Flask
from config import config
from lib_logging import setup_logging
import os

def create_app(config_name=None):
    """Application factory function."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    
    @app.route('/')
    def index():
        app.logger.info('Index page accessed')
        return 'Hello, World!'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
