"""Flask development server entry point."""
import os
import sys

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, socketio

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    # Run development server
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001)),
        debug=True,
        use_reloader=True,
        use_debugger=True,
    )
