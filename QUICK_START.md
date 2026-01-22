# Quick Start: Testing Pipeline with Real CDLI Data

## Immediate Next Steps (Copy & Paste Ready)

### Step 1: Download Real CDLI Tablets (First Time Only)
```bash
cd /Users/jeffgoldner/Documents/CuniformTranslator

# Download 50 tablets from CDLI
python scripts/run_complete_pipeline.py \
  --num-tablets 50 \
  --skip-annotation \
  --skip-quality \
  --skip-training \
  --skip-evaluation
```
**Time**: 5-10 minutes  
**Output**: 50 tablet images in `data/raw/cdli/`

### Step 2: Quick Test (Everything at Once)
```bash
# Test full pipeline with small dataset
python scripts/run_complete_pipeline.py \
  --mode full \
  --enable-augmentation \
  --num-tablets 10 \
  --epochs 5 \
  --batch-size 8
```
**Time**: 20-30 minutes  
**Output**: `pipeline_report.json` + trained model

### Step 3: Compare 3D Augmentation Effect
```bash
# Train both models side-by-side
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation \
  --enable-augmentation \
  --train-baseline \
  --epochs 50 \
  --batch-size 16
```
**Time**: 2-3 hours  
**Output**: 
- `models/baseline_best.pt` (without 3D)
- `models/best.pt` (with 3D)
- Compare metrics to quantify improvement

### Step 4: Production Training
```bash
# Train on full dataset with 3D augmentation
python scripts/run_complete_pipeline.py \
  --mode full \
  --enable-augmentation \
  --num-tablets 500 \
  --model l \
  --epochs 100 \
  --batch-size 32 \
  --device mps
```
**Time**: 4-6 hours  
**Output**: Production-ready model + detailed report

---

## Monitor Progress

Each run generates `pipeline_report.json`:
```bash
# View the report
cat pipeline_report.json | python -m json.tool

# Extract just timing information
python -c "import json; r=json.load(open('pipeline_report.json')); print('Total time:', r['total_execution_time_seconds'], 'seconds')"
```

---

## Troubleshooting

### "No annotated tablets found"
```bash
# You need annotations first. Create sample annotations:
python scripts/annotate_tablets.py
# Manually annotate at least one tablet, then retry
```

### "GPU out of memory"
```bash
# Reduce batch size
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation \
  --batch-size 4  # Reduced from 16
```

### "Training is too slow"
```bash
# Use smaller model
python scripts/run_complete_pipeline.py \
  --model s  # small instead of medium
  --epochs 10  # fewer epochs for testing
```

### "Want to interrupt and resume"
```bash
# Stop current run (Ctrl+C)
# Resume from next step:
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation \
  --skip-quality \
  --skip-training  # Skip to evaluation if training completed
```

---

## Understanding Output

### Console Output Example
```
======================================================================
  CUNEIFORM TRANSLATOR PIPELINE
======================================================================
Project root: /Users/jeffgoldner/Documents/CuniformTranslator
Data directory: data
Models directory: models
Started: 2026-01-21 22:15:14

▶ Validating Prerequisites
----------------------------------------------------------------------
✓ Python 3.9+
✓ All prerequisites met (6/6)

▶ STEP 1: Download Tablet Data
----------------------------------------------------------------------
✓ Downloaded 50 tablets

▶ STEP 2: Annotate Tablets
----------------------------------------------------------------------
⊘ Skipped by user

▶ STEP 3: Data Quality Validation
----------------------------------------------------------------------
✓ Data quality validation
  result: PASS

▶ STEP 4: Train YOLOv8 Sign Detection Model
----------------------------------------------------------------------
🎨 Training with 3D augmentation enabled
✓ Model training
  mAP: 0.823
  mAP50: 0.912

======================================================================
  PIPELINE SUMMARY
======================================================================

📊 EXECUTION TIMELINE
----------------------------------------------------------------------
  download              4m 05s
  annotation        20m 00s
  quality_check         0m 45s
  training          39m 00s
  evaluation            0m 16s

  Total pipeline   64m 06s

📋 RESULTS
----------------------------------------------------------------------
  ✓ download: success (count: 50)
  ✓ annotation: completed (count: 48)
  ✓ quality_check: success (result: PASS)
  ✓ training: success (mAP: 0.823)
  ✓ evaluation: complete

💡 NEXT STEPS
----------------------------------------------------------------------
  • Model training complete! Available models:
    - best.pt (3D augmented)
    - baseline_best.pt (for comparison)

  • To use the model for inference:
    python scripts/infer_signs.py --model models/best.pt \
      --image <tablet_image.jpg> --output predictions.json
```

### JSON Report (`pipeline_report.json`)
```json
{
  "timestamp": "2026-01-21T22:15:15.051470",
  "total_execution_time_seconds": 3847.32,
  "step_times": {
    "download": 245.3,
    "annotation": 1200.0,
    "quality_check": 45.2,
    "training": 2340.0,
    "evaluation": 16.8
  },
  "results": {
    "download": {
      "status": "success",
      "count": 50
    },
    "annotation": {
      "status": "completed",
      "count": 48
    },
    "quality_check": {
      "status": "success",
      "result": "PASS",
      "quality_score": 95
    },
    "training": {
      "status": "success",
      "model_size": "m",
      "epochs": 50,
      "batch_size": 16,
      "device": "mps",
      "augmentation_enabled": true,
      "trained_baseline": true,
      "metrics": {
        "baseline_mAP": 0.742,
        "augmented_mAP": 0.823,
        "improvement_percentage": 10.9
      }
    },
    "evaluation": {
      "status": "complete"
    }
  }
}
```

---

## Production Workflows

### Deploy on HPC Cluster
```bash
#!/bin/bash
#SBATCH --job-name=cuneiform-train
#SBATCH --time=6:00:00
#SBATCH --gpus=1
#SBATCH --mem=32GB

cd $SLURM_SUBMIT_DIR
python scripts/run_complete_pipeline.py \
  --enable-augmentation \
  --device cuda \
  --epochs 100 \
  --batch-size 64 \
  --num-tablets 500
```

### Deploy in Docker
```bash
# Build
docker build -t cuneiform-trainer .

# Run
docker run --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  cuneiform-trainer \
  python scripts/run_complete_pipeline.py \
    --enable-augmentation \
    --epochs 100
```

### Deploy with GitHub Actions
```yaml
name: Train Model on Schedule
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly at midnight

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: python scripts/run_complete_pipeline.py \
              --enable-augmentation --epochs 50
      - uses: actions/upload-artifact@v3
        with:
          name: models
          path: models/
      - uses: actions/upload-artifact@v3
        with:
          name: reports
          path: pipeline_report.json
```

---

## What to Measure

After running experiments, compare:

### Model Performance
- **mAP**: Mean Average Precision (main metric)
- **mAP50**: Precision at IoU=0.5
- **mAP75**: Precision at IoU=0.75
- **F1-score**: Balance of precision/recall

### Augmentation Impact
- `baseline_mAP` vs `augmented_mAP` improvement
- Percentage gain: `(augmented - baseline) / baseline * 100`
- Expected: 5-15% improvement from Stötzner et al. (2023)

### Resource Usage
- Training time per epoch
- GPU/CPU memory usage
- Total pipeline execution time

### Data Quality
- Annotation quality score (0-100)
- Inter-annotator agreement (kappa)
- Coverage (% of tablets annotated)

---

## Save Results for Research

```bash
# Create timestamped results archive
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir results_$timestamp

cp pipeline_report.json results_$timestamp/
cp models/best.pt results_$timestamp/
cp models/baseline_best.pt results_$timestamp/
cp -r data/yolo_dataset_augmented results_$timestamp/

# Archive for long-term storage
tar -czf cuneiform_results_$timestamp.tar.gz results_$timestamp/
```

---

## Recommended Testing Schedule

**Day 1 (2 hours)**
- Step 1: Download 50 tablets
- Step 2: Quick test with 10 tablets, 5 epochs

**Day 2 (4 hours)**
- Step 3: Compare augmentation (baseline vs 3D)

**Day 3+ (6+ hours)**
- Step 4: Production training on full dataset
- Publish results

---

## For Publication

When publishing research:
1. Include `pipeline_report.json` in supplementary materials
2. Document exact commands used
3. Report baseline vs augmented comparison
4. Share trained models on Hugging Face Model Hub
5. Link to GitHub repository

Example paper text:
```
We trained YOLOv8 models using the complete pipeline orchestrator
(https://github.com/UniswapSniper/Cuneiform-Translator-Tool).
The model with 3D augmentation achieved 82.3% mAP compared to 74.2%
for the baseline, representing an 10.9% improvement. All code,
data, and trained models are publicly available.
```

---

## Questions?

Refer to documentation:
- **Full Usage**: `docs/PIPELINE_ORCHESTRATION.md`
- **Architecture**: `WORKFLOW.md`
- **3D Rendering**: `docs/STEP4_3D_RENDERING_AUGMENTATION.md`
- **Troubleshooting**: `docs/PIPELINE_ORCHESTRATION.md#troubleshooting`

Happy researching! 🎉
