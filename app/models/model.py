"""Trained model records."""
from datetime import datetime
from .. import db


class TrainedModel(db.Model):
    """Trained ML model record."""
    
    __tablename__ = 'trained_models'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Model info
    model_type = db.Column(db.String(50), default='yolov8')  # yolov8, yolov8-3d
    model_size = db.Column(db.String(10), default='m')  # n, s, m, l, x
    version = db.Column(db.String(50), nullable=True)
    
    # Training details
    epochs = db.Column(db.Integer)
    batch_size = db.Column(db.Integer)
    augmentation_enabled = db.Column(db.Boolean, default=False)
    training_device = db.Column(db.String(50), default='auto')
    
    # Paths
    model_path = db.Column(db.String(255), nullable=False)
    weights_path = db.Column(db.String(255), nullable=True)
    config_path = db.Column(db.String(255), nullable=True)
    
    # Performance metrics
    metrics = db.Column(db.JSON, default={})  # mAP, precision, recall, F1, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trained_at = db.Column(db.DateTime, nullable=True)
    
    is_published = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'model_type': self.model_type,
            'model_size': self.model_size,
            'version': self.version,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'augmentation_enabled': self.augmentation_enabled,
            'training_device': self.training_device,
            'model_path': self.model_path,
            'weights_path': self.weights_path,
            'config_path': self.config_path,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'trained_at': self.trained_at.isoformat() if self.trained_at else None,
            'is_published': self.is_published,
        }
