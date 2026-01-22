# Scripts guide

Quick utility scripts for data pipeline, annotation, and model tasks.

## download_cdli_tablets.py

Download cuneiform tablets from CDLI (Cuneiform Digital Library Initiative).

### Basic usage

**Download 50 Ur III tablets with images:**
```bash
python scripts/download_cdli_tablets.py --period "Ur III" --limit 50
```

**Also download 3D models (when available):**
```bash
python scripts/download_cdli_tablets.py --period "Ur III" --limit 50 --with-3d
```

**Different language:**
```bash
python scripts/download_cdli_tablets.py --language Akkadian --limit 30
```

**Custom cache directory:**
```bash
python scripts/download_cdli_tablets.py --cache-dir ./my_data/cdli_downloads --limit 20
```

### Output

Downloads are stored in `data/raw/cdli/`:
- `metadata.jsonl` — Tablet metadata (one JSON per line)
- `P{number}_obverse.jpg` — Tablet images
- `P{number}_reverse.jpg`
- `P{number}_edge.jpg` (if available)

3D models (if `--with-3d`) go in `data/raw/3d_models/{tablet_id}/`

### Rate limiting

The script respects CDLI's courtesy rate limit (0.5s between requests).
For bulk downloads, consider downloading CDLI's full database snapshot instead.

## Usage patterns

### 1. Fresh data download
```bash
# Start with ~50-100 tablets to test annotation workflow
python scripts/download_cdli_tablets.py --period "Ur III" --limit 100 --with-3d

# Check what was downloaded
ls -lh data/raw/cdli/ | head -20
wc -l data/raw/cdli/metadata.jsonl
```

### 2. Validate downloaded data
```bash
# Check if all tablets have required fields
python -m cuneiform_translator.io.pipeline validate --input data/raw/cdli/metadata.jsonl
```

### 3. Check stats
```bash
# See download summary
python -m cuneiform_translator.io.pipeline stats --data-dir data/
```

## Notes for future development

- **CDLI API**: Currently using mock data. When CDLI's API stabilizes, replace with real API calls
- **3D models**: CDLI is expanding 3D photogrammetry coverage. Check their 3D archive regularly
- **ORACC integration**: Add `download_oracc_corpus.py` for transliteration validation
- **GigaMesh rendering**: Add `render_3d_gigamesh.py` to convert 3D models to MSII/Phong renderings
