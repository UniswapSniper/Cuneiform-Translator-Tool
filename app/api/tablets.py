"""Tablet gallery API endpoints."""
from flask import request, jsonify
from .. import db
from ..models import Tablet, Annotation
from . import tablets_bp


@tablets_bp.route('', methods=['GET'])
def list_tablets():
    """List all tablets with pagination and filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    quality_status = request.args.get('quality_status', None)
    
    query = Tablet.query
    
    if search:
        query = query.filter(
            Tablet.pnumber.ilike(f'%{search}%') |
            Tablet.name.ilike(f'%{search}%')
        )
    
    if quality_status:
        query = query.filter_by(quality_status=quality_status)
    
    paginated = query.order_by(Tablet.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'items': [tablet.to_dict() for tablet in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
    }), 200


@tablets_bp.route('/<int:tablet_id>', methods=['GET'])
def get_tablet(tablet_id):
    """Get tablet details."""
    tablet = Tablet.query.get(tablet_id)
    if not tablet:
        return jsonify({'error': 'Tablet not found'}), 404
    
    return jsonify({
        'tablet': tablet.to_dict(),
        'annotations': [ann.to_dict() for ann in tablet.annotations],
    }), 200


@tablets_bp.route('/<int:tablet_id>/annotations', methods=['POST'])
def add_annotation(tablet_id):
    """Add annotation to tablet."""
    tablet = Tablet.query.get(tablet_id)
    if not tablet:
        return jsonify({'error': 'Tablet not found'}), 404
    
    data = request.get_json() or {}
    
    annotation = Annotation(
        tablet_id=tablet_id,
        sign_name=data.get('sign_name', ''),
        x=data.get('x', 0),
        y=data.get('y', 0),
        width=data.get('width', 0),
        height=data.get('height', 0),
        confidence=data.get('confidence', 1.0),
        notes=data.get('notes', ''),
    )
    db.session.add(annotation)
    db.session.commit()
    
    return jsonify(annotation.to_dict()), 201


@tablets_bp.route('/annotations/<int:annotation_id>', methods=['PUT'])
def update_annotation(annotation_id):
    """Update annotation."""
    annotation = Annotation.query.get(annotation_id)
    if not annotation:
        return jsonify({'error': 'Annotation not found'}), 404
    
    data = request.get_json() or {}
    
    if 'sign_name' in data:
        annotation.sign_name = data['sign_name']
    if 'confidence' in data:
        annotation.confidence = data['confidence']
    if 'notes' in data:
        annotation.notes = data['notes']
    
    db.session.commit()
    return jsonify(annotation.to_dict()), 200


@tablets_bp.route('/annotations/<int:annotation_id>', methods=['DELETE'])
def delete_annotation(annotation_id):
    """Delete annotation."""
    annotation = Annotation.query.get(annotation_id)
    if not annotation:
        return jsonify({'error': 'Annotation not found'}), 404
    
    db.session.delete(annotation)
    db.session.commit()
    
    return jsonify({'status': 'deleted'}), 204


@tablets_bp.route('/upload', methods=['POST'])
def upload_tablet():
    """Upload a tablet image for processing."""
    import os
    import uuid
    from werkzeug.utils import secure_filename
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'tiff', 'tif'}
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # Save file
    file.save(filepath)
    
    # Get metadata from form
    name = request.form.get('name', original_filename)
    description = request.form.get('description', '')
    period = request.form.get('period', 'Unknown')
    
    # Generate P-number for user uploads (custom prefix)
    existing_count = Tablet.query.filter(Tablet.pnumber.like('U%')).count()
    pnumber = f"U{existing_count + 1:06d}"
    
    # Create tablet record
    tablet = Tablet(
        pnumber=pnumber,
        name=name,
        description=description,
        image_path=f"/static/uploads/{unique_filename}",
        thumbnail_path=f"/static/uploads/{unique_filename}",  # Same for now, could generate thumbnail
        period=period,
        quality_score=0.0,
        quality_status='unreviewed',
    )
    
    db.session.add(tablet)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Tablet uploaded successfully',
        'tablet': tablet.to_dict(),
    }), 201

