"""
Marshmallow schemas initialization
"""

from flask_marshmallow import Marshmallow

# Initialize Marshmallow
ma = Marshmallow()

# Import schemas to make them available
from app.schemas.user import UserSchema
from app.schemas.product import ProductSchema 