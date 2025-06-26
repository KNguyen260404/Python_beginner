"""
User routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from flasgger import swag_from

from app.models import db
from app.models.user import User
from app.schemas.user import UserSchema, UserUpdateSchema
from app.utils.auth import admin_required
from app.utils.pagination import get_pagination_params, get_paginated_response

users_bp = Blueprint('users', __name__)
user_schema = UserSchema()
user_update_schema = UserUpdateSchema()

@users_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Users'],
    'summary': 'Get all users',
    'description': 'Returns a list of all users (admin only)',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access token with Bearer prefix'
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': 'Page number'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'default': 10,
            'description': 'Items per page'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of users',
            'schema': {
                'type': 'object',
                'properties': {
                    'pagination': {'type': 'object'},
                    'items': {
                        'type': 'array',
                        'items': {'type': 'object'}
                    }
                }
            }
        },
        '403': {
            'description': 'Admin privileges required'
        }
    }
})
def get_users():
    """Get all users (admin only)"""
    # Get pagination parameters
    page, per_page = get_pagination_params()
    
    # Query users
    query = User.query.order_by(User.created_at.desc())
    
    # Return paginated response
    return jsonify(get_paginated_response(user_schema, query, page, per_page)), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Get user by ID',
    'description': 'Returns a specific user by ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access token with Bearer prefix'
        },
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'User details',
            'schema': {
                'type': 'object'
            }
        },
        '403': {
            'description': 'Access denied'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def get_user(user_id):
    """Get user by ID"""
    # Get current user ID
    current_user_id = get_jwt_identity()
    
    # Get user from database
    user = User.query.get_or_404(user_id)
    
    # Check if current user is admin or the requested user
    if current_user_id != user_id and not User.query.get(current_user_id).is_admin():
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    # Return user
    return jsonify(user_schema.dump(user)), 200

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Update user',
    'description': 'Updates a specific user by ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access token with Bearer prefix'
        },
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'User updated successfully',
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
        },
        '403': {
            'description': 'Access denied'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def update_user(user_id):
    """Update user by ID"""
    try:
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Get user from database
        user = User.query.get_or_404(user_id)
        
        # Check if current user is admin or the requested user
        if current_user_id != user_id and not User.query.get(current_user_id).is_admin():
            return jsonify({
                'error': 'Forbidden',
                'message': 'Access denied'
            }), 403
        
        # Parse and validate request data
        user_data = request.get_json()
        
        # Update user
        user_update_schema.instance = user
        updated_user = user_update_schema.load(user_data, instance=user, partial=True)
        
        # Save to database
        db.session.commit()
        
        # Return response
        return jsonify({
            'message': 'User updated successfully',
            'user': user_schema.dump(updated_user)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 400

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Delete user',
    'description': 'Deletes a specific user by ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access token with Bearer prefix'
        },
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'User deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        '403': {
            'description': 'Access denied'
        },
        '404': {
            'description': 'User not found'
        }
    }
})
def delete_user(user_id):
    """Delete user by ID"""
    # Get current user ID
    current_user_id = get_jwt_identity()
    
    # Get user from database
    user = User.query.get_or_404(user_id)
    
    # Check if current user is admin
    if not User.query.get(current_user_id).is_admin():
        return jsonify({
            'error': 'Forbidden',
            'message': 'Admin privileges required'
        }), 403
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    # Return response
    return jsonify({
        'message': 'User deleted successfully'
    }), 200 