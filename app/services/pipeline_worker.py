"""Pipeline worker for processing cuneiform tablets."""
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
from .. import db, socketio
from ..models import PipelineRun, PipelineStep, Tablet, Annotation
from .websocket_service import WebSocketService


class PipelineWorker:
    """Background worker for processing pipeline runs."""
    
    def __init__(self, run_id: int):
        self.run_id = run_id
        self.run = PipelineRun.query.get(run_id)
        if not self.run:
            raise ValueError(f"Pipeline run {run_id} not found")
        
        self.config = self.run.config or {}
        self.ws = WebSocketService()
        self.upload_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 
            'tablets'
        )
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def run_pipeline(self):
        """Execute the full pipeline."""
        try:
            # Re-merge the run into the current session to ensure it's attached correctly
            # throughout the background process.
            self.run = db.session.merge(self.run)
            
            self.run.status = 'running'
            self.run.started_at = datetime.utcnow()
            self.run.progress = 0
            db.session.commit()
            
            # Emit events to all clients in the pipeline room
            self.ws.emit_pipeline_started(self.run_id, self.config)
            self.ws.emit_pipeline_progress(self.run_id, 0, 'running', 'Pipeline started')
            self.ws.emit_log_message(self.run_id, 'info', 'Pipeline process initialized')
            
            # Step 1: Download tablets from CDLI
            if not self.config.get('skip_download', False):
                self._download_tablets()
            
            # Step 2: Run sign detection
            if not self.config.get('skip_annotation', False):
                self._run_detection()
            
            # Step 3: Generate translations (placeholder)
            self._generate_translations()
            
            # Complete
            self.run.status = 'completed'
            self.run.completed_at = datetime.utcnow()
            self.run.progress = 100
            db.session.commit()
            
            self.ws.emit_pipeline_progress(self.run_id, 100, 'completed', 'Pipeline completed successfully')
            self.ws.emit_pipeline_completed(self.run_id, {'tablets_processed': self._count_tablets()})
            
        except Exception as e:
            self.run.status = 'failed'
            self.run.error_message = str(e)
            db.session.commit()
            
            self.ws.emit_error(self.run_id, str(e), 'pipeline_error')
            self.ws.emit_log_message(self.run_id, 'error', f'Pipeline failed: {str(e)}')
    
    def _download_tablets(self):
        """Download tablet images from CDLI."""
        self.ws.emit_step_progress(self.run_id, 'download', 0, 'running')
        self.ws.emit_log_message(self.run_id, 'info', 'Starting tablet download from CDLI')
        
        # Get sample P-numbers (in production, this would query CDLI API)
        sample_pnumbers = self._get_sample_pnumbers()
        total = len(sample_pnumbers)
        
        for idx, pnumber in enumerate(sample_pnumbers):
            try:
                # Check if already exists
                existing = Tablet.query.filter_by(pnumber=pnumber).first()
                if existing:
                    self.ws.emit_log_message(self.run_id, 'info', f'Tablet {pnumber} already exists, skipping')
                    continue
                
                # Download image from CDLI
                image_url = f"https://cdli.mpiwg-berlin.mpg.de/dl/photo/{pnumber}.jpg"
                self.ws.emit_log_message(self.run_id, 'info', f'Downloading {pnumber}...')
                
                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    # Save image
                    filename = f"{pnumber}.jpg"
                    filepath = os.path.join(self.upload_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Create tablet record
                    tablet = Tablet(
                        pnumber=pnumber,
                        name=f"Tablet {pnumber}",
                        image_path=f"/static/tablets/{filename}",
                        thumbnail_path=f"/static/tablets/{filename}",
                        period="Unknown",
                        quality_score=0.0,
                        quality_status='unreviewed'
                    )
                    db.session.add(tablet)
                    db.session.commit()
                    
                    self.ws.emit_log_message(self.run_id, 'info', f'✓ Downloaded {pnumber}')
                else:
                    self.ws.emit_log_message(self.run_id, 'warning', f'Failed to download {pnumber}: HTTP {response.status_code}')
                
                # Update progress
                progress = int((idx + 1) / total * 100)
                self.ws.emit_step_progress(self.run_id, 'download', progress, 'running')
                self.ws.emit_pipeline_progress(self.run_id, int(progress * 0.4), 'running', f'Downloaded {idx + 1}/{total} tablets')
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                self.ws.emit_log_message(self.run_id, 'error', f'Error downloading {pnumber}: {str(e)}')
        
        self.ws.emit_step_progress(self.run_id, 'download', 100, 'completed')
        self.ws.emit_log_message(self.run_id, 'info', 'Download phase completed')
    
    def _run_detection(self):
        """Run sign detection on downloaded tablets."""
        self.ws.emit_step_progress(self.run_id, 'detection', 0, 'running')
        self.ws.emit_log_message(self.run_id, 'info', 'Starting sign detection')
        
        # Get tablets without annotations
        tablets = Tablet.query.filter(
            ~Tablet.annotations.any()
        ).limit(20).all()
        
        total = len(tablets)
        if total == 0:
            self.ws.emit_log_message(self.run_id, 'info', 'No tablets to process')
            self.ws.emit_step_progress(self.run_id, 'detection', 100, 'completed')
            return
        
        for idx, tablet in enumerate(tablets):
            try:
                self.ws.emit_log_message(self.run_id, 'info', f'Processing {tablet.pnumber}...')
                
                # Simulate detection (in production, this would run YOLO)
                # For now, create dummy annotations
                self._create_dummy_annotations(tablet)
                
                # Update progress
                progress = int((idx + 1) / total * 100)
                self.ws.emit_step_progress(self.run_id, 'detection', progress, 'running')
                self.ws.emit_pipeline_progress(
                    self.run_id, 
                    40 + int(progress * 0.4), 
                    'running', 
                    f'Detected signs in {idx + 1}/{total} tablets'
                )
                
                # Emit metrics
                self.ws.emit_metrics_update(self.run_id, 'detection', {
                    'tablets_processed': idx + 1,
                    'total_tablets': total,
                    'avg_confidence': 0.85
                })
                
                time.sleep(0.2)  # Simulate processing time
                
            except Exception as e:
                self.ws.emit_log_message(self.run_id, 'error', f'Error processing {tablet.pnumber}: {str(e)}')
        
        self.ws.emit_step_progress(self.run_id, 'detection', 100, 'completed')
        self.ws.emit_log_message(self.run_id, 'info', 'Detection phase completed')
    
    def _generate_translations(self):
        """Generate translations from detected signs."""
        self.ws.emit_step_progress(self.run_id, 'translation', 0, 'running')
        self.ws.emit_log_message(self.run_id, 'info', 'Generating translations')
        
        # Simulate translation generation
        for i in range(10):
            progress = int((i + 1) / 10 * 100)
            self.ws.emit_step_progress(self.run_id, 'translation', progress, 'running')
            self.ws.emit_pipeline_progress(
                self.run_id, 
                80 + int(progress * 0.2), 
                'running', 
                'Generating translations'
            )
            time.sleep(0.3)
        
        self.ws.emit_step_progress(self.run_id, 'translation', 100, 'completed')
        self.ws.emit_log_message(self.run_id, 'info', 'Translation phase completed')
    
    def _get_sample_pnumbers(self) -> List[str]:
        """Get P-numbers based on configured selection method."""
        method = self.config.get('selection_method', 'range')
        count = self.config.get('tablet_count', 50)
        
        if method == 'range':
            return self._get_range_pnumbers(count)
        elif method == 'search':
            return self._get_search_pnumbers(count)
        elif method == 'random':
            return self._get_random_pnumbers(count)
        else:
            # Default to range
            return self._get_range_pnumbers(count)
    
    def _get_range_pnumbers(self, count: int) -> List[str]:
        """Get P-numbers from a sequential range."""
        start = self.config.get('range_start', 254200)
        self.ws.emit_log_message(
            self.run_id, 
            'info', 
            f'Using range method: P{start} to P{start + count - 1}'
        )
        return [f'P{start + i}' for i in range(count)]
    
    def _get_search_pnumbers(self, count: int) -> List[str]:
        """Query CDLI search API for tablets by criteria."""
        period = self.config.get('period', 'Ur III')
        self.ws.emit_log_message(
            self.run_id, 
            'info', 
            f'Searching CDLI for {count} tablets from period: {period}'
        )
        
        try:
            # CDLI search endpoint (simplified - actual API may differ)
            # This is a placeholder - CDLI's actual search API would need proper implementation
            url = "https://cdli.mpiwg-berlin.mpg.de/search"
            params = {
                'q': f'period:{period}',
                'format': 'json',
                'limit': count
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                # Parse response (format depends on CDLI API)
                # For now, fall back to range if search fails
                self.ws.emit_log_message(
                    self.run_id, 
                    'warning', 
                    'CDLI search API not fully implemented, falling back to range'
                )
                return self._get_range_pnumbers(count)
            else:
                self.ws.emit_log_message(
                    self.run_id, 
                    'warning', 
                    f'CDLI search failed (HTTP {response.status_code}), falling back to range'
                )
                return self._get_range_pnumbers(count)
        except Exception as e:
            self.ws.emit_log_message(
                self.run_id, 
                'error', 
                f'Search error: {str(e)}, falling back to range'
            )
            return self._get_range_pnumbers(count)
    
    def _get_random_pnumbers(self, count: int) -> List[str]:
        """Get random P-numbers from CDLI's collection."""
        import random
        
        self.ws.emit_log_message(
            self.run_id, 
            'info', 
            f'Generating {count} random P-numbers from CDLI collection'
        )
        
        # CDLI P-numbers range approximately from P100000 to P500000
        # This samples from known ranges with higher density of tablets
        pnumbers = []
        ranges = [
            (100000, 150000),  # Early tablets
            (200000, 300000),  # Middle period
            (400000, 500000),  # Later tablets
        ]
        
        for _ in range(count):
            # Pick a random range
            start, end = random.choice(ranges)
            pnum = f'P{random.randint(start, end):06d}'
            pnumbers.append(pnum)
        
        return pnumbers

    
    def _create_dummy_annotations(self, tablet: Tablet):
        """Create dummy annotations for demonstration."""
        import random
        
        signs = ['KU', 'GI', 'DU', 'AN', 'KI', 'LU', 'SAG', 'GAL']
        num_signs = random.randint(3, 8)
        
        for i in range(num_signs):
            annotation = Annotation(
                tablet_id=tablet.id,
                sign_name=random.choice(signs),
                x=random.uniform(0.1, 0.8),
                y=random.uniform(0.1, 0.8),
                width=random.uniform(0.05, 0.15),
                height=random.uniform(0.05, 0.15),
                confidence=random.uniform(0.7, 0.95),
                notes='Auto-detected'
            )
            db.session.add(annotation)
        
        tablet.quality_score = random.uniform(60, 95)
        tablet.quality_status = 'pass' if tablet.quality_score > 70 else 'warning'
        db.session.commit()
    
    def _count_tablets(self) -> int:
        """Count tablets in database."""
        return Tablet.query.count()


def start_pipeline_worker(run_id: int):
    """Start a pipeline worker in a background task."""
    from flask import current_app
    app = current_app._get_current_object()
    
    def run_in_task(app_instance, r_id):
        with app_instance.app_context():
            try:
                worker = PipelineWorker(r_id)
                worker.run_pipeline()
            except Exception as e:
                print(f"Error in pipeline worker: {e}")
                import traceback
                traceback.print_exc()
    
    socketio.start_background_task(run_in_task, app, run_id)
