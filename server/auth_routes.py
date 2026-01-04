from flask import Blueprint, request, jsonify
import logging
from auth import register_user, login_user, get_current_user, require_auth
from database import init_database

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        result = register_user(email, password, full_name)
        return jsonify(result), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in register: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Log in a user"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        result = login_user(email, password)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    """Get current user info"""
    try:
        user = get_current_user(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user}), 200

    except Exception as e:
        logger.error(f"Error in get_me: {e}")
        return jsonify({'error': 'Failed to get user info'}), 500

@auth_bp.route('/init-db', methods=['POST'])
def initialize_database():
    """Initialize the database schema (for development)"""
    try:
        init_database()
        return jsonify({'message': 'Database initialized successfully'}), 200
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return jsonify({'error': str(e)}), 500
