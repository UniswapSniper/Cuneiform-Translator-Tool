"""Tablet analysis API endpoints for real-time decoding experience."""
import time
import threading
from flask import request, jsonify
from .. import db, socketio
from ..models import Tablet, Annotation
from . import tablets_bp


@tablets_bp.route('/<int:tablet_id>/analyze', methods=['POST'])
def analyze_tablet(tablet_id):
    """Start real-time analysis on a tablet."""
    tablet = Tablet.query.get(tablet_id)
    if not tablet:
        return jsonify({'error': 'Tablet not found'}), 404
    
    # Start analysis in background thread
    thread = threading.Thread(
        target=_run_analysis,
        args=(tablet_id,),
        daemon=True
    )
    thread.start()
    
    return jsonify({
        'status': 'started',
        'tablet_id': tablet_id,
        'message': 'Analysis started'
    }), 202


def _run_analysis(tablet_id):
    """Run the analysis process with WebSocket updates."""
    import random
    
    with socketio.server.app.app_context():
        tablet = Tablet.query.get(tablet_id)
        if not tablet:
            return
        
        room = f'tablet:{tablet_id}'
        
        # Phase 1: Scanning (3 seconds)
        socketio.emit('analysis:phase', {
            'tablet_id': tablet_id,
            'phase': 'scanning',
            'message': 'Initializing neural scan...'
        }, room=room, namespace='/')
        
        for progress in range(0, 101, 5):
            socketio.emit('analysis:scanning', {
                'tablet_id': tablet_id,
                'progress': progress,
                'scan_line_position': progress  # 0-100 percent of image height
            }, room=room, namespace='/')
            time.sleep(0.15)
        
        # Phase 2: Detection (detect signs one by one)
        socketio.emit('analysis:phase', {
            'tablet_id': tablet_id,
            'phase': 'detection',
            'message': 'Detecting cuneiform signs...'
        }, room=room, namespace='/')
        
        # Generate realistic detection boxes
        signs = _generate_detected_signs(tablet)
        total_signs = len(signs)
        
        for idx, sign in enumerate(signs):
            socketio.emit('analysis:detection', {
                'tablet_id': tablet_id,
                'sign': sign,
                'sign_index': idx,
                'total_signs': total_signs,
                'progress': int((idx + 1) / total_signs * 100)
            }, room=room, namespace='/')
            time.sleep(0.3)  # Staggered reveal
        
        # Phase 3: Translation (reveal translation)
        socketio.emit('analysis:phase', {
            'tablet_id': tablet_id,
            'phase': 'translation',
            'message': 'Decoding ancient text...'
        }, room=room, namespace='/')
        
        translation = _generate_translation(signs)
        words = translation.split(' ')
        
        for idx, word in enumerate(words):
            socketio.emit('analysis:translation', {
                'tablet_id': tablet_id,
                'word': word,
                'word_index': idx,
                'total_words': len(words),
                'progress': int((idx + 1) / len(words) * 100)
            }, room=room, namespace='/')
            time.sleep(0.2)
        
        # Phase 4: Complete
        socketio.emit('analysis:phase', {
            'tablet_id': tablet_id,
            'phase': 'complete',
            'message': 'Analysis complete'
        }, room=room, namespace='/')
        
        socketio.emit('analysis:complete', {
            'tablet_id': tablet_id,
            'signs_detected': total_signs,
            'translation': translation,
            'confidence': random.uniform(0.85, 0.95)
        }, room=room, namespace='/')


def _generate_detected_signs(tablet):
    """Generate realistic-looking detected signs."""
    import random
    
    # Real Sumerian/Akkadian sign names
    sign_names = [
        'AN', 'KI', 'LU', 'GI', 'DU', 'SAG', 'GAL', 'KUR',
        'UD', 'ITI', 'MU', 'E', 'A', 'NI', 'TA', 'DA',
        'LUGAL', 'DINGIR', 'EN', 'NAM', 'URU', 'NIBRU'
    ]
    
    num_signs = random.randint(8, 18)
    signs = []
    
    # Generate non-overlapping bounding boxes
    grid_cols = 4
    grid_rows = (num_signs // grid_cols) + 1
    
    for i in range(num_signs):
        row = i // grid_cols
        col = i % grid_cols
        
        # Add some randomness to position
        x = (col / grid_cols) * 0.8 + 0.05 + random.uniform(-0.02, 0.02)
        y = (row / grid_rows) * 0.7 + 0.1 + random.uniform(-0.02, 0.02)
        
        signs.append({
            'id': i,
            'name': random.choice(sign_names),
            'x': x,  # Percentage of image width
            'y': y,  # Percentage of image height
            'width': random.uniform(0.08, 0.15),
            'height': random.uniform(0.06, 0.12),
            'confidence': random.uniform(0.75, 0.98),
            'unicode': _get_cuneiform_unicode(random.choice(sign_names))
        })
    
    return signs


def _generate_translation(signs):
    """Generate a realistic-looking translation."""
    # Sample translations (mix of real Sumerian texts)
    translations = [
        "In the reign of Ur-Nammu, king of Ur, this tablet records the delivery of barley",
        "To the temple of Inanna, offerings of silver and grain were brought by the merchants",
        "The king of Sumer and Akkad, mighty ruler, commissioned this inscription",
        "Three shekels of silver for the purchase of sheep, recorded in the year of the flood",
        "By the command of Enlil, the temple granary received ten gur of barley",
        "This administrative record documents the workers assigned to the irrigation canal",
        "Royal inscription commemorating the restoration of the ancient temple walls",
    ]
    import random
    return random.choice(translations)


def _get_cuneiform_unicode(sign_name):
    """Get Unicode cuneiform character for sign name."""
    # Real cuneiform Unicode mappings (subset)
    unicode_map = {
        'AN': '𒀭', 'KI': '𒆠', 'LU': '𒇻', 'GI': '𒄀', 'DU': '𒁺',
        'SAG': '𒊕', 'GAL': '𒃲', 'KUR': '𒆳', 'UD': '𒌓', 'ITI': '𒌗',
        'MU': '𒈬', 'E': '𒂊', 'A': '𒀀', 'NI': '𒉌', 'TA': '𒋫',
        'DA': '𒁕', 'LUGAL': '𒈗', 'DINGIR': '𒀭', 'EN': '𒂗', 'NAM': '𒉆',
        'URU': '𒌷', 'NIBRU': '𒉌𒁍𒊒'
    }
    return unicode_map.get(sign_name, '𒀀')
