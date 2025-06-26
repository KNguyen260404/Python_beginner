"""
Authentication utilities
"""

import functools
from flask import jsonify, request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User, TokenBlocklist

def admin_required(fn):
    """
    Decorator to require admin role
    
    Args:
        fn: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # Verify JWT token
        verify_jwt_in_request()
        
        # Get current user
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is admin
        if not user or not user.is_admin():
            return jsonify({
                'error': 'Forbidden',
                'message': 'Admin privileges required'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper

def check_token_in_blocklist(jwt_header, jwt_payload):
    """
    Callback function to check if a token is in the blocklist
    
    Args:
        jwt_header: JWT header
        jwt_payload: JWT payload
        
    Returns:
        True if token is in blocklist, False otherwise
    """
    jti = jwt_payload['jti']
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None

def get_current_user():
    """
    Get the current user from the JWT token
    
    Returns:
        User object or None
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None

def is_token_revoked(jwt_payload):
    """
    Check if a token is revoked
    
    Args:
        jwt_payload: JWT payload
        
    Returns:
        True if token is revoked, False otherwise
    """
    jti = jwt_payload['jti']
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None 