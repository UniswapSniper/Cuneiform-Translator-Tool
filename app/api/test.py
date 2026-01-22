"""Test endpoints for WebSocket functionality."""
from flask import Blueprint, request, jsonify
from ..services import WebSocketService

test_bp = Blueprint('test', __name__, url_prefix='/api/test')


@test_bp.route('/websocket/ping', methods=['POST'])
def websocket_ping():
    """Send a test WebSocket event.
    
    Request body:
    {
        "run_id": 1,
        "event_type": "progress",  # progress, step, metrics, log, error
        "data": {...}
    }
    """
    try:
        data = request.get_json()
        run_id = data.get('run_id')
        event_type = data.get('event_type', 'progress')
        payload = data.get('data', {})
        
        if not run_id:
            return jsonify({'error': 'run_id required'}), 400
        
        if event_type == 'progress':
            WebSocketService.emit_pipeline_progress(
                run_id,
                payload.get('progress', 50),
                payload.get('status', 'running'),
                payload.get('message', 'Test update')
            )
        elif event_type == 'step':
            WebSocketService.emit_step_progress(
                run_id,
                payload.get('step_name', 'test_step'),
                payload.get('progress', 50),
                payload.get('status', 'running'),
                payload.get('details', {})
            )
        elif event_type == 'metrics':
            WebSocketService.emit_metrics_update(
                run_id,
                payload.get('step_name', 'training'),
                payload.get('metrics', {'loss': 0.5})
            )
        elif event_type == 'batch':
            WebSocketService.emit_batch_metrics(
                run_id,
                payload.get('batch_num', 1),
                payload.get('epoch', 1),
                payload.get('metrics', {'loss': 0.5})
            )
        elif event_type == 'log':
            WebSocketService.emit_log_message(
                run_id,
                payload.get('level', 'info'),
                payload.get('message', 'Test log'),
                payload.get('context', {})
            )
        elif event_type == 'error':
            WebSocketService.emit_error(
                run_id,
                payload.get('error_message', 'Test error'),
                payload.get('error_type', 'error'),
                payload.get('traceback', '')
            )
        else:
            return jsonify({'error': f'Unknown event_type: {event_type}'}), 400
        
        return jsonify({
            'status': 'ok',
            'message': f'Emitted {event_type} event to pipeline {run_id}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_bp.route('/websocket/stream', methods=['POST'])
def websocket_stream():
    """Simulate a stream of WebSocket events for testing.
    
    Request body:
    {
        "run_id": 1,
        "num_events": 5,
        "event_type": "progress"
    }
    """
    try:
        data = request.get_json()
        run_id = data.get('run_id')
        num_events = data.get('num_events', 5)
        event_type = data.get('event_type', 'progress')
        
        if not run_id:
            return jsonify({'error': 'run_id required'}), 400
        
        events_sent = []
        for i in range(num_events):
            progress = int((i + 1) / num_events * 100)
            
            if event_type == 'progress':
                WebSocketService.emit_pipeline_progress(
                    run_id,
                    progress,
                    'running' if progress < 100 else 'completed',
                    f'Event {i+1}/{num_events}'
                )
            elif event_type == 'batch':
                WebSocketService.emit_batch_metrics(
                    run_id,
                    i + 1,
                    1,
                    {'loss': 1.0 - (progress / 100), 'accuracy': progress / 100}
                )
            
            events_sent.append({
                'event': event_type,
                'progress': progress,
                'event_num': i + 1
            })
        
        return jsonify({
            'status': 'ok',
            'message': f'Sent {num_events} {event_type} events',
            'events': events_sent
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
