# Annotation format

This document describes the format used to store tablet annotations.

## Tablet record (JSON)

Each tablet is stored as a single JSON object with the following structure:

```json
{
  "tablet_id": "unique_string",
  "provenance": {
    "museum_id": "string or null",
    "museum": "string or null",
    "period": "string (e.g., 'Ur III', 'Old Babylonian')",
    "source_url": "string (canonical URL to primary source)",
    "source_license": "string (license terms for the tablet data itself)"
  },
  "image_paths": {
    "primary": "relative path to main image",
    "reverse": "optional reverse side",
    "edge": "optional edge"
  },
  "regions": [
    {
      "region_id": "unique_string_within_tablet",
      "type": "polygon" | "box",
      "coordinates": [[x1, y1], [x2, y2], ...],
      "sign_candidate": "proposed sign ID or null",
      "transliteration": "user-confirmed transliteration or empty string",
      "damaged": false | true,
      "uncertain": false | true,
      "notes": "free text",
      "annotated_by": "email or username",
      "timestamp": "ISO8601"
    }
  ],
  "metadata": {
    "language": "Sumerian" | "Akkadian" | ...,
    "genre": "administrative" | "literary" | ...,
    "date_created": "ISO8601",
    "status": "draft" | "review" | "approved"
  }
}
```

## Conventions

- **region_id** within a tablet should be stable across revisions (e.g., `r001`, `r002`, ...).
- **coordinates**: use image pixel coordinates; (0, 0) is top-left.
- **transliteration**: store the user-approved string; normalization happens in the translit module.
- **damaged** / **uncertain**: flags for scholarship, not ML classification.
- **sign_candidate**: can be null until ML model provides suggestions.

## Batch format (JSONL)

For efficiency, multiple tablet records are stored one-per-line in JSONL files (e.g., `data/processed/split_train.jsonl`).

## Version control

- Store annotations in git (not LFS) if < 100MB; otherwise use DVC.
- Include a `.gitattributes` for reproducible diff/merge behavior (TODO).
