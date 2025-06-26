"""
Tests for authentication routes
"""

import json
import pytest
from flask import url_for

from app import create_app
from app.models import db
from app.models.user import User, TokenBlocklist

@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    app = create_app('testing')
    
    # Create all tables
    with app.app_context():
        db.create_all()
        
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.password = 'password123'
        db.session.add(user)
        
        # Create an admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.password = 'adminpass'
        db.session.add(admin)
        
        db.session.commit()
        
    yield app
    
    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

def test_register(client):
    """Test user registration"""
    # Register a new user
    response = client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword'
        }),
        content_type='application/json'
    )
    
    # Check response
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert 'user' in data
    assert data['user']['username'] == 'newuser'
    assert data['user']['email'] == 'new@example.com'
    assert 'password' not in data['user']

def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    # Register a user with existing username
    response = client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    # Check response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'details' in data
    assert 'username' in data['details']

def test_login_success(client):
    """Test successful login"""
    # Login with valid credentials
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['token_type'] == 'bearer'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    # Login with invalid password
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        }),
        content_type='application/json'
    )
    
    # Check response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Unauthorized'

def test_refresh_token(client):
    """Test refreshing access token"""
    # First login to get tokens
    login_response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    tokens = json.loads(login_response.data)
    refresh_token = tokens['refresh_token']
    
    # Use refresh token to get new access token
    response = client.post(
        '/api/auth/refresh',
        headers={
            'Authorization': f'Bearer {refresh_token}'
        }
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'

def test_logout(client):
    """Test logout"""
    # First login to get tokens
    login_response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    tokens = json.loads(login_response.data)
    access_token = tokens['access_token']
    
    # Logout
    response = client.post(
        '/api/auth/logout',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Successfully logged out'
    
    # Try to use the token again
    response = client.post(
        '/api/auth/logout',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    
    # Token should be invalid
    assert response.status_code == 401 