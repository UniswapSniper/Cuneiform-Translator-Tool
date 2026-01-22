"""WebSocket handlers for real-time communication."""
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import PipelineRun, PipelineStep
from datetime import datetime


def register_handlers(socketio_instance):
    """Register all WebSocket event handlers."""
    
    @socketio_instance.on('connect')
    def handle_connect():
        """Handle client connection."""
        emit('connected', {'data': 'Connected to Cuneiform Translator'})
    
    @socketio_instance.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        pass
    
    @socketio_instance.on('subscribe:pipeline')
    def handle_subscribe_pipeline(data):
        """Subscribe to pipeline updates."""
        run_id = data.get('run_id')
        room = f'pipeline:{run_id}'
        join_room(room)
        emit('subscribed', {'run_id': run_id, 'room': room})
    
    @socketio_instance.on('unsubscribe:pipeline')
    def handle_unsubscribe_pipeline(data):
        """Unsubscribe from pipeline updates."""
        run_id = data.get('run_id')
        room = f'pipeline:{run_id}'
        leave_room(room)
        emit('unsubscribed', {'run_id': run_id})
    
    @socketio_instance.on('pipeline:update')
    def handle_pipeline_update(data):
        """Handle pipeline progress update."""
        run_id = data.get('run_id')
        progress = data.get('progress', 0)
        status = data.get('status', 'running')
        
        run = PipelineRun.query.get(run_id)
        if run:
            run.progress = progress
            run.status = status
            run.updated_at = datetime.utcnow()
            db.session.commit()
            
            emit('pipeline:progress', data, room=f'pipeline:{run_id}')
    
    @socketio_instance.on('step:update')
    def handle_step_update(data):
        """Handle pipeline step update."""
        run_id = data.get('run_id')
        step_name = data.get('step_name')
        progress = data.get('progress', 0)
        status = data.get('status', 'running')
        
        step = PipelineStep.query.filter_by(
            pipeline_run_id=run_id,
            name=step_name
        ).first()
        
        if step:
            step.progress = progress
            step.status = status
            step.updated_at = datetime.utcnow()
            db.session.commit()
        
        emit('step:progress', data, room=f'pipeline:{run_id}')
    
    @socketio_instance.on('metrics:update')
    def handle_metrics_update(data):
        """Handle training metrics update."""
        run_id = data.get('run_id')
        metrics = data.get('metrics', {})
        
        emit('metrics', {
            'run_id': run_id,
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat(),
        }, room=f'pipeline:{run_id}')


def emit_pipeline_event(run_id, event_name, data):
    """Emit event to all clients subscribed to a pipeline."""
    socketio.emit(event_name, data, room=f'pipeline:{run_id}')
