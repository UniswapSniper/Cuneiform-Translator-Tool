# Development setup

## Setup (macOS with uv or pip)

### Option A: Using `uv` (recommended, fast)
```bash
# Install uv: https://docs.astral.sh/uv/
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv + install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Option B: Using `pip`
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running tests
```bash
pytest tests/ -v
# or with coverage:
pytest tests/ --cov=src/cuneiform_translator --cov-report=html
```

## Code style & linting
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

## Next steps (M0/M1)
1. Try `pytest tests/test_sample.py` — should pass if paths are correct.
2. Check the sample tablet record at `data/processed/sample_tablet_record.json`.
3. Read [docs/annotation_format.md](docs/annotation_format.md) to understand the data schema.
4. Read [docs/datasets.md](docs/datasets.md) for current data sourcing plan.
5. Check [docs/decisions.md](docs/decisions.md) for rationale behind design choices.
