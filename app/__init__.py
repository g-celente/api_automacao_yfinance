from flask import Flask
from mvc_flask import FlaskMVC
from config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])

    mvc = FlaskMVC(app)

    return app