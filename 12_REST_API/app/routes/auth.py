"""
Authentication routes
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity,
    jwt_required, get_jwt
)
from marshmallow import ValidationError
from flasgger import swag_from

from app.models import db
from app.models.user import User, TokenBlocklist
from app.schemas.user import UserSchema, LoginSchema, TokenSchema

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()
login_schema = LoginSchema()
token_schema = TokenSchema()

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Register a new user',
    'description': 'Creates a new user account',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'johndoe'},
                    'email': {'type': 'string', 'example': 'john@example.com'},
                    'password': {'type': 'string', 'example': 'password123'}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'User registered successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'user': {'type': 'object'}
                }
            }
        },
        '400': {
            'description': 'Validation error'
        }
    }
})
def register():
    """Register a new user"""
    try:
        # Parse and validate request data
        user_data = request.get_json()
        user = user_schema.load(user_data)
        
        # Save user to database
        db.session.add(user)
        db.session.commit()
        
        # Return response
        return jsonify({
            'message': 'User registered successfully',
            'user': user_schema.dump(user)
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 400

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Login user',
    'description': 'Authenticates a user and returns access and refresh tokens',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'johndoe'},
                    'password': {'type': 'string', 'example': 'password123'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {'type': 'string'},
                    'refresh_token': {'type': 'string'},
                    'token_type': {'type': 'string'}
                }
            }
        },
        '401': {
            'description': 'Invalid credentials'
        }
    }
})
def login():
    """Login user and return access token"""
    try:
        # Parse and validate request data
        login_data = login_schema.load(request.get_json())
        
        # Find user by username
        user = User.query.filter_by(username=login_data['username']).first()
        
        # Check if user exists and password is correct
        if not user or not user.verify_password(login_data['password']):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid username or password'
            }), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Account is inactive'
            }), 401
        
        # Create access and refresh tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Return tokens
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 400

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Refresh access token',
    'description': 'Generates a new access token using a refresh token',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Refresh token with Bearer prefix'
        }
    ],
    'responses': {
        '200': {
            'description': 'Token refreshed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {'type': 'string'},
                    'token_type': {'type': 'string'}
                }
            }
        },
        '401': {
            'description': 'Invalid or expired refresh token'
        }
    }
})
def refresh():
    """Refresh access token"""
    # Get current user identity
    current_user_id = get_jwt_identity()
    
    # Create new access token
    access_token = create_access_token(identity=current_user_id)
    
    # Return new access token
    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer'
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Logout user',
    'description': 'Revokes the current access token',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access token with Bearer prefix'
        }
    ],
    'responses': {
        '200': {
            'description': 'Logout successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        }
    }
})
def logout():
    """Logout user by revoking token"""
    # Get JWT token data
    token = get_jwt()
    jti = token['jti']
    user_id = get_jwt_identity()
    
    # Add token to blocklist
    token_blocklist = TokenBlocklist(
        jti=jti,
        type='access',
        user_id=user_id
    )
    db.session.add(token_blocklist)
    db.session.commit()
    
    # Return response
    return jsonify({
        'message': 'Successfully logged out'
    }), 200 