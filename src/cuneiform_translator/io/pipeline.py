"""
Data pipeline utilities for loading, validating, and processing tablet records.

This module handles:
- Loading raw tablet data (JSON, JSONL, images)
- Validation against annotation schema
- Converting between formats
- Caching and indexing
"""

import json
import logging
from pathlib import Path
from typing import Any, Iterator, Optional

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

# Project root for relative paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


class TabletProvenance(BaseModel):
    """Metadata about tablet origin and provenance."""

    museum_id: Optional[str] = None
    museum: Optional[str] = None
    period: str  # e.g., "Ur III", "Old Babylonian"
    source_url: Optional[str] = None
    source_license: str = "CC0 1.0 Universal"


class Region(BaseModel):
    """Annotated region on a tablet."""

    region_id: str
    type: str = Field(..., pattern="^(polygon|box)$")
    coordinates: list[list[float]]  # [[x1, y1], [x2, y2], ...]
    sign_candidate: Optional[str] = None
    transliteration: str = ""
    damaged: bool = False
    uncertain: bool = False
    notes: str = ""
    annotated_by: Optional[str] = None
    timestamp: Optional[str] = None


class TabletMetadata(BaseModel):
    """Metadata about a tablet."""

    language: str  # e.g., "Sumerian", "Akkadian"
    genre: str  # e.g., "administrative", "literary"
    date_created: str  # ISO 8601
    status: str = Field(default="draft", pattern="^(draft|review|approved)$")


class TabletRecord(BaseModel):
    """Complete tablet record (annotation schema)."""

    tablet_id: str
    provenance: TabletProvenance
    image_paths: dict[str, str]
    regions: list[Region] = []
    metadata: TabletMetadata


class DataPipeline:
    """Manage data loading, validation, and processing."""

    def __init__(self, data_dir: Path = DATA_DIR):
        """Initialize pipeline."""
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.interim_dir = self.data_dir / "interim"
        self.processed_dir = self.data_dir / "processed"

    def load_jsonl(self, filepath: Path) -> Iterator[dict[str, Any]]:
        """
        Load JSONL file (one JSON record per line).

        Yields:
            Parsed JSON objects
        """
        with open(filepath) as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON at line {i}: {e}")

    def load_tablet_record(self, filepath: Path) -> Optional[TabletRecord]:
        """
        Load and validate a tablet record.

        Args:
            filepath: Path to JSON file

        Returns:
            Validated TabletRecord, or None if invalid
        """
        try:
            with open(filepath) as f:
                data = json.load(f)
            record = TabletRecord(**data)
            return record
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to load {filepath}: {e}")
            return None

    def save_tablet_record(self, record: TabletRecord, filepath: Path) -> bool:
        """
        Save tablet record to JSON file.

        Args:
            record: TabletRecord to save
            filepath: Output path

        Returns:
            True if successful
        """
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(record.model_dump(), f, indent=2)
            return True
        except IOError as e:
            logger.error(f"Failed to save {filepath}: {e}")
            return False

    def validate_record(self, data: dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate tablet record against schema.

        Args:
            data: Raw record data

        Returns:
            (is_valid, error_message)
        """
        try:
            TabletRecord(**data)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def load_raw_cdli_metadata(self) -> Iterator[dict[str, Any]]:
        """Load metadata from raw CDLI downloads."""
        metadata_file = self.raw_dir / "cdli" / "metadata.jsonl"
        if metadata_file.exists():
            yield from self.load_jsonl(metadata_file)
        else:
            logger.warning(f"Metadata file not found: {metadata_file}")

    def batch_validate(self, input_dir: Path) -> dict[str, Any]:
        """
        Validate all JSON files in a directory.

        Args:
            input_dir: Directory containing JSON files

        Returns:
            Summary stats (total, valid, invalid)
        """
        stats = {"total": 0, "valid": 0, "invalid": 0, "errors": []}

        for json_file in sorted(input_dir.glob("*.json")):
            stats["total"] += 1
            is_valid, error = self.validate_record(
                json.loads(json_file.read_text())
            )
            if is_valid:
                stats["valid"] += 1
            else:
                stats["invalid"] += 1
                stats["errors"].append({"file": json_file.name, "error": error})

        return stats


def main():
    """CLI for data pipeline operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Data pipeline utilities")
    parser.add_argument(
        "command",
        choices=["validate", "load", "stats"],
        help="Pipeline command",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Input file or directory",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Data root directory",
    )

    args = parser.parse_args()
    pipeline = DataPipeline(args.data_dir)

    if args.command == "validate":
        if args.input:
            if args.input.is_dir():
                stats = pipeline.batch_validate(args.input)
                print(f"Validation results: {stats['valid']}/{stats['total']} valid")
                if stats["errors"]:
                    print("Errors:")
                    for err in stats["errors"][:5]:
                        print(f"  {err['file']}: {err['error']}")
            else:
                record = pipeline.load_tablet_record(args.input)
                if record:
                    print(f"✓ Valid: {record.tablet_id}")
                else:
                    print("✗ Invalid record")

    elif args.command == "load":
        if args.input:
            for tablet in pipeline.load_jsonl(args.input):
                print(f"Loaded: {tablet.get('tablet_id')}")

    elif args.command == "stats":
        processed_dir = pipeline.processed_dir
        if processed_dir.exists():
            tablets = list(pipeline.load_jsonl(processed_dir / "*.jsonl"))
            print(f"Total tablets: {len(tablets)}")
        else:
            print("No processed data found")


if __name__ == "__main__":
    main()
