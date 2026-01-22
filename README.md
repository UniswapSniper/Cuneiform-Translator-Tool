# Cuneiform Translator

Translating ancient Sumerian cuneiform tablets from image to transliteration, with machine learning-powered sign recognition and optional English glossing.

## Overview

This project aims to build a comprehensive pipeline for digitizing, annotating, and translating cuneiform tablets. We combine computer vision, natural language processing, and domain expertise to unlock knowledge from one of humanity's oldest writing systems.

**Current phase (M0):** Annotation infrastructure & data pipeline  
**MVP target:** Full tablet → transliteration workflow with manual review  
**Future phases:** ML-powered sign recognition, English glossing, web UI

## Project Status: Steps 1-4 Complete ✅

### Recent Completions

- **Step 1 (Dec 2025)**: CDLI REST API integration framework with mock data fallback
- **Step 2 (Jan 21, 2026)**: Data quality checks & inter-annotator agreement metrics
- **Step 3 (Jan 21, 2026)**: YOLOv8 baseline sign detection model training pipeline
- **Step 4 (Jan 21, 2026)**: 3D rendering & augmentation pipeline for improved model training

See [docs/](docs/) for detailed step documentation:
- [CDLI_API_INTEGRATION.md](docs/CDLI_API_INTEGRATION.md)
- [STEP2_DATA_QUALITY_AND_IAA.md](docs/STEP2_DATA_QUALITY_AND_IAA.md)
- [STEP3_YOLOV8_BASELINE.md](docs/STEP3_YOLOV8_BASELINE.md)
- [STEP4_3D_RENDERING_AUGMENTATION.md](docs/STEP4_3D_RENDERING_AUGMENTATION.md)

## Quick Start

### Prerequisites
- Python 3.11+
- macOS, Linux, or WSL

### Installation

#### Option A: Using `uv` (recommended, fast)
```bash
# Install uv: https://docs.astral.sh/uv/
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv + install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

#### Option B: Using `pip`
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run the Complete Pipeline

The easiest way to get started is with the unified pipeline orchestrator:

```bash
# Full pipeline with 3D augmentation (recommended)
python scripts/run_complete_pipeline.py --mode full --enable-augmentation

# Compare baseline vs. 3D-augmented models
python scripts/run_complete_pipeline.py --enable-augmentation --train-baseline

# Skip to training (if you already have annotated data)
python scripts/run_complete_pipeline.py --skip-download --skip-annotation

# Interactive mode (prompts for each step)
python scripts/run_complete_pipeline.py --mode interactive
```

See [docs/PIPELINE_ORCHESTRATION.md](docs/PIPELINE_ORCHESTRATION.md) for complete usage guide.

### Running tests
```bash
pytest tests/ -v
# or with coverage:
pytest tests/ --cov=src/cuneiform_translator --cov-report=html
```

### Code quality
```bash
# Format
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Project structure

```
cuneiform-translator/
├── src/cuneiform_translator/     # Main package
│   ├── eval/                     # Evaluation metrics & tools
│   ├── io/                       # Data loading & serialization
│   ├── lexicon/                  # Sumerian sign lexicon & lookup
│   ├── translit/                 # Transliteration normalization & processing
│   ├── ui/                       # User interface (web, CLI)
│   └── vision/                   # Computer vision & image processing
├── tests/                        # Unit & integration tests
├── data/
│   └── processed/                # Annotation data (JSON/JSONL)
└── docs/                         # Design & decision documents
```

## Documentation

- [Annotation format](docs/annotation_format.md) — JSON schema for tablet records
- [Datasets & provenance](docs/datasets.md) — Data sources and licenses
- [Design decisions](docs/decisions.md) — Technical & process decisions
- [Contributing](CONTRIBUTING.md) — Development setup & guidelines
- [Roadmap](ROADMAP.md) — Feature roadmap & milestones

## Key components

### io
Handles loading and serializing tablet records. Validates against the annotation schema.

### vision
Computer vision utilities for image processing, region extraction, and (later) sign recognition.

### translit
Transliteration normalization, cuneiform sign disambiguation, and rule-based processing.

### lexicon
Sign lookups, historical variants, and Sumerian/Akkadian lexical data.

### eval
Evaluation metrics, inter-annotator agreement, and model benchmarking.

### ui
User-facing tools (CLI, web interface) for annotation, review, and translation.

## Data sources

This project uses publicly available datasets:

- **CDLI** (Cuneiform Digital Library Initiative): ~500k+ tablets, high-quality images + 3D models, CC0 licensed
- **ORACC** (Open Richly Annotated Cuneiform Corpus): Transliteration corpora for validation, CC0 licensed

See [docs/datasets.md](docs/datasets.md) for licensing details and integration status.

## Existing research & models

This project builds on established research:

- **Stötzner et al. (2023)**: [CNN-based Cuneiform Sign Detection](https://hf.co/papers/2308.11277) — RepPoints detector for sign localization, HeiCuBeDa/MaiCuBeDa datasets (~500 annotated tablets)
- **Key insight**: 3D renderings significantly improve detection accuracy on photographs
- **Recommended vision baseline**: YOLOv8 for quick prototyping, RepPoints for production
- **Related work**: GigaMesh for 3D rendering, illumination augmentation techniques

## Current focus

### M0 (MVP Foundation) — ~95% Complete
- ✅ Project structure & module layout
- ✅ Annotation format schema
- ✅ Data pipeline from CDLI API
- ✅ Annotation CLI tool with region management
- ✅ Data quality validation & IAA metrics
- ✅ YOLO dataset conversion & training pipeline
- ✅ 3D rendering & augmentation pipeline (GigaMesh-ready)
- 🚧 CI/CD & test automation

### M1 (Annotation Workflow) — ~90% Complete
- ✅ Batch annotation capability
- ✅ Inter-annotator agreement metrics (Fleiss' kappa, IoU-based)
- ✅ Data quality checks (overlaps, bounds validation)
- ✅ Quality scoring (0-100 with PASS/WARNING/FAIL)
- 🚧 Web-based annotation UI (Streamlit)
- 🚧 Advanced comparison workflows

### M2 (ML Pipeline) — ~80% Complete
- ✅ YOLOv8 sign detection baseline
- ✅ Training data converter (annotated tablets → YOLO format)
- ✅ End-to-end training orchestration
- ✅ Inference engine with batch prediction
- ✅ Prediction export (JSON/JSONL/CSV)
- 🚧 3D rendering with GigaMesh
- 🚧 RepPoints ensemble for production
- 🚧 Sign classification model

### M3+ (Production) — Planned
- REST API service
- Web UI for annotation & translation
- Transfer learning pipelines
- English glossing with NLP
- Benchmark datasets & leaderboards

See [ROADMAP.md](ROADMAP.md) for detailed timeline and feature breakdown.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and development guidelines.

## License

This project is licensed under MIT. Tablet data uses public domain (CC0) sources with proper attribution.

## Team

**Cuneiform Team** — team@example.com

## References

- CDLI: https://cdli.ucla.edu/
- ORACC: http://oracc.museum.upenn.edu/
- Cuneiform writing systems: https://en.wikipedia.org/wiki/Cuneiform

---

Questions? Open an issue or start a discussion!
