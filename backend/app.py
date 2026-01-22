"""Production WSGI entry point for Render/Gunicorn."""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, socketio

# Detect environment
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

# This is what gunicorn will call
if __name__ == '__main__':
    # For local testing
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001)),
        debug=False,
    )
