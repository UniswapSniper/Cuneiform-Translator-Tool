"""Analytics and statistics API endpoints."""
from flask import jsonify
from sqlalchemy import func
from app import db
from app.models import PipelineRun, TrainedModel, Tablet, Annotation
from app.api import analytics_bp


@analytics_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    """Get overall analytics summary."""
    total_runs = db.session.query(func.count(PipelineRun.id)).scalar()
    total_models = db.session.query(func.count(TrainedModel.id)).scalar()
    total_tablets = db.session.query(func.count(Tablet.id)).scalar()
    total_annotations = db.session.query(func.count(Annotation.id)).scalar()
    
    avg_mAP = db.session.query(func.avg(func.cast(
        db.func.json_extract(TrainedModel.metrics, '$.mAP'),
        db.Float
    ))).scalar() or 0.0
    
    return jsonify({
        'total_pipeline_runs': total_runs,
        'total_models': total_models,
        'total_tablets': total_tablets,
        'total_annotations': total_annotations,
        'average_mAP': round(avg_mAP, 4),
    }), 200


@analytics_bp.route('/pipeline/stats', methods=['GET'])
def get_pipeline_stats():
    """Get pipeline execution statistics."""
    total_runs = PipelineRun.query.count()
    completed_runs = PipelineRun.query.filter_by(status='completed').count()
    failed_runs = PipelineRun.query.filter_by(status='failed').count()
    
    avg_duration = db.session.query(
        func.avg(PipelineRun.duration)
    ).filter(PipelineRun.status == 'completed').scalar() or 0
    
    return jsonify({
        'total_runs': total_runs,
        'completed': completed_runs,
        'failed': failed_runs,
        'success_rate': (completed_runs / total_runs * 100) if total_runs > 0 else 0,
        'average_duration_seconds': avg_duration,
    }), 200


@analytics_bp.route('/models/stats', methods=['GET'])
def get_models_stats():
    """Get model training statistics."""
    total_models = TrainedModel.query.count()
    published_models = TrainedModel.query.filter_by(is_published=True).count()
    
    size_distribution = db.session.query(
        TrainedModel.model_size,
        func.count(TrainedModel.id).label('count')
    ).group_by(TrainedModel.model_size).all()
    
    type_distribution = db.session.query(
        TrainedModel.model_type,
        func.count(TrainedModel.id).label('count')
    ).group_by(TrainedModel.model_type).all()
    
    return jsonify({
        'total_models': total_models,
        'published': published_models,
        'size_distribution': {size: count for size, count in size_distribution},
        'type_distribution': {mtype: count for mtype, count in type_distribution},
    }), 200


@analytics_bp.route('/tablets/stats', methods=['GET'])
def get_tablets_stats():
    """Get tablet statistics."""
    total_tablets = Tablet.query.count()
    
    quality_distribution = db.session.query(
        Tablet.quality_status,
        func.count(Tablet.id).label('count')
    ).group_by(Tablet.quality_status).all()
    
    avg_quality_score = db.session.query(
        func.avg(Tablet.quality_score)
    ).scalar() or 0.0
    
    return jsonify({
        'total_tablets': total_tablets,
        'average_quality_score': round(avg_quality_score, 2),
        'quality_distribution': {status: count for status, count in quality_distribution},
    }), 200
