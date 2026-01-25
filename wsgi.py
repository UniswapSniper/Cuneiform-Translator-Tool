"""Main entry point for Render/Gunicorn at the project root."""
import eventlet
eventlet.monkey_patch()

import os
import sys

# Ensure the root directory is in the path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the application factory from the 'app' package
from app import create_app, socketio

# Initialize the production app
app = create_app('production')

# For local testing
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port)
