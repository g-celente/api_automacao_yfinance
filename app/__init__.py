from flask import Flask
from mvc_flask import FlaskMVC
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
import logging

db = SQLAlchemy()

def create_app(config_name='development'):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Configure CORS
    CORS(app, 
         origins=["*"],  # Em produção, especifique os domínios permitidos
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    mvc = FlaskMVC(app)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')
    
    # Import models to register them with SQLAlchemy
    from app.model.User import User
    from app.model.Cliente import Cliente
    from app.model.Carteira import Carteira
    from app.model.Asset import Asset
    
    # Register blueprints/routes
    from app import routes
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "investment-api"}, 200
    
    return app