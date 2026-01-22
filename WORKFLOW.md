# Complete Workflow Diagram

## How the Pipeline Orchestrator Ties Everything Together

```
╔══════════════════════════════════════════════════════════════════════════╗
║                     CUNEIFORM TRANSLATOR PIPELINE                       ║
║                                                                          ║
║  Single entry point: python scripts/run_complete_pipeline.py            ║
╚══════════════════════════════════════════════════════════════════════════╝

                                    ↓

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Download Tablets (5-10 min)                                     │
├──────────────────────────────────────────────────────────────────────────┤
│ scripts/download_cdli_tablets.py                                        │
│                                                                          │
│  CDLI API                                                               │
│   ↓                                                                     │
│  50 tablet images + metadata                                           │
│   ↓                                                                     │
│  data/raw/cdli/ (128 MB)                                              │
└──────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Annotate Tablets (Manual - 15-60 min)                          │
├──────────────────────────────────────────────────────────────────────────┤
│ scripts/annotate_tablets.py                                            │
│                                                                          │
│  Interactive CLI:                                                       │
│   • Display tablet image                                              │
│   • User draws regions around signs                                   │
│   • Mark sign type/category                                           │
│   • Save annotation JSON                                              │
│                                                                          │
│  Repeat for each tablet...                                            │
│   ↓                                                                     │
│  data/processed/ (JSON annotations)                                   │
│                                                                          │
│  Format: TabletRecord {                                                │
│    "p_number": "P100100",                                             │
│    "regions": [{                                                       │
│      "shape": "polygon",                                              │
│      "coordinates": [[x,y], ...],                                    │
│      "sign": "A-1",                                                   │
│      "confidence": 0.95                                               │
│    }, ...]                                                             │
│  }                                                                      │
└──────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Data Quality Validation (1-2 min)                              │
├──────────────────────────────────────────────────────────────────────────┤
│ scripts/validate_tablets.py                                            │
│                                                                          │
│  Check:                                                                 │
│   ✓ No overlapping regions                                           │
│   ✓ Coordinates within image bounds                                  │
│   ✓ Sign categories valid                                            │
│   ✓ Inter-annotator agreement (if multiple)                          │
│                                                                          │
│  Output: PASS / WARNING / FAIL                                        │
│   ↓                                                                     │
│  Quality score: 0-100                                                 │
└──────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Convert to YOLO Format (30 seconds)                            │
├──────────────────────────────────────────────────────────────────────────┤
│ vision/data_converter.py (internal)                                    │
│                                                                          │
│  Transform annotations:                                                │
│   Polygon regions → Bounding boxes                                    │
│   Absolute coords → Normalized YOLO format                           │
│                                                                          │
│  Output:                                                                │
│   data/yolo_dataset/                                                 │
│   ├── images/train/ (70% of data)                                    │
│   ├── images/val/   (15% of data)                                    │
│   ├── images/test/  (15% of data)                                    │
│   ├── labels/train/                                                  │
│   ├── labels/val/                                                    │
│   ├── labels/test/                                                   │
│   └── data.yaml (dataset configuration)                              │
└──────────────────────────────────────────────────────────────────────────┘

                                    ↓

                        ┌─────────────────────┐
                        │ Optional: 3D Data   │
                        ├─────────────────────┤
                        │ GigaMesh PLY files  │
                        │ (3D models of      │
                        │  same tablets)     │
                        └─────────────────────┘
                                ↓
                        (If --enable-augmentation)
                                ↓

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 4b: 3D Augmentation (Optional - 10-20 min)                        │
├──────────────────────────────────────────────────────────────────────────┤
│ vision/model_3d.py + vision/trainer_3d.py (internal)                  │
│                                                                          │
│  For each tablet:                                                       │
│   1. Load 3D model (PLY format)                                       │
│   2. Extract depth map (3 methods available)                          │
│   3. Overlay depth on photograph (variable opacity)                   │
│   4. Create N variations per image                                    │
│                                                                          │
│  Result: Augmented training set                                       │
│   data/yolo_dataset_augmented/                                       │
│   ├── images/train/ (70% + augmented variants)                       │
│   ├── labels/train/ (corresponding labels)                           │
│   └── data.yaml (updated config)                                     │
│                                                                          │
│  Benefits: 5-15% mAP improvement (Stötzner et al. 2023)              │
└──────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Train YOLOv8 Model (30-120 min depending on config)            │
├──────────────────────────────────────────────────────────────────────────┤
│ scripts/train_sign_detector_3d.py                                      │
│                                                                          │
│  Configuration:                                                         │
│   • Model: YOLOv8-{nano|small|medium|large|xlarge}                   │
│   • Epochs: 50 (default, configurable)                               │
│   • Batch size: 16 (configurable)                                    │
│   • Device: CPU / CUDA / MPS (Apple Silicon)                         │
│   • Augmentation: Yes/No (configurable)                              │
│                                                                          │
│  Optional baseline training (for comparison):                         │
│   → Trains standard YOLOv8 without 3D augmentation                  │
│   → Saves as baseline_best.pt                                        │
│                                                                          │
│  Training outputs:                                                     │
│   models/                                                              │
│   ├── best.pt (best model on validation set)                         │
│   ├── baseline_best.pt (if --train-baseline)                         │
│   ├── training_summary.json (metrics)                                │
│   └── training_config.json (parameters used)                         │
└──────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Evaluation & Report (1-2 min)                                  │
├──────────────────────────────────────────────────────────────────────────┤
│ run_complete_pipeline.py (internal)                                    │
│                                                                          │
│  Generates:                                                             │
│   • pipeline_report.json                                              │
│   • Execution timeline (timing for each step)                         │
│   • Results summary (status, metrics)                                 │
│   • Next steps recommendations                                        │
│                                                                          │
│  Output file: pipeline_report.json                                    │
│  {                                                                      │
│    "timestamp": "2026-01-21T21:46:22...",                            │
│    "total_execution_time_seconds": 3847,                             │
│    "step_times": {...},                                               │
│    "results": {                                                        │
│      "download": {...},                                               │
│      "annotation": {...},                                             │
│      "quality_check": {...},                                          │
│      "training": {...},                                               │
│      "evaluation": {...}                                              │
│    }                                                                    │
│  }                                                                      │
└──────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 7: Use Trained Model for Inference                                │
├──────────────────────────────────────────────────────────────────────────┤
│ scripts/infer_signs.py                                                │
│                                                                          │
│  Usage:                                                                 │
│   python scripts/infer_signs.py \                                     │
│     --model models/best.pt \                                          │
│     --image new_tablet.jpg \                                          │
│     --output predictions.json                                         │
│                                                                          │
│  Outputs:                                                               │
│   predictions.json {                                                   │
│     "image": "new_tablet.jpg",                                        │
│     "detections": [{                                                   │
│       "class": "A-1",                                                 │
│       "confidence": 0.94,                                             │
│       "bbox": [x1, y1, x2, y2]                                       │
│     }, ...]                                                            │
│   }                                                                    │
│                                                                          │
│  Alternative outputs:                                                  │
│   • CSV format (--format csv)                                         │
│   • Visualized image (--save-viz)                                     │
└──────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════╗
║                         COMPLETE!                                       ║
║  Model is ready for production use or further research/improvement.    ║
╚══════════════════════════════════════════════════════════════════════════╝
```

## Command Examples by Use Case

### Research & Development
```bash
# Quick test to verify everything works
python scripts/run_complete_pipeline.py \
  --num-tablets 10 \
  --epochs 5 \
  --enable-augmentation

# Compare models
python scripts/run_complete_pipeline.py \
  --skip-download --skip-annotation \
  --epochs 50 \
  --enable-augmentation \
  --train-baseline
```

### Production Training
```bash
# Train on full dataset with 3D augmentation
python scripts/run_complete_pipeline.py \
  --mode full \
  --enable-augmentation \
  --num-tablets 500 \
  --model l \
  --epochs 100 \
  --batch-size 32 \
  --device cuda
```

### Existing Data
```bash
# Resume from annotated tablets
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation \
  --enable-augmentation
```

### Interactive Session
```bash
# Step through pipeline with prompts
python scripts/run_complete_pipeline.py --mode interactive
```

## Data Flow Summary

| Stage | Input | Process | Output |
|-------|-------|---------|--------|
| 1. Download | CDLI API | Fetch metadata + images | `data/raw/cdli/` |
| 2. Annotate | Images + User input | Draw regions, label signs | `data/processed/*.json` |
| 3. Validate | Annotations | Check quality & integrity | Quality report, issues |
| 4. Convert | Annotations | To YOLO format | `data/yolo_dataset/` |
| 4b. Augment | YOLO data + PLY models | Overlay depth maps | `data/yolo_dataset_augmented/` |
| 5. Train | YOLO dataset | YOLOv8 training loop | `models/best.pt` |
| 6. Evaluate | Training metrics | Summarize results | `pipeline_report.json` |
| 7. Infer | Model + new image | Sign detection | `predictions.json` |

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│         User Interface Layer                    │
├─────────────────────────────────────────────────┤
│  ① Command-line orchestrator (current)         │
│  ② Terminal dashboard (planned)                │
│  ③ Web UI (future - Step 5/M3)                 │
├─────────────────────────────────────────────────┤
│         Pipeline Orchestration Layer            │
├─────────────────────────────────────────────────┤
│  run_complete_pipeline.py coordinates all      │
│  steps with progress tracking                  │
├─────────────────────────────────────────────────┤
│         Component Layer                        │
├─────────────────────────────────────────────────┤
│  ✓ CDLI downloader                            │
│  ✓ Annotation tool                            │
│  ✓ Quality validator                          │
│  ✓ 3D model processor                         │
│  ✓ YOLO trainer                               │
│  ✓ Inference engine                           │
├─────────────────────────────────────────────────┤
│         Data Layer                             │
├─────────────────────────────────────────────────┤
│  Raw data → Annotations → YOLO format →       │
│  Augmented data → Trained model → Predictions │
└─────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Orchestrator, not UI** - Keeps system modular and testable
2. **Skip flags** - Users can resume from any step
3. **JSON reports** - Easy to parse for dashboards/monitoring
4. **Optional 3D aug** - Works without 3D models, benefits when available
5. **No web server** - Works over SSH, in containers, batch jobs
6. **CLI first** - Web UI can layer on top later

This architecture allows:
- ✅ Immediate research use
- ✅ Easy testing and development
- ✅ Smooth transition to web UI later
- ✅ Integration with existing tools
- ✅ Production-ready workflows
