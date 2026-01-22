# Data pipeline setup complete!

## What we've created

### 1. Data structure (`data/` directory)
```
data/
├── raw/
│   ├── cdli/              ← CDLI tablet downloads
│   ├── 3d_models/         ← 3D OBJ/PLY models  
│   └── oracc/             ← ORACC transliterations
├── interim/               ← Processed intermediates (renderings, augmentation)
└── processed/             ← Final annotated records (JSON/JSONL)
```

### 2. Download script (`scripts/download_cdli_tablets.py`)
- Batch download tablets from CDLI
- Downloads metadata, images (obverse/reverse/edge), and 3D models
- Respects rate limits (~0.5s per request)
- Currently uses mock data for testing (ready for real CDLI integration)

**Usage:**
```bash
# Download 50 Ur III tablets with 3D models
python scripts/download_cdli_tablets.py --period "Ur III" --limit 50 --with-3d

# Different language
python scripts/download_cdli_tablets.py --language Akkadian --limit 30

# Custom output directory
python scripts/download_cdli_tablets.py --cache-dir ./my_data --limit 100
```

### 3. Data pipeline module (`src/cuneiform_translator/io/pipeline.py`)
- **TabletRecord**: Pydantic model for annotation schema validation
- **DataPipeline**: Main class for loading/saving/validating
- Supports JSONL batch loading
- Validates records against schema

**Usage:**
```python
from cuneiform_translator.io import DataPipeline, TabletRecord

pipeline = DataPipeline()

# Validate a tablet record
record = pipeline.load_tablet_record("data/processed/sample.json")

# Batch validate directory
stats = pipeline.batch_validate("data/processed/")
print(f"Valid: {stats['valid']}/{stats['total']}")

# Load JSONL metadata
for tablet in pipeline.load_jsonl("data/raw/cdli/metadata.jsonl"):
    print(tablet['tablet_id'])
```

**CLI:**
```bash
# Validate single file
python -m cuneiform_translator.io.pipeline validate --input data/processed/sample.json

# Validate directory
python -m cuneiform_translator.io.pipeline validate --input data/processed/

# Get stats
python -m cuneiform_translator.io.pipeline stats --data-dir data/
```

### 4. Documentation
- [data/README.md](../data/README.md) — Data structure & flow
- [scripts/README.md](../scripts/README.md) — Script usage guide

## Quick start

### 1. Download test data
```bash
# Small batch to test pipeline
cd ~/Documents/CuniformTranslator

# Activate venv (if needed)
source .venv/bin/activate

# Download 10 Ur III tablets
/path/to/.venv/bin/python scripts/download_cdli_tablets.py --limit 10 --with-3d

# Check metadata
head data/raw/cdli/metadata.jsonl
```

### 2. Validate existing data
```bash
# Test validation on sample record
/path/to/.venv/bin/python -m cuneiform_translator.io.pipeline \
  validate --input data/processed/sample_tablet_record.json

# Should output: ✓ Valid: sample_001
```

### 3. Next steps (when ready)
- [ ] Connect real CDLI API (replace mock data)
- [ ] Build annotation CLI tool (M1)
- [ ] Add GigaMesh 3D rendering pipeline (M1)
- [ ] Create data augmentation (illumination variations)
- [ ] Set up YOLOv8 baseline for sign detection (M2)

## Architecture overview

```
User runs download script
  ↓
scripts/download_cdli_tablets.py
  ↓
data/raw/cdli/ (metadata.jsonl + images)
  ↓
data/raw/3d_models/ (3D OBJ files)
  ↓
[Future: Annotation tool / 3D rendering / Augmentation]
  ↓
src/cuneiform_translator/io/pipeline.py (validation & loading)
  ↓
data/processed/ (final annotated tablets)
  ↓
Model training
```

## Key updates to project

### Updated files
- `README.md` — Added research findings (Stötzner et al. 2023)
- `ROADMAP.md` — Added 3D data strategy, updated M0/M2 milestones
- `pyproject.toml` — Added `requests>=2.31` dependency

### New files
- `scripts/download_cdli_tablets.py` — CDLI download utility
- `scripts/README.md` — Script usage guide
- `src/cuneiform_translator/io/pipeline.py` — Data pipeline module
- `data/README.md` — Data directory structure guide
- `data/raw/cdli/` — Directory for CDLI downloads
- `data/raw/3d_models/` — Directory for 3D models
- `data/interim/` — Directory for processed intermediates

### Updated modules
- `src/cuneiform_translator/io/__init__.py` — Exported pipeline classes

## Next: Real CDLI integration

When ready to download real data:
1. Check CDLI's current data access options:
   - REST API: https://cdli.ucla.edu/
   - Database snapshots: https://github.com/cdli-data/
   - Data exports: https://cdli.ucla.edu/search

2. Update `download_cdli_tablets.py`:
   - Replace `_get_mock_tablets()` with real API calls
   - Handle CDLI's XML/CSV export formats
   - Implement error handling for network issues

3. Set up scheduled downloads if needed (Airflow/Cron)

## Questions?
See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup or check the project [ROADMAP.md](../ROADMAP.md) for next milestones.
