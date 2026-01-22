"""Flask development server entry point."""
import os
from app import create_app, socketio

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    # Run development server
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True,
        use_debugger=True,
    )
