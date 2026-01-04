from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Import blueprints
from tasks import tasks_bp
from projects import projects_bp
from health import health_bp
from auth_routes import auth_bp
from database import init_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS
CORS(app, origins=['http://localhost:3000', 'https://*.vercel.app'], supports_credentials=True)

# Initialize database
def initialize_db_with_retry(max_retries=5, delay=2):
    """Initialize database with retry logic for container startup"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to initialize database (attempt {attempt + 1}/{max_retries})...")
            init_database()
            logger.info("✅ Database initialized successfully")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database initialization failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {e}")
                logger.error("Server will start but database operations may fail")

# Try to initialize database on startup
initialize_db_with_retry()

# Register blueprints
app.register_blueprint(health_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(projects_bp)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
