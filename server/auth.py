import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from database import DatabaseOperations

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_token(user_id: int, email: str) -> str:
    """Create a JWT token for a user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')

def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401

        try:
            # Expected format: "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'error': 'Invalid authorization header format'}), 401

            token = parts[1]
            payload = decode_token(token)

            # Add user info to request context
            request.user_id = payload['user_id']
            request.user_email = payload['email']

            return f(*args, **kwargs)

        except ValueError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401

    return decorated_function

def register_user(email: str, password: str, full_name: str = None):
    """Register a new user"""
    # Check if user already exists
    existing_user = DatabaseOperations.get_user_by_email(email)
    if existing_user:
        raise ValueError('User with this email already exists')

    # Hash password and create user
    password_hash = hash_password(password)
    user = DatabaseOperations.create_user(email, password_hash, full_name)

    # Create token
    token = create_token(user['id'], user['email'])

    return {
        'user': {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name']
        },
        'token': token
    }

def login_user(email: str, password: str):
    """Log in a user"""
    # Get user
    user = DatabaseOperations.get_user_by_email(email)
    if not user:
        raise ValueError('Invalid email or password')

    # Verify password
    if not verify_password(password, user['password_hash']):
        raise ValueError('Invalid email or password')

    # Create token
    token = create_token(user['id'], user['email'])

    return {
        'user': {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name']
        },
        'token': token
    }

def get_current_user(user_id: int):
    """Get current user info"""
    return DatabaseOperations.get_user_by_id(user_id)
