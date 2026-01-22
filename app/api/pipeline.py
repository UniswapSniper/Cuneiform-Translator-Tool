"""Pipeline control API endpoints."""
from flask import request, jsonify
from datetime import datetime
from .. import db
from ..models import PipelineRun, PipelineStep
from . import pipeline_bp


@pipeline_bp.route('/status', methods=['GET'])
def get_pipeline_status():
    """Get status of all pipeline runs."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    paginated = PipelineRun.query.order_by(PipelineRun.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'items': [run.to_dict() for run in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
    }), 200


@pipeline_bp.route('/<int:run_id>', methods=['GET'])
def get_pipeline_run(run_id):
    """Get detailed pipeline run information."""
    run = PipelineRun.query.get(run_id)
    if not run:
        return jsonify({'error': 'Pipeline run not found'}), 404
    
    return jsonify({
        'pipeline': run.to_dict(),
        'steps': [step.to_dict() for step in run.steps],
    }), 200


@pipeline_bp.route('/start', methods=['POST'])
def start_pipeline():
    """Start a new pipeline run."""
    data = request.get_json() or {}
    
    # Create pipeline run record
    run = PipelineRun(
        name=data.get('name', 'Pipeline Run'),
        config=data.get('config', {}),
        status='pending',
    )
    db.session.add(run)
    db.session.commit()
    
    # Emit event for background task to start
    from .. import socketio
    socketio.emit('pipeline:start', {
        'run_id': run.id,
        'config': run.config,
    })
    
    return jsonify({
        'id': run.id,
        'status': 'pending',
        'message': 'Pipeline starting...',
    }), 202


@pipeline_bp.route('/<int:run_id>/cancel', methods=['POST'])
def cancel_pipeline(run_id):
    """Cancel a running pipeline."""
    run = PipelineRun.query.get(run_id)
    if not run:
        return jsonify({'error': 'Pipeline run not found'}), 404
    
    if run.status in ['completed', 'failed', 'cancelled']:
        return jsonify({'error': 'Cannot cancel a completed pipeline'}), 400
    
    run.status = 'cancelled'
    run.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Emit cancellation event
    from .. import socketio
    socketio.emit('pipeline:cancel', {'run_id': run.id})
    
    return jsonify({'status': 'cancelled'}), 200


@pipeline_bp.route('/<int:run_id>/steps', methods=['GET'])
def get_pipeline_steps(run_id):
    """Get steps for a pipeline run."""
    run = PipelineRun.query.get(run_id)
    if not run:
        return jsonify({'error': 'Pipeline run not found'}), 404
    
    return jsonify({
        'steps': [step.to_dict() for step in run.steps],
    }), 200
