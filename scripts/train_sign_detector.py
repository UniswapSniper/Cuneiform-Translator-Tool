#!/usr/bin/env python3
"""
End-to-end training pipeline for YOLOv8 cuneiform sign detector.

This script orchestrates:
1. Converting annotated tablets to YOLO format
2. Creating dataset splits and YAML config
3. Training YOLOv8 model
4. Evaluating trained model
"""

import argparse
import json
import logging
from pathlib import Path

from cuneiform_translator.vision import (
    TrainingConfig,
    TrainingDataConverter,
    YOLOTrainer,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main training pipeline."""
    parser = argparse.ArgumentParser(description="Train YOLOv8 cuneiform sign detector")

    parser.add_argument(
        "--annotations",
        type=Path,
        default=Path("data/processed"),
        help="Directory with annotated tablets (JSON)",
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=Path("data/raw/cdli"),
        help="Directory with tablet images",
    )
    parser.add_argument(
        "--dataset-output",
        type=Path,
        default=Path("data/yolo_dataset"),
        help="Output directory for YOLO dataset",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n",
        help="YOLOv8 model size (n/s/m/l/x)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Training device (cpu/cuda/mps)",
    )
    parser.add_argument(
        "--models-output",
        type=Path,
        default=Path("models/cuneiform_sign_detector"),
        help="Directory to save trained models",
    )
    parser.add_argument(
        "--skip-conversion",
        action="store_true",
        help="Skip dataset conversion (reuse existing)",
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip training (only evaluate)",
    )

    args = parser.parse_args()

    logger.info("=== CUNEIFORM SIGN DETECTOR TRAINING PIPELINE ===\n")

    # Step 1: Convert dataset
    if not args.skip_conversion:
        logger.info("Step 1: Converting annotations to YOLO format...")
        converter = TrainingDataConverter(
            output_dir=args.dataset_output,
            train_ratio=0.7,
            val_ratio=0.2,
            test_ratio=0.1,
        )

        summary = converter.convert_dataset(args.annotations, args.images)

        logger.info(f"  Total tablets: {summary['total_tablets']}")
        logger.info(f"  Train: {summary['train_tablets']}, Val: {summary['val_tablets']}, Test: {summary['test_tablets']}")
        logger.info(f"  Successful: {summary['successful_conversions']}, Failed: {summary['failed_conversions']}")
        logger.info(f"  Total annotations: {summary['total_annotations']}")
        logger.info(f"  Mean regions per tablet: {summary['mean_regions_per_tablet']:.1f}\n")

        if summary["successful_conversions"] == 0:
            logger.error("No successful conversions. Check image paths and annotations.")
            return

        converter.create_dataset_yaml("cuneiform-signs")
    else:
        logger.info("Step 1: Skipping dataset conversion (reusing existing)\n")

    # Step 2: Train model
    if not args.skip_training:
        logger.info("Step 2: Training YOLOv8 model...")
        config = TrainingConfig(
            model_name=args.model,
            epochs=args.epochs,
            batch_size=args.batch_size,
            device=args.device,
        )

        trainer = YOLOTrainer(config, args.models_output)

        dataset_yaml = args.dataset_output / "dataset.yaml"
        if not dataset_yaml.exists():
            logger.error(f"Dataset YAML not found: {dataset_yaml}")
            return

        best_model = trainer.train(dataset_yaml)

        if not best_model:
            logger.error("Training failed")
            return

        logger.info(f"  Best model saved: {best_model}\n")
    else:
        logger.info("Step 2: Skipping training\n")
        # Find best model
        best_model = args.models_output / "train" / "weights" / "best.pt"
        if not best_model.exists():
            logger.error("No trained model found. Run without --skip-training first.")
            return

    # Step 3: Evaluate model
    logger.info("Step 3: Evaluating trained model...")
    config = TrainingConfig(device=args.device)
    trainer = YOLOTrainer(config, args.models_output)

    dataset_yaml = args.dataset_output / "dataset.yaml"
    metrics = trainer.evaluate(best_model, dataset_yaml)

    logger.info("  Evaluation Results:")
    for key, value in metrics.items():
        logger.info(f"    {key}: {value:.4f}")

    # Save summary
    summary_data = {
        "model_path": str(best_model),
        "config": config.model_dump(),
        "metrics": metrics,
        "dataset": {
            "annotations_dir": str(args.annotations),
            "images_dir": str(args.images),
            "yolo_dataset_dir": str(args.dataset_output),
        },
    }

    summary_path = args.models_output / "training_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    logger.info(f"\n=== TRAINING COMPLETE ===")
    logger.info(f"Summary saved to: {summary_path}")
    logger.info(f"Model available at: {best_model}")


if __name__ == "__main__":
    main()
