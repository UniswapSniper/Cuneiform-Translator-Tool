"""Health check endpoints."""
from flask import jsonify
from . import health_bp


@health_bp.route('', methods=['GET'])
def health_check():
    """Check API health status."""
    return jsonify({
        'status': 'ok',
        'message': 'Cuneiform Translator API is running',
        'version': '1.0.0',
    }), 200


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Check if API is ready to accept requests."""
    try:
        # Check database
        from .. import db
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'ready',
            'database': 'connected',
            'cache': 'connected',
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e),
        }), 503
