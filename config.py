import os

class Config:
    """Base configuration."""
    
    # Basic Flask config
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    # SQLAlchemy config
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL_DEV', 'postgresql://neondb_owner:npg_W4sL0kISKoQt@ep-twilight-dust-a5q9fhog-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Additional development-specific config can go here
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL_DEV')

config = {
    'development': DevelopmentConfig,
}