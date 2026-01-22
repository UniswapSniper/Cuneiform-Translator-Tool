# Pipeline Orchestration Guide

**Status**: ✅ Complete  
**Added**: Jan 21, 2026  
**Location**: `scripts/run_complete_pipeline.py`

## Overview

The **Pipeline Orchestrator** is a unified entry point that manages the entire Cuneiform Translator workflow in a single command. Instead of running 5+ separate scripts, users can now orchestrate the complete pipeline with a single control interface.

## What It Does

```
run_complete_pipeline.py orchestrates:

1. DOWNLOAD  → Fetch tablets from CDLI
2. ANNOTATE  → Interactive region & sign labeling
3. VALIDATE  → Quality checks & inter-annotator agreement
4. TRAIN     → YOLOv8 model with optional 3D augmentation
5. EVALUATE  → Summary reports & model comparison
```

All with:
- ✅ Integrated progress tracking
- ✅ Skip flags for individual steps
- ✅ JSON report generation
- ✅ Timing metrics
- ✅ Error handling & validation

## Quick Start

### Full Pipeline (Recommended)

```bash
# Complete workflow with 3D augmentation
python scripts/run_complete_pipeline.py --mode full --enable-augmentation
```

This runs all 5 steps with 3D depth augmentation enabled.

### With Baseline Comparison

```bash
# Train both baseline AND 3D-augmented for direct comparison
python scripts/run_complete_pipeline.py \
  --mode full \
  --enable-augmentation \
  --train-baseline
```

Produces two trained models so you can compare:
- `baseline_best.pt` - Standard YOLOv8
- `best.pt` - YOLOv8 with 3D augmentation

### Skip Existing Steps

```bash
# You've already downloaded and annotated data?
# Jump straight to training:
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation \
  --skip-quality
```

### Training Only

```bash
# Pre-configured shorthand for skipping to training
python scripts/run_complete_pipeline.py --mode training-only
```

### Interactive Mode

```bash
# Get prompted at each step
python scripts/run_complete_pipeline.py --mode interactive
```

## Command Reference

### Modes

| Mode | Behavior |
|------|----------|
| `--mode full` (default) | Run all steps non-interactively |
| `--mode interactive` | Prompt for confirmation at each step |
| `--mode training-only` | Skip data prep, go straight to training |

### Step Control

| Flag | Effect |
|------|--------|
| `--skip-download` | Don't download tablets |
| `--skip-annotation` | Don't prompt for annotation |
| `--skip-quality` | Don't run quality validation |
| `--skip-training` | Don't train model |
| `--skip-evaluation` | Don't generate final report |

### Training Options

| Option | Default | Options |
|--------|---------|---------|
| `--enable-augmentation` | (disabled) | Enable 3D augmentation |
| `--train-baseline` | (disabled) | Also train non-augmented baseline |
| `--model` | `m` | `n`, `s`, `m`, `l`, `x` (YOLO sizes) |
| `--epochs` | `50` | Any integer |
| `--batch-size` | `16` | Any integer (adjust for GPU memory) |
| `--device` | `mps` | `cpu`, `cuda`, `mps` |

### Data Locations

| Option | Purpose |
|--------|---------|
| `--project-root` | Project directory (auto-detected) |
| `--data-dir` | Data storage location |
| `--models-dir` | Where to save trained models |

### Data Options

| Option | Default |
|--------|---------|
| `--num-tablets` | `50` |

## Usage Examples

### Example 1: Quick Test (Small Dataset)

```bash
python scripts/run_complete_pipeline.py \
  --num-tablets 10 \
  --epochs 5 \
  --batch-size 8
```

- Downloads 10 tablets
- Trains for 5 epochs (fast)
- Uses batch size 8 (lower memory)
- Good for testing setup

### Example 2: Production Training with Augmentation

```bash
python scripts/run_complete_pipeline.py \
  --mode full \
  --enable-augmentation \
  --num-tablets 200 \
  --model l \
  --epochs 100 \
  --batch-size 32 \
  --device cuda
```

- 200 tablets
- Large YOLOv8 model (better accuracy)
- 100 epochs (thorough training)
- 3D augmentation enabled
- GPU training

### Example 3: Resume from Existing Data

```bash
# Already have annotated tablets? Skip to training.
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation \
  --skip-quality \
  --enable-augmentation \
  --epochs 50
```

### Example 4: Compare Models

```bash
# Train both baseline and augmented to see improvement
python scripts/run_complete_pipeline.py \
  --mode full \
  --enable-augmentation \
  --train-baseline \
  --epochs 50 \
  --batch-size 16
```

Output shows:
- Baseline model mAP
- 3D-augmented model mAP
- Improvement percentage

### Example 5: Interactive Session

```bash
python scripts/run_complete_pipeline.py --mode interactive
```

Output:
```
======================================================================
  CUNEIFORM TRANSLATOR PIPELINE
======================================================================

▶ Validating Prerequisites
----------------------------------------------------------------------
✓ Python 3.9+
✓ All prerequisites met (6/6)

▶ STEP 1: Download Tablet Data
----------------------------------------------------------------------
Proceed with STEP 1: Download Tablet Data? [y/N]: y

[Downloads 50 tablets...]

▶ STEP 2: Annotate Tablets
----------------------------------------------------------------------
Proceed with STEP 2: Annotate Tablets? [y/N]: y

To annotate tablets:
  python scripts/annotate_tablets.py

Annotations will be saved to:
  data/processed

Press Enter once you've completed annotations...
[User annotates, then presses Enter]

▶ STEP 3: Data Quality Validation
----------------------------------------------------------------------
[Validation runs...]

✓ Data quality validation
  result: PASS
  coverage: 100%
```

## Output & Reports

### Pipeline Report (`pipeline_report.json`)

Generated after each run with:

```json
{
  "timestamp": "2026-01-21T21:46:22.123456",
  "total_execution_time_seconds": 3847,
  "step_times": {
    "download": 245.3,
    "annotation": 1200.0,
    "quality_check": 45.2,
    "training": 2340.0,
    "evaluation": 16.5
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
      "result": "PASS"
    },
    "training": {
      "status": "success",
      "model_size": "m",
      "epochs": 50,
      "augmentation_enabled": true,
      "trained_baseline": true
    },
    "evaluation": {
      "status": "complete"
    }
  }
}
```

### Console Output

The orchestrator shows:

1. **Prerequisites Check** - Validates environment
2. **Execution Timeline** - Timing for each step
3. **Results Summary** - Status and metrics for each step
4. **Next Steps** - Recommendations based on results

Example:
```
📊 EXECUTION TIMELINE
----------------------------------------------------------------------
  download              4m 05s
  annotation        20m 00s (manual)
  quality_check         0m 45s
  training          39m 00s
  evaluation            0m 16s

  Total pipeline   64m 06s

📋 RESULTS
----------------------------------------------------------------------
  ✓ download: success
      count: 50
  ✓ annotation: completed
      count: 48
  ✓ quality_check: success
      result: PASS
  ✓ training: success
      model_size: m
      epochs: 50
      augmentation_enabled: true
  ✓ evaluation: complete

💡 NEXT STEPS
----------------------------------------------------------------------
  • Model training complete! Available models:
    - baseline_best.pt
    - best.pt

  • To use the model for inference:
    python scripts/infer_signs.py --model models/best.pt \
      --image <tablet_image.jpg> --output predictions.json
```

## How It Works

### Prerequisite Validation (30 seconds)

Checks:
- Python 3.9+ installed
- Project structure intact
- Required packages (NumPy, OpenCV, etc.)
- Directories writable

### Step 1: Download (5-10 minutes)

- Fetches tablet images from CDLI
- Downloads metadata
- Skips if data already exists
- Falls back to mock data if API unavailable

### Step 2: Annotation (Manual, 15-60 minutes)

- Launches interactive annotation tool
- User draws regions around signs
- Waits for user completion
- Counts annotated tablets

### Step 3: Quality Check (1-2 minutes)

- Validates annotation integrity
- Checks for overlapping regions
- Verifies coordinate bounds
- Calculates inter-annotator agreement (if multiple annotators)
- Reports: PASS / WARNING / FAIL

### Step 4: Training (30-120 minutes, depending on configuration)

- Converts annotations to YOLO format
- Optionally generates 3D-augmented images
- Trains YOLOv8 on dataset
- Optionally trains baseline for comparison
- Saves best model weights

### Step 5: Evaluation (1-2 minutes)

- Generates comprehensive report
- Calculates mAP and other metrics
- Creates JSON summary
- Recommends next steps

## Troubleshooting

### "Python 3.9+ required"
```bash
# Use explicit Python path
/usr/bin/python3.11 scripts/run_complete_pipeline.py
```

### "Missing required package"
```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

### Training stops with OOM (out of memory)
```bash
# Reduce batch size and resolution
python scripts/run_complete_pipeline.py \
  --batch-size 8 \
  --model n
```

### "No annotated tablets found"
```bash
# Manually annotate first
python scripts/annotate_tablets.py

# Then resume
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation
```

### Report shows poor mAP
```bash
# Try with more augmentation and epochs
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation \
  --enable-augmentation \
  --epochs 100 \
  --batch-size 32
```

## Integration with Other Tools

The orchestrator calls existing scripts:
- `download_cdli_tablets.py` - Data fetching
- `annotate_tablets.py` - Interactive annotation
- `validate_tablets.py` - Quality checks
- `train_sign_detector_3d.py` - Model training
- `infer_signs.py` - Inference

You can still use these independently for advanced usage.

## For Web UI Development (Step 5)

The orchestrator is perfect for prototyping a web interface:

### Current Flow (CLI)
```
User runs:
  python run_complete_pipeline.py --enable-augmentation

Orchestrator calls scripts in sequence ✓
```

### Future Flow (Web UI)
```
User clicks:
  [START PIPELINE] button

Web backend calls:
  run_complete_pipeline.py --enable-augmentation

Web frontend shows:
  Real-time progress bars ← Parse stdout
  Metrics dashboard ← Parse pipeline_report.json
  Model comparison graphs ← Extract from results
```

The JSON report and structured output make it easy to build a web UI on top.

## Advanced Configuration

### Custom Data Paths

```bash
python scripts/run_complete_pipeline.py \
  --data-dir /mnt/shared_storage/cuneiform_data \
  --models-dir /mnt/shared_storage/models \
  --project-root /app/cuneiform
```

### Batch Processing

```bash
# Run multiple training experiments
for batch_size in 8 16 32; do
  python scripts/run_complete_pipeline.py \
    --skip-download \
    --skip-annotation \
    --skip-quality \
    --batch-size $batch_size \
    --enable-augmentation
done
```

### Reproducible Results

```bash
# Save config for exact reproduction
python scripts/run_complete_pipeline.py \
  --mode full \
  --enable-augmentation \
  --model m \
  --epochs 50 \
  --batch-size 16
  # Results saved to pipeline_report.json

# Reproduce later with same settings
python scripts/run_complete_pipeline.py \
  --skip-download \
  --skip-annotation \
  --model m \
  --epochs 50 \
  --batch-size 16 \
  --enable-augmentation
```

## Next Steps

1. **Run a test pipeline** - See how it works with small data
2. **Examine the report** - Understand metrics and timing
3. **Experiment with options** - Try different model sizes, batch sizes
4. **Compare models** - Use `--train-baseline` to see 3D augmentation benefits
5. **Build web UI** (Step 5/M3) - Use orchestrator as backend

The orchestrator is production-ready and can be used as-is for research and production workflows.
