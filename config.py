import os

class Config:
    """Base configuration."""
    
    # Basic Flask config
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-in-production')
    
    # SQLAlchemy config
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL_DEV', 
        'postgresql://neondb_owner:npg_W4sL0kISKoQt@ep-twilight-dust-a5q9fhog-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Redis config (para cache e blacklist de tokens)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT config
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Configurações específicas de produção
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}