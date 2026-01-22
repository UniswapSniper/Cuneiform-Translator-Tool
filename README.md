# Cuneiform Translator

Translating ancient Sumerian cuneiform tablets from image to transliteration, with machine learning-powered sign recognition and optional English glossing.

## Overview

This project aims to build a comprehensive pipeline for digitizing, annotating, and translating cuneiform tablets. We combine computer vision, natural language processing, and domain expertise to unlock knowledge from one of humanity's oldest writing systems.

**Current phase (M0):** Annotation infrastructure & data pipeline  
**MVP target:** Full tablet → transliteration workflow with manual review  
**Future phases:** ML-powered sign recognition, English glossing, web UI

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

### M0 (MVP Foundation)
- ✅ Project structure & module layout
- ✅ Annotation format schema
- 🚧 Data ingestion from CDLI (photos + 3D models)
- 🚧 3D rendering pipeline (GigaMesh integration)
- 🚧 Basic annotation tool (CLI)
- 🚧 Test suite & CI/CD

### M1 (Enhanced annotation)
- Batch annotation workflow
- Inter-annotator agreement metrics
- Data quality checks
- Web-based annotation UI (Streamlit)

### M2+ (Machine learning)
- Vision-based sign recognition
- Transliteration RNN/Transformer
- English glossing model
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
