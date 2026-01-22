"""Production WSGI entry point for Render/Gunicorn."""
import os
import sys

# Add the current directory to path so the 'app' package can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, socketio

# Detect environment
env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

# This is what gunicorn will refer to: 'wsgi:app'
if __name__ == '__main__':
    # For local testing
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001)),
        debug=False,
    )
