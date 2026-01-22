"""Model management API endpoints."""
from flask import request, jsonify
from app import db
from app.models import TrainedModel
from app.api import models_bp


@models_bp.route('', methods=['GET'])
def list_models():
    """List all trained models."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    model_type = request.args.get('model_type', None)
    published_only = request.args.get('published_only', False, type=bool)
    
    query = TrainedModel.query
    
    if model_type:
        query = query.filter_by(model_type=model_type)
    
    if published_only:
        query = query.filter_by(is_published=True)
    
    paginated = query.order_by(TrainedModel.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'items': [model.to_dict() for model in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
    }), 200


@models_bp.route('/<int:model_id>', methods=['GET'])
def get_model(model_id):
    """Get model details."""
    model = TrainedModel.query.get(model_id)
    if not model:
        return jsonify({'error': 'Model not found'}), 404
    
    return jsonify(model.to_dict()), 200


@models_bp.route('/<int:model_id>', methods=['PUT'])
def update_model(model_id):
    """Update model information."""
    model = TrainedModel.query.get(model_id)
    if not model:
        return jsonify({'error': 'Model not found'}), 404
    
    data = request.get_json() or {}
    
    if 'name' in data:
        model.name = data['name']
    if 'description' in data:
        model.description = data['description']
    if 'is_published' in data:
        model.is_published = data['is_published']
    
    db.session.commit()
    return jsonify(model.to_dict()), 200


@models_bp.route('/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete a model."""
    model = TrainedModel.query.get(model_id)
    if not model:
        return jsonify({'error': 'Model not found'}), 404
    
    db.session.delete(model)
    db.session.commit()
    
    return jsonify({'status': 'deleted'}), 204


@models_bp.route('/compare', methods=['POST'])
def compare_models():
    """Compare multiple models."""
    data = request.get_json() or {}
    model_ids = data.get('model_ids', [])
    
    if not model_ids or len(model_ids) < 2:
        return jsonify({'error': 'At least 2 model IDs required'}), 400
    
    models = TrainedModel.query.filter(TrainedModel.id.in_(model_ids)).all()
    
    if len(models) != len(model_ids):
        return jsonify({'error': 'Some models not found'}), 404
    
    return jsonify({
        'models': [m.to_dict() for m in models],
        'comparison': {
            'mAP': [m.metrics.get('mAP', 0) for m in models],
            'precision': [m.metrics.get('precision', 0) for m in models],
            'recall': [m.metrics.get('recall', 0) for m in models],
            'F1': [m.metrics.get('F1', 0) for m in models],
        },
    }), 200
