"""
Database models initialization
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()

# Import models to register them with SQLAlchemy
from app.models.user import User, TokenBlocklist
from app.models.product import Product 