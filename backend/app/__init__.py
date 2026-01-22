"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
jwt = JWTManager()


def create_app(config_name='development'):
    """Create and configure Flask application.
    
    Args:
        config_name: Configuration environment ('development', 'testing', 'production')
    
    Returns:
        Configured Flask application instance
    """
    from .config import get_config
    
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from .api import pipeline_bp, models_bp, tablets_bp, analytics_bp, health_bp, test_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(tablets_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(test_bp)
    
    # Register SocketIO handlers
    from .websocket import register_handlers
    register_handlers(socketio)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
