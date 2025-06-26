"""
Configuration settings for the Flask application
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API settings
    API_TITLE = os.getenv('API_TITLE', 'Product API')
    API_VERSION = os.getenv('API_VERSION', '1.0')
    API_DESCRIPTION = os.getenv('API_DESCRIPTION', 'A simple REST API for managing products')
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=10)

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Ensure these are set in production
    @classmethod
    def init_app(cls, app):
        assert os.getenv('SECRET_KEY'), "SECRET_KEY environment variable must be set"
        assert os.getenv('JWT_SECRET_KEY'), "JWT_SECRET_KEY environment variable must be set"
        assert os.getenv('DATABASE_URL'), "DATABASE_URL environment variable must be set"

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 