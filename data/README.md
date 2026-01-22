# Data directory structure

```
data/
├── raw/                          # Original, unprocessed data
│   ├── cdli/                     # CDLI tablet data
│   │   ├── metadata.jsonl        # Tablet metadata (downloaded from CDLI)
│   │   ├── P100001_obverse.jpg   # Tablet images
│   │   ├── P100001_reverse.jpg
│   │   └── ...
│   ├── 3d_models/                # 3D model files (OBJ, PLY, etc.)
│   │   ├── P100001/
│   │   │   ├── P100001.obj       # Wavefront OBJ format
│   │   │   └── P100001.mtl       # Material file
│   │   └── ...
│   └── oracc/                    # ORACC transliteration data
│       └── oracc_lemmas.json     # Lexical data
├── interim/                      # Intermediate processing artifacts
│   ├── rendered_3d/              # 3D renderings (MSII, Phong-shaded)
│   │   ├── P100001_msii.png
│   │   ├── P100001_phong.png
│   │   └── ...
│   └── augmented/                # Illumination-augmented images
│       ├── P100001_aug_001.jpg
│       └── ...
└── processed/                    # Final annotation data
    ├── MANIFEST.md               # Data manifest & statistics
    ├── sample_tablet_record.json
    └── split_train.jsonl         # Training set (JSONL format)
```

## Data flow

```
CDLI API
  ↓
download_cdli_tablets.py → raw/cdli/ (images, metadata)
  ↓
raw/3d_models/ (3D OBJ files)
  ↓
render_3d_models.py (GigaMesh or custom renderer)
  ↓
interim/rendered_3d/ (PNG/JPG renderings)
  ↓
augmentation.py (illumination variations)
  ↓
interim/augmented/ (augmented images)
  ↓
annotation tool (manual annotation)
  ↓
processed/ (final annotated tablets in JSON/JSONL)
  ↓
Model training
```

## File naming conventions

### Images
- **Obverse (front)**: `{tablet_id}_obverse.jpg`
- **Reverse (back)**: `{tablet_id}_reverse.jpg`
- **Edge**: `{tablet_id}_edge.jpg`
- **Rendered 3D (MSII)**: `{tablet_id}_msii.png`
- **Rendered 3D (Phong)**: `{tablet_id}_phong.png`
- **Augmented**: `{tablet_id}_aug_{variant}.jpg` (e.g., `_aug_001.jpg`)

### Metadata & records
- **Metadata**: One JSON per line in `metadata.jsonl`
- **Annotated records**: `{tablet_id}.json` in `processed/`
- **Batches**: `split_{train|val|test}.jsonl`

## Downloading data

### Quick start (50 Ur III tablets with 3D models)
```bash
python scripts/download_cdli_tablets.py \
  --period "Ur III" \
  --limit 50 \
  --with-3d
```

### Full dataset (all available)
```bash
python scripts/download_cdli_tablets.py \
  --period "Ur III" \
  --limit 500 \
  --language Sumerian \
  --with-3d
```

## Data validation

```bash
python -m cuneiform_translator.io.pipeline validate --input data/processed/
```

## Statistics

Track in `data/processed/MANIFEST.md`:
- Total tablets: ~N
- Annotated: ~M
- With 3D models: ~K
- Languages: (list)
- Periods: (list)
- Inter-annotator agreement (Fleiss' kappa): X.XX

## License

All data sourced from:
- **CDLI**: CC0 1.0 Universal (Public Domain)
- **ORACC**: CC0 1.0 Universal (with attribution)

See [docs/datasets.md](../docs/datasets.md) for full licensing details.
