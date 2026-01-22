# Manifest of processed datasets

This file tracks all datasets used in the project: sources, licenses, splits, and paths.

## Format (JSONL)
Each line is a JSON object with:
- `name`: dataset identifier
- `source`: where it came from (URL + date)
- `license`: license/terms
- `subset`: train / val / test
- `num_tablets`: count of tablets
- `num_regions`: count of annotated regions
- `path`: local directory path
- `notes`: any relevant caveats or metadata

## Example

```jsonl
{"name": "cdli_sample", "source": "https://cdli.ucla.edu/search", "license": "CC0 1.0 Universal", "subset": "train", "num_tablets": 10, "num_regions": 50, "path": "data/processed/cdli_sample_train", "notes": "Ur III admin texts, high-quality photos"}
{"name": "cdli_sample", "source": "https://cdli.ucla.edu/search", "license": "CC0 1.0 Universal", "subset": "val", "num_tablets": 2, "num_regions": 12, "path": "data/processed/cdli_sample_val", "notes": "Held out for validation"}
```

## Current datasets
(empty for now — populate as you download and process data)
