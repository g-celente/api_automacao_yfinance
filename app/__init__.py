from flask import Flask
from mvc_flask import FlaskMVC
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    CORS(app, supports_credentials=True)

    mvc = FlaskMVC(app) 
    db.init_app(app)
    migrate = Migrate(app, db)

    from app.model.User import User
    from app.model.Cliente import Cliente
    from app.model.Carteira import Carteira
    from app.model.Asset import Asset
    # Import models to register them with SQLAlchemy

    return app