"""Tablet and annotation models."""
from datetime import datetime
from .. import db


class Tablet(db.Model):
    """Cuneiform tablet record."""
    
    __tablename__ = 'tablets'
    
    id = db.Column(db.Integer, primary_key=True)
    pnumber = db.Column(db.String(50), unique=True, index=True)  # CDLI P-number
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Image data
    image_path = db.Column(db.String(255), nullable=True)
    thumbnail_path = db.Column(db.String(255), nullable=True)
    
    # 3D model data
    model_3d_path = db.Column(db.String(255), nullable=True)
    depth_map_path = db.Column(db.String(255), nullable=True)
    
    # Metadata
    period = db.Column(db.String(100), nullable=True)
    provenances = db.Column(db.String(255), nullable=True)
    material = db.Column(db.String(100), nullable=True)
    
    # Quality
    quality_score = db.Column(db.Float, default=0.0)
    quality_status = db.Column(db.String(20), default='unreviewed')  # unreviewed, pass, warning, fail
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    annotations = db.relationship('Annotation', backref='tablet', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'pnumber': self.pnumber,
            'name': self.name,
            'description': self.description,
            'image_path': self.image_path,
            'thumbnail_path': self.thumbnail_path,
            'model_3d_path': self.model_3d_path,
            'depth_map_path': self.depth_map_path,
            'period': self.period,
            'provenances': self.provenances,
            'material': self.material,
            'quality_score': self.quality_score,
            'quality_status': self.quality_status,
            'annotation_count': len(self.annotations),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Annotation(db.Model):
    """Sign region annotation for tablet."""
    
    __tablename__ = 'annotations'
    
    id = db.Column(db.Integer, primary_key=True)
    tablet_id = db.Column(db.Integer, db.ForeignKey('tablets.id'), nullable=False)
    
    # Region data
    sign_name = db.Column(db.String(100), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    
    # Metadata
    confidence = db.Column(db.Float, default=1.0)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'tablet_id': self.tablet_id,
            'sign_name': self.sign_name,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'confidence': self.confidence,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
