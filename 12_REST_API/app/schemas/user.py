"""
User schema for serialization and validation
"""

from marshmallow import fields, validate, validates, ValidationError
from app.schemas import ma
from app.models.user import User

class UserSchema(ma.SQLAlchemySchema):
    """Schema for User model"""
    
    class Meta:
        model = User
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(
        required=True,
        validate=validate.Length(min=3, max=80)
    )
    email = ma.auto_field(
        required=True,
        validate=validate.Email()
    )
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )
    role = ma.auto_field(dump_only=True)
    is_active = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    @validates('username')
    def validate_username(self, username):
        """Validate username is unique"""
        if User.query.filter_by(username=username).first():
            raise ValidationError('Username already exists')
    
    @validates('email')
    def validate_email(self, email):
        """Validate email is unique"""
        if User.query.filter_by(email=email).first():
            raise ValidationError('Email already exists')

class UserUpdateSchema(ma.SQLAlchemySchema):
    """Schema for updating User model"""
    
    class Meta:
        model = User
        load_instance = True
    
    username = ma.auto_field(validate=validate.Length(min=3, max=80))
    email = ma.auto_field(validate=validate.Email())
    password = fields.String(load_only=True, validate=validate.Length(min=8))
    is_active = ma.auto_field()
    
    @validates('username')
    def validate_username(self, username):
        """Validate username is unique"""
        user = User.query.filter_by(username=username).first()
        if user and user.id != self.instance.id:
            raise ValidationError('Username already exists')
    
    @validates('email')
    def validate_email(self, email):
        """Validate email is unique"""
        user = User.query.filter_by(email=email).first()
        if user and user.id != self.instance.id:
            raise ValidationError('Email already exists')

class LoginSchema(ma.Schema):
    """Schema for login credentials"""
    
    username = fields.String(required=True)
    password = fields.String(required=True)

class TokenSchema(ma.Schema):
    """Schema for JWT tokens"""
    
    access_token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)
    token_type = fields.String(dump_only=True, default="bearer") 