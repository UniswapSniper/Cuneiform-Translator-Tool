"""WebSocket event broadcasting service."""
from datetime import datetime
from .. import socketio
from ..models import PipelineRun, PipelineStep


class WebSocketService:
    """Service for emitting WebSocket events to connected clients."""
    
    @staticmethod
    def emit_pipeline_progress(run_id: int, progress: int, status: str, message: str = ""):
        """Emit pipeline progress update.
        
        Args:
            run_id: Pipeline run ID
            progress: Progress percentage (0-100)
            status: Pipeline status (running, completed, failed, cancelled)
            message: Optional status message
        """
        data = {
            'run_id': run_id,
            'progress': max(0, min(100, progress)),
            'status': status,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
        }
        socketio.emit(
            'pipeline:progress',
            data,
            room=f'pipeline:{run_id}',
            namespace='/'
        )
        return data
    
    @staticmethod
    def emit_step_progress(run_id: int, step_name: str, progress: int, status: str, details: dict = None):
        """Emit step progress update.
        
        Args:
            run_id: Pipeline run ID
            step_name: Step name (e.g., 'data_loading', 'preprocessing', 'training')
            progress: Step progress percentage (0-100)
            status: Step status (pending, running, completed, failed)
            details: Optional additional details (e.g., metrics, errors)
        """
        data = {
            'run_id': run_id,
            'step_name': step_name,
            'progress': max(0, min(100, progress)),
            'status': status,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat(),
        }
        socketio.emit(
            'step:progress',
            data,
            room=f'pipeline:{run_id}',
            namespace='/'
        )
        return data
    
    @staticmethod
    def emit_metrics_update(run_id: int, step_name: str, metrics: dict):
        """Emit training metrics update.
        
        Args:
            run_id: Pipeline run ID
            step_name: Step name
            metrics: Dictionary of metrics (e.g., {'loss': 0.5, 'accuracy': 0.95})
        """
        data = {
            'run_id': run_id,
            'step_name': step_name,
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat(),
        }
        socketio.emit(
            'metrics:update',
            data,
            room=f'pipeline:{run_id}',
            namespace='/'
        )
        return data
    
    @staticmethod
    def emit_batch_metrics(run_id: int, batch_num: int, epoch: int, metrics: dict):
        """Emit per-batch metrics for training.
        
        Args:
            run_id: Pipeline run ID
            batch_num: Batch number
            epoch: Epoch number
            metrics: Batch metrics (loss, accuracy, etc.)
        """
        data = {
            'run_id': run_id,
            'batch_num': batch_num,
            'epoch': epoch,
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat(),
        }
        socketio.emit(
            'batch:metrics',
            data,
            room=f'pipeline:{run_id}',
            namespace='/'
        )
        return data
    
    @staticmethod
    def emit_log_message(run_id: int, level: str, message: str, context: dict = None):
        """Emit log message.
        
        Args:
            run_id: Pipeline run ID
            level: Log level (debug, info, warning, error)
            message: Log message
            context: Optional context data
        """
        data = {
            'run_id': run_id,
            'level': level,
            'message': message,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
        }
        socketio.emit(
            'log:message',
            data,
            room=f'pipeline:{run_id}',
            namespace='/'
        )
        return data
    
    @staticmethod
    def emit_error(run_id: int, error_message: str, error_type: str = "error", traceback_str: str = ""):
        """Emit error event.
        
        Args:
            run_id: Pipeline run ID
            error_message: Error message
            error_type: Type of error
            traceback_str: Optional traceback string
        """
        data = {
            'run_id': run_id,
            'error_message': error_message,
            'error_type': error_type,
            'traceback': traceback_str,
            'timestamp': datetime.utcnow().isoformat(),
        }
        socketio.emit(
            'pipeline:error',
            data,
            room=f'pipeline:{run_id}',
            namespace='/'
        )
        return data
    
    @staticmethod
    def emit_pipeline_started(run_id: int, config: dict):
        """Emit pipeline start event.
        
        Args:
            run_id: Pipeline run ID
            config: Pipeline configuration
        """
        data = {
            'run_id': run_id,
            'config': config,
            'timestamp': datetime.utcnow().isoformat(),
        }
        socketio.emit(
            'pipeline:started',
            data,
            room=f'pipeline:{run_id}',
            namespace='/'
        )
        return data
    
    @staticmethod
    def emit_pipeline_completed(run_id: int, results: dict):
        """Emit pipeline completion event.
        
        Args:
            run_id: Pipeline run ID
            results: Pipeline results
        """
        data = {
            'run_id': run_id,
            'results': results,
            'timestamp': datetime.utcnow().isoformat(),
        }
        socketio.emit(
            'pipeline:completed',
            data,
            room=f'pipeline:{run_id}',
            namespace='/'
        )
        return data
