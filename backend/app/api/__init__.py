"""API blueprints."""
from flask import Blueprint

# Create blueprints
health_bp = Blueprint('health', __name__, url_prefix='/api/health')
pipeline_bp = Blueprint('pipeline', __name__, url_prefix='/api/pipeline')
models_bp = Blueprint('models', __name__, url_prefix='/api/models')
tablets_bp = Blueprint('tablets', __name__, url_prefix='/api/tablets')
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Register routes
from .health import *
from .pipeline import *
from .models import *
from .tablets import *
from .analytics import *

__all__ = ['health_bp', 'pipeline_bp', 'models_bp', 'tablets_bp', 'analytics_bp']
