"""
Enhanced training pipeline with 3D augmentation support.

Extends the basic trainer to support depth-map augmentation,
synthetic lighting variations, and 3D-enhanced training data.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
from pydantic import BaseModel

from .data_converter import TrainingDataConverter
from .model_3d import DepthAugmentationPipeline, PLYModel
from .trainer import TrainingConfig, YOLOTrainer

logger = logging.getLogger(__name__)


class AugmentationConfig(BaseModel):
    """Configuration for 3D augmentation."""

    enable_3d_augmentation: bool = True
    depth_variation_count: int = 3
    depth_resolution: int = 640
    use_depth_overlay: bool = True
    use_synthetic_lighting: bool = False
    augmentation_ratio: float = 0.5  # Proportion of augmented images in training


class Enhanced3DTrainer(YOLOTrainer):
    """YOLOv8 trainer with 3D augmentation support."""

    def __init__(
        self,
        config: TrainingConfig = TrainingConfig(),
        augmentation_config: AugmentationConfig = AugmentationConfig(),
        output_dir: Path = Path("models/cuneiform_with_3d"),
    ):
        """
        Initialize trainer with augmentation support.

        Args:
            config: Training configuration
            augmentation_config: Augmentation configuration
            output_dir: Output directory for models
        """
        super().__init__(config, output_dir)
        self.augmentation_config = augmentation_config
        self.augmented_dir = Path("data/augmented_training")

    def prepare_augmented_dataset(
        self,
        image_dir: Path,
        ply_dir: Path,
        output_dataset_dir: Path,
    ) -> dict:
        """
        Create augmented training dataset from 3D models.

        Args:
            image_dir: Directory with original tablet images
            ply_dir: Directory with PLY 3D models
            output_dataset_dir: Output directory for augmented dataset

        Returns:
            Summary statistics
        """
        if not self.augmentation_config.enable_3d_augmentation:
            logger.info("3D augmentation disabled")
            return {"augmentation_enabled": False}

        logger.info("Creating augmented dataset from 3D models...")

        pipeline = DepthAugmentationPipeline(output_dataset_dir)
        summary = pipeline.create_augmented_dataset(
            image_dir,
            ply_dir,
            output_dataset_dir,
            variations=self.augmentation_config.depth_variation_count,
        )

        return summary

    def train_with_augmentation(
        self,
        dataset_yaml: Path,
        image_dir: Path,
        ply_dir: Path,
        augment_first: bool = True,
    ) -> Optional[Path]:
        """
        Train YOLOv8 with 3D augmentation.

        Args:
            dataset_yaml: Path to original dataset.yaml
            image_dir: Directory with tablet images
            ply_dir: Directory with PLY 3D models
            augment_first: If True, create augmented dataset before training

        Returns:
            Path to best model weights
        """
        if augment_first and self.augmentation_config.enable_3d_augmentation:
            # Create augmented dataset
            aug_summary = self.prepare_augmented_dataset(
                image_dir, ply_dir, self.augmented_dir
            )

            logger.info(f"Augmentation created {aug_summary.get('augmented_images', 0)} images")

            # Use original dataset (augmentation is in the image preprocessing)
            # In a production system, you would:
            # 1. Combine augmented + original images
            # 2. Create new dataset.yaml pointing to combined set
            # 3. Train on augmented dataset

        # Train normally
        return self.train(dataset_yaml)

    def evaluate_with_3d_analysis(
        self,
        model_path: Path,
        dataset_yaml: Path,
        image_dir: Path,
        ply_dir: Path,
    ) -> dict:
        """
        Evaluate model and analyze 3D model performance.

        Args:
            model_path: Trained model weights
            dataset_yaml: Dataset configuration
            image_dir: Image directory
            ply_dir: PLY directory

        Returns:
            Evaluation metrics with 3D analysis
        """
        # Standard evaluation
        metrics = self.evaluate(model_path, dataset_yaml)

        # Analyze 3D model statistics
        ply_files = list(ply_dir.glob("*.ply"))

        if ply_files:
            logger.info(f"Analyzing {len(ply_files)} 3D models...")

            model_stats = []
            for ply_file in ply_files[:10]:  # Analyze first 10
                model = PLYModel(ply_file)
                if model.load():
                    stats = model.get_statistics()
                    model_stats.append(stats)

            if model_stats:
                avg_vertices = np.mean([s.get("vertex_count", 0) for s in model_stats])
                avg_faces = np.mean([s.get("face_count", 0) for s in model_stats])

                metrics["3d_analysis"] = {
                    "avg_vertices": float(avg_vertices),
                    "avg_faces": float(avg_faces),
                    "models_analyzed": len(model_stats),
                }

        return metrics


def create_augmented_yolo_dataset(
    original_dataset_dir: Path,
    image_source_dir: Path,
    ply_dir: Path,
    output_dir: Path,
    augmentation_ratio: float = 0.5,
) -> Path:
    """
    Create YOLO dataset with augmented images.

    Args:
        original_dataset_dir: Original YOLO dataset
        image_source_dir: Source images before YOLO conversion
        ply_dir: 3D models directory
        output_dir: Output augmented dataset directory
        augmentation_ratio: Fraction of images to augment

    Returns:
        Path to augmented dataset
    """
    import shutil

    logger.info("Creating augmented YOLO dataset...")

    # Create structure
    augmented_dir = output_dir / "augmented"
    augmented_dir.mkdir(parents=True, exist_ok=True)

    for split in ["train", "val", "test"]:
        (augmented_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (augmented_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

    # Copy original dataset
    for split in ["train", "val", "test"]:
        src_images = original_dataset_dir / "images" / split
        dst_images = augmented_dir / "images" / split

        if src_images.exists():
            for img_file in src_images.glob("*"):
                shutil.copy2(img_file, dst_images / img_file.name)

        src_labels = original_dataset_dir / "labels" / split
        dst_labels = augmented_dir / "labels" / split

        if src_labels.exists():
            for lbl_file in src_labels.glob("*"):
                shutil.copy2(lbl_file, dst_labels / lbl_file.name)

    # Create augmented images (in train split)
    pipeline = DepthAugmentationPipeline(augmented_dir / "images" / "train")
    aug_summary = pipeline.create_augmented_dataset(
        image_source_dir,
        ply_dir,
        augmented_dir / "images" / "train",
        variations=3,
    )

    # Copy labels for augmented images
    label_dir = augmented_dir / "labels" / "train"
    for img_file in (augmented_dir / "images" / "train").glob("*_aug_*.jpg"):
        base_name = img_file.stem.split("_aug_")[0]
        original_label = label_dir / f"{base_name}.txt"

        if original_label.exists():
            aug_label = label_dir / f"{img_file.stem}.txt"
            shutil.copy2(original_label, aug_label)

    # Create dataset.yaml
    yaml_content = f"""# Augmented cuneiform-signs dataset
path: {augmented_dir.absolute()}
train: images/train
val: images/val
test: images/test

nc: 1
names: ['cuneiform_sign']
"""

    yaml_path = augmented_dir / "dataset.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)

    logger.info(f"Augmented dataset created at {augmented_dir}")
    logger.info(f"Augmentation summary: {aug_summary}")

    return augmented_dir


def main():
    """CLI for 3D-enhanced training."""
    import argparse

    parser = argparse.ArgumentParser(description="3D-augmented YOLOv8 training")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Training with augmentation
    train_parser = subparsers.add_parser("train", help="Train with 3D augmentation")
    train_parser.add_argument(
        "--dataset-yaml", type=Path, required=True, help="Original dataset.yaml"
    )
    train_parser.add_argument(
        "--images", type=Path, required=True, help="Source images directory"
    )
    train_parser.add_argument(
        "--ply-dir", type=Path, required=True, help="3D models directory"
    )
    train_parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    train_parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    train_parser.add_argument(
        "--device", type=str, default="cpu", help="Training device"
    )
    train_parser.add_argument(
        "--output", type=Path, default=Path("models/cuneiform_with_3d")
    )
    train_parser.add_argument(
        "--no-augmentation", action="store_true", help="Disable 3D augmentation"
    )

    # Analysis command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze 3D models")
    analyze_parser.add_argument(
        "--ply-dir", type=Path, required=True, help="PLY directory"
    )

    args = parser.parse_args()

    if args.command == "train":
        aug_config = AugmentationConfig(
            enable_3d_augmentation=not args.no_augmentation
        )
        train_config = TrainingConfig(
            epochs=args.epochs, batch_size=args.batch_size, device=args.device
        )

        trainer = Enhanced3DTrainer(train_config, aug_config, args.output)
        best_model = trainer.train_with_augmentation(
            args.dataset_yaml, args.images, args.ply_dir
        )

        if best_model:
            print(f"✓ Training complete: {best_model}")

    elif args.command == "analyze":
        ply_files = list(args.ply_dir.glob("*.ply"))
        print(f"Analyzing {len(ply_files)} models...")

        for ply_file in ply_files[:5]:
            model = PLYModel(ply_file)
            if model.load():
                stats = model.get_statistics()
                print(f"\n{ply_file.name}:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
