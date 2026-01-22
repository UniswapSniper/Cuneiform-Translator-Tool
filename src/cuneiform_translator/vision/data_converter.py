"""
Data converter for transforming tablet annotations into YOLO training format.

Converts annotated regions from TabletRecord format to YOLO v8 format:
- Images: Copied/extracted to training directory
- Annotations: Region coordinates → YOLO normalized bounding boxes
- Dataset split: Training/validation/test split with metadata
"""

import json
import logging
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from pydantic import BaseModel

from cuneiform_translator.io import DataPipeline, TabletRecord

logger = logging.getLogger(__name__)


class YOLOAnnotation(BaseModel):
    """Single YOLO annotation (one region/sign in image)."""

    class_id: int  # 0 for cuneiform sign (single class for now)
    x_center: float  # Normalized center X (0-1)
    y_center: float  # Normalized center Y (0-1)
    width: float  # Normalized width (0-1)
    height: float  # Normalized height (0-1)


class YOLODataset(BaseModel):
    """Metadata for YOLO dataset."""

    name: str
    total_images: int
    total_annotations: int
    train_images: int
    val_images: int
    test_images: int
    train_annotations: int
    val_annotations: int
    test_annotations: int
    class_count: dict  # Count per class


class TrainingDataConverter:
    """Convert tablet annotations to YOLO format."""

    def __init__(
        self,
        output_dir: Path = Path("data/yolo_dataset"),
        train_ratio: float = 0.7,
        val_ratio: float = 0.2,
        test_ratio: float = 0.1,
    ):
        """
        Initialize converter.

        Args:
            output_dir: Root directory for YOLO dataset
            train_ratio: Proportion of data for training
            val_ratio: Proportion of data for validation
            test_ratio: Proportion of data for testing
        """
        self.output_dir = Path(output_dir)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio

        # Create directory structure
        self.images_dir = self.output_dir / "images"
        self.labels_dir = self.output_dir / "labels"

        for split in ["train", "val", "test"]:
            (self.images_dir / split).mkdir(parents=True, exist_ok=True)
            (self.labels_dir / split).mkdir(parents=True, exist_ok=True)

    def extract_bounding_box(
        self, coordinates: list[list[float]]
    ) -> Tuple[float, float, float, float]:
        """
        Extract axis-aligned bounding box from region coordinates.

        Args:
            coordinates: List of [x, y] points

        Returns:
            (min_x, min_y, max_x, max_y)
        """
        if not coordinates:
            return 0, 0, 0, 0

        coords_array = np.array(coordinates)
        min_x = float(coords_array[:, 0].min())
        min_y = float(coords_array[:, 1].min())
        max_x = float(coords_array[:, 0].max())
        max_y = float(coords_array[:, 1].max())

        return min_x, min_y, max_x, max_y

    def normalize_bbox(
        self, bbox: Tuple[float, float, float, float], image_width: int, image_height: int
    ) -> Tuple[float, float, float, float]:
        """
        Convert absolute bounding box to YOLO format (normalized center + size).

        Args:
            bbox: (min_x, min_y, max_x, max_y)
            image_width: Image width in pixels
            image_height: Image height in pixels

        Returns:
            (x_center_norm, y_center_norm, width_norm, height_norm)
        """
        min_x, min_y, max_x, max_y = bbox

        # Clamp to image bounds
        min_x = max(0, min(min_x, image_width))
        max_x = max(0, min(max_x, image_width))
        min_y = max(0, min(min_y, image_height))
        max_y = max(0, min(max_y, image_height))

        # Calculate center and size
        x_center = (min_x + max_x) / 2.0
        y_center = (min_y + max_y) / 2.0
        width = max_x - min_x
        height = max_y - min_y

        # Normalize to 0-1
        x_center_norm = x_center / image_width
        y_center_norm = y_center / image_height
        width_norm = width / image_width
        height_norm = height / image_height

        return x_center_norm, y_center_norm, width_norm, height_norm

    def tablet_to_yolo(
        self, record: TabletRecord, image_path: Path, output_split: str = "train"
    ) -> Tuple[bool, Optional[str]]:
        """
        Convert single tablet to YOLO format.

        Args:
            record: TabletRecord with annotated regions
            image_path: Path to tablet image
            output_split: Train/val/test

        Returns:
            (success, error_message)
        """
        if not image_path.exists():
            return False, f"Image not found: {image_path}"

        # Read image to get dimensions
        img = cv2.imread(str(image_path))
        if img is None:
            return False, f"Cannot read image: {image_path}"

        img_height, img_width = img.shape[:2]

        # Output paths
        output_images_dir = self.images_dir / output_split
        output_labels_dir = self.labels_dir / output_split

        image_name = f"{record.tablet_id}.jpg"
        label_name = f"{record.tablet_id}.txt"

        output_image_path = output_images_dir / image_name
        output_label_path = output_labels_dir / label_name

        # Copy image
        try:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.imwrite(str(output_image_path), img_rgb)
        except Exception as e:
            return False, f"Failed to save image: {e}"

        # Generate annotations
        annotations = []
        for region in record.regions:
            # Skip empty regions
            if not region.coordinates or len(region.coordinates) < 3:
                logger.warning(f"Skipping invalid region {region.region_id}: insufficient coordinates")
                continue

            # Extract and normalize bounding box
            bbox = self.extract_bounding_box(region.coordinates)
            normalized = self.normalize_bbox(bbox, img_width, img_height)

            annotations.append(normalized)

        # Write YOLO annotation file
        with open(output_label_path, "w") as f:
            for x_center, y_center, width, height in annotations:
                # YOLO format: class_id x_center y_center width height (all normalized)
                f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        logger.info(
            f"Converted {record.tablet_id}: {len(annotations)} regions → {output_split}"
        )
        return True, None

    def convert_dataset(
        self,
        input_dir: Path,
        image_dir: Path = Path("data/raw/cdli"),
    ) -> dict:
        """
        Convert entire dataset from input directory.

        Args:
            input_dir: Directory containing annotated tablet JSON files
            image_dir: Directory containing tablet images

        Returns:
            Conversion summary with statistics
        """
        logger.info(f"Converting dataset from {input_dir}")

        tablet_files = sorted(input_dir.glob("*.json"))
        pipeline = DataPipeline()

        # Load all tablets
        tablets = []
        for tablet_file in tablet_files:
            record = pipeline.load_tablet_record(tablet_file)
            if record:
                tablets.append((record, tablet_file))

        logger.info(f"Loaded {len(tablets)} tablets")

        # Split dataset
        n_total = len(tablets)
        n_train = int(n_total * self.train_ratio)
        n_val = int(n_total * self.val_ratio)

        np.random.seed(42)  # Reproducible split
        indices = np.random.permutation(n_total)

        train_indices = set(indices[:n_train])
        val_indices = set(indices[n_train : n_train + n_val])
        test_indices = set(indices[n_train + n_val :])

        summary = {
            "total_tablets": n_total,
            "train_tablets": len(train_indices),
            "val_tablets": len(val_indices),
            "test_tablets": len(test_indices),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "conversion_errors": [],
            "total_annotations": 0,
            "regions_per_tablet": [],
        }

        # Convert tablets
        for idx, (record, tablet_file) in enumerate(tablets):
            # Determine split
            if idx in train_indices:
                split = "train"
            elif idx in val_indices:
                split = "val"
            else:
                split = "test"

            # Find image
            image_path = image_dir / f"{record.tablet_id}_l.jpg"
            if not image_path.exists():
                # Try alternative paths
                for candidate in (image_dir / record.tablet_id).glob("*.*"):
                    if candidate.is_file():
                        image_path = candidate
                        break

            if not image_path.exists():
                logger.warning(f"Image not found for {record.tablet_id}, skipping")
                summary["failed_conversions"] += 1
                summary["conversion_errors"].append(
                    {"tablet_id": record.tablet_id, "error": "Image not found"}
                )
                continue

            # Convert
            success, error = self.tablet_to_yolo(record, image_path, split)
            if success:
                summary["successful_conversions"] += 1
                summary["total_annotations"] += len(record.regions)
                summary["regions_per_tablet"].append(len(record.regions))
            else:
                summary["failed_conversions"] += 1
                summary["conversion_errors"].append(
                    {"tablet_id": record.tablet_id, "error": error}
                )

        # Calculate stats
        if summary["regions_per_tablet"]:
            summary["mean_regions_per_tablet"] = (
                sum(summary["regions_per_tablet"]) / len(summary["regions_per_tablet"])
            )
        else:
            summary["mean_regions_per_tablet"] = 0

        logger.info(f"Conversion complete: {summary['successful_conversions']} successful")
        logger.info(f"Total annotations: {summary['total_annotations']}")

        return summary

    def create_dataset_yaml(self, dataset_name: str = "cuneiform-signs"):
        """
        Create dataset.yaml file for YOLOv8.

        Args:
            dataset_name: Name of the dataset
        """
        yaml_content = f"""# {dataset_name} dataset
path: {self.output_dir.absolute()}
train: images/train
val: images/val
test: images/test

# Classes
nc: 1  # Number of classes
names: ['cuneiform_sign']  # Class names
"""

        yaml_path = self.output_dir / "dataset.yaml"
        with open(yaml_path, "w") as f:
            f.write(yaml_content)

        logger.info(f"Created dataset.yaml at {yaml_path}")
        return yaml_path


def main():
    """CLI for dataset conversion."""
    import argparse

    parser = argparse.ArgumentParser(description="Convert annotations to YOLO format")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Directory with annotated tablets (JSON)",
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path("data/raw/cdli"),
        help="Directory with tablet images",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/yolo_dataset"),
        help="Output directory for YOLO dataset",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.7,
        help="Training set ratio",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.2,
        help="Validation set ratio",
    )

    args = parser.parse_args()

    converter = TrainingDataConverter(
        output_dir=args.output,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
    )

    summary = converter.convert_dataset(args.input, args.image_dir)

    print("\n=== CONVERSION SUMMARY ===")
    print(f"Total tablets: {summary['total_tablets']}")
    print(f"Train: {summary['train_tablets']}, Val: {summary['val_tablets']}, Test: {summary['test_tablets']}")
    print(f"Successful: {summary['successful_conversions']}, Failed: {summary['failed_conversions']}")
    print(f"Total annotations: {summary['total_annotations']}")
    print(f"Mean regions per tablet: {summary['mean_regions_per_tablet']:.1f}")

    converter.create_dataset_yaml()
    print(f"\nDataset ready at: {args.output}")


if __name__ == "__main__":
    main()
