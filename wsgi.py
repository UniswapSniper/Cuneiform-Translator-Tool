"""Main entry point for Render/Gunicorn at the project root."""
import os
import sys

# Add the backend directory to Python's search path
# This allows 'import app' to work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Now we can import the app factory
from app import create_app, socketio

# Initialize the production app
app = create_app('production')

# This is what Gunicorn looks for (wsgi:app)
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
