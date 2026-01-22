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
from collections import defaultdict
from shapely.geometry import Polygon, box

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

    # ===== Data Quality Checks =====

    def check_overlapping_regions(self, record: TabletRecord) -> dict[str, Any]:
        """
        Detect overlapping or intersecting regions in a tablet.

        Args:
            record: TabletRecord to check

        Returns:
            Report with overlapping region pairs and intersection details
        """
        report = {
            "tablet_id": record.tablet_id,
            "total_regions": len(record.regions),
            "overlapping_pairs": [],
            "has_overlaps": False,
        }

        regions = record.regions
        for i in range(len(regions)):
            for j in range(i + 1, len(regions)):
                region_i = regions[i]
                region_j = regions[j]

                try:
                    if region_i.type == "polygon" and region_j.type == "polygon":
                        poly_i = Polygon(region_i.coordinates)
                        poly_j = Polygon(region_j.coordinates)
                    elif region_i.type == "box" and region_j.type == "box":
                        # Box format: [[x_min, y_min], [x_max, y_max]]
                        poly_i = box(
                            region_i.coordinates[0][0],
                            region_i.coordinates[0][1],
                            region_i.coordinates[1][0],
                            region_i.coordinates[1][1],
                        )
                        poly_j = box(
                            region_j.coordinates[0][0],
                            region_j.coordinates[0][1],
                            region_j.coordinates[1][0],
                            region_j.coordinates[1][1],
                        )
                    else:
                        continue

                    if poly_i.intersects(poly_j):
                        intersection = poly_i.intersection(poly_j)
                        report["overlapping_pairs"].append(
                            {
                                "region_i": region_i.region_id,
                                "region_j": region_j.region_id,
                                "intersection_area": float(intersection.area),
                                "region_i_area": float(poly_i.area),
                                "region_j_area": float(poly_j.area),
                                "overlap_percent_i": (
                                    float(intersection.area) / float(poly_i.area) * 100
                                    if poly_i.area > 0
                                    else 0
                                ),
                                "overlap_percent_j": (
                                    float(intersection.area) / float(poly_j.area) * 100
                                    if poly_j.area > 0
                                    else 0
                                ),
                            }
                        )
                        report["has_overlaps"] = True

                except Exception as e:
                    logger.warning(
                        f"Error checking overlap between {region_i.region_id} and {region_j.region_id}: {e}"
                    )

        return report

    def check_bounds_validity(self, record: TabletRecord, image_width: int = 1024, image_height: int = 768) -> dict[str, Any]:
        """
        Validate that all regions are within valid bounds.

        Args:
            record: TabletRecord to check
            image_width: Expected image width
            image_height: Expected image height

        Returns:
            Report with out-of-bounds regions and invalid coordinates
        """
        report = {
            "tablet_id": record.tablet_id,
            "image_width": image_width,
            "image_height": image_height,
            "total_regions": len(record.regions),
            "invalid_regions": [],
            "has_errors": False,
        }

        for region in record.regions:
            issues = []

            for i, coord in enumerate(region.coordinates):
                if len(coord) != 2:
                    issues.append(f"Coordinate {i} has {len(coord)} values (expected 2)")
                    report["has_errors"] = True

                x, y = coord
                if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                    issues.append(f"Coordinate {i} has non-numeric values: {coord}")
                    report["has_errors"] = True
                elif x < 0 or x > image_width:
                    issues.append(
                        f"Coordinate {i} x={x} out of bounds [0, {image_width}]"
                    )
                    report["has_errors"] = True
                elif y < 0 or y > image_height:
                    issues.append(
                        f"Coordinate {i} y={y} out of bounds [0, {image_height}]"
                    )
                    report["has_errors"] = True

            if issues:
                report["invalid_regions"].append(
                    {
                        "region_id": region.region_id,
                        "type": region.type,
                        "coord_count": len(region.coordinates),
                        "issues": issues,
                    }
                )

        return report

    def generate_quality_report(self, record: TabletRecord, image_width: int = 1024, image_height: int = 768) -> dict[str, Any]:
        """
        Generate comprehensive data quality report.

        Args:
            record: TabletRecord to analyze
            image_width: Expected image width
            image_height: Expected image height

        Returns:
            Comprehensive quality report
        """
        overlap_report = self.check_overlapping_regions(record)
        bounds_report = self.check_bounds_validity(record, image_width, image_height)

        report = {
            "tablet_id": record.tablet_id,
            "quality_score": 100.0,
            "quality_status": "pass",
            "checks": {
                "overlapping_regions": overlap_report,
                "bounds_validity": bounds_report,
            },
            "issues": [],
        }

        # Deduct points for issues
        if overlap_report["has_overlaps"]:
            penalty = len(overlap_report["overlapping_pairs"]) * 5
            report["quality_score"] -= penalty
            report["issues"].append(
                f"{len(overlap_report['overlapping_pairs'])} overlapping region pairs"
            )

        if bounds_report["has_errors"]:
            penalty = len(bounds_report["invalid_regions"]) * 10
            report["quality_score"] -= penalty
            report["issues"].append(
                f"{len(bounds_report['invalid_regions'])} regions with invalid coordinates"
            )

        # Regions with uncertainty or damage marks
        uncertain_regions = sum(1 for r in record.regions if r.uncertain)
        damaged_regions = sum(1 for r in record.regions if r.damaged)
        if uncertain_regions > 0:
            report["issues"].append(f"{uncertain_regions} uncertain region(s)")
        if damaged_regions > 0:
            report["issues"].append(f"{damaged_regions} damaged region(s)")

        report["quality_score"] = max(0, report["quality_score"])
        if report["quality_score"] < 50:
            report["quality_status"] = "fail"
        elif report["quality_score"] < 80:
            report["quality_status"] = "warning"
        else:
            report["quality_status"] = "pass"

        return report


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
