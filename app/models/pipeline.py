"""Pipeline execution models."""
from datetime import datetime
from .. import db


class PipelineRun(db.Model):
    """Pipeline execution record."""
    
    __tablename__ = 'pipeline_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Configuration
    config = db.Column(db.JSON, default={})  # stores CLI args
    
    # Results
    report_path = db.Column(db.String(255), nullable=True)
    metrics = db.Column(db.JSON, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    steps = db.relationship('PipelineStep', backref='pipeline_run', lazy=True, cascade='all, delete-orphan')
    
    @property
    def duration(self):
        """Get pipeline duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'status': self.status,
            'progress': self.progress,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'config': self.config,
            'report_path': self.report_path,
            'metrics': self.metrics,
            'duration': self.duration,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class PipelineStep(db.Model):
    """Individual pipeline step execution."""
    
    __tablename__ = 'pipeline_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    pipeline_run_id = db.Column(db.Integer, db.ForeignKey('pipeline_runs.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # download, annotate, validate, train, evaluate
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, skipped, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    output = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def duration(self):
        """Get step duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'pipeline_run_id': self.pipeline_run_id,
            'name': self.name,
            'status': self.status,
            'progress': self.progress,
            'output': self.output,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'created_at': self.created_at.isoformat(),
        }
