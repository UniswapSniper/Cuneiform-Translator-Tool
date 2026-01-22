#!/usr/bin/env python3
"""
Step 4: 3D-Enhanced YOLOv8 Training Pipeline

Orchestrates the complete 3D augmentation workflow:
1. Load 3D models (PLY format)
2. Generate depth maps and augmentations
3. Train YOLOv8 with augmented data
4. Compare performance vs baseline
5. Visualize results
"""

import argparse
import json
import logging
from pathlib import Path

from cuneiform_translator.vision import (
    AugmentationConfig,
    Enhanced3DTrainer,
    TrainingConfig,
    YOLOTrainer,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main 3D training pipeline."""
    parser = argparse.ArgumentParser(
        description="3D-Enhanced YOLOv8 Sign Detector Training"
    )

    # Data inputs
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
        "--ply-dir",
        type=Path,
        help="Directory with PLY 3D models (optional)",
    )

    # Output directories
    parser.add_argument(
        "--dataset-output",
        type=Path,
        default=Path("data/yolo_dataset"),
        help="Output directory for YOLO dataset",
    )
    parser.add_argument(
        "--augmented-output",
        type=Path,
        default=Path("data/yolo_dataset_augmented"),
        help="Output directory for augmented dataset",
    )
    parser.add_argument(
        "--models-output",
        type=Path,
        default=Path("models/cuneiform_3d"),
        help="Directory to save trained models",
    )

    # Training parameters
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

    # Augmentation parameters
    parser.add_argument(
        "--enable-augmentation",
        action="store_true",
        default=True,
        help="Enable 3D augmentation",
    )
    parser.add_argument(
        "--augmentation-variations",
        type=int,
        default=3,
        help="Number of augmentation variations per image",
    )
    parser.add_argument(
        "--depth-resolution",
        type=int,
        default=640,
        help="Depth map resolution",
    )

    # Pipeline options
    parser.add_argument(
        "--skip-conversion",
        action="store_true",
        help="Skip YOLO dataset conversion",
    )
    parser.add_argument(
        "--skip-augmentation",
        action="store_true",
        help="Skip 3D augmentation",
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip model training",
    )
    parser.add_argument(
        "--train-baseline",
        action="store_true",
        help="Also train baseline (non-augmented) model",
    )

    args = parser.parse_args()

    logger.info("=== STEP 4: 3D-ENHANCED YOLOV8 TRAINING ===\n")

    # Step 1: Convert base dataset
    if not args.skip_conversion:
        logger.info("Step 1: Converting annotations to YOLO format...")

        from cuneiform_translator.vision import TrainingDataConverter

        converter = TrainingDataConverter(
            output_dir=args.dataset_output,
            train_ratio=0.7,
            val_ratio=0.2,
            test_ratio=0.1,
        )

        summary = converter.convert_dataset(args.annotations, args.images)

        logger.info(f"  Total tablets: {summary['total_tablets']}")
        logger.info(f"  Successful conversions: {summary['successful_conversions']}")

        converter.create_dataset_yaml("cuneiform-signs")

        if summary["successful_conversions"] == 0:
            logger.error("No successful conversions. Exiting.")
            return

    else:
        logger.info("Step 1: Skipping dataset conversion (reusing existing)\n")

    # Step 2: 3D Augmentation
    if not args.skip_augmentation and args.ply_dir:
        logger.info("Step 2: Creating 3D-augmented training dataset...")

        from cuneiform_translator.vision.trainer_3d import create_augmented_yolo_dataset

        augmented_dir = create_augmented_yolo_dataset(
            args.dataset_output,
            args.images,
            args.ply_dir,
            args.augmented_output,
            augmentation_ratio=0.5,
        )

        logger.info(f"  Augmented dataset ready at {augmented_dir}\n")
        dataset_yaml_for_training = augmented_dir / "dataset.yaml"
    else:
        logger.info("Step 2: Skipping 3D augmentation\n")
        dataset_yaml_for_training = args.dataset_output / "dataset.yaml"

    # Step 3a: Train baseline (optional)
    if args.train_baseline and not args.skip_training:
        logger.info("Step 3a: Training baseline model (without 3D augmentation)...")

        config = TrainingConfig(
            model_name=args.model,
            epochs=args.epochs,
            batch_size=args.batch_size,
            device=args.device,
        )

        baseline_output = args.models_output / "baseline"
        trainer = YOLOTrainer(config, baseline_output)

        baseline_dataset = args.dataset_output / "dataset.yaml"
        if baseline_dataset.exists():
            baseline_model = trainer.train(baseline_dataset)
            logger.info(f"  Baseline model: {baseline_model}\n")

    # Step 3b: Train with 3D augmentation
    if not args.skip_training:
        logger.info("Step 3b: Training 3D-enhanced model...")

        aug_config = AugmentationConfig(
            enable_3d_augmentation=args.enable_augmentation and args.ply_dir is not None,
            depth_variation_count=args.augmentation_variations,
            depth_resolution=args.depth_resolution,
        )

        train_config = TrainingConfig(
            model_name=args.model,
            epochs=args.epochs,
            batch_size=args.batch_size,
            device=args.device,
        )

        trainer = Enhanced3DTrainer(train_config, aug_config, args.models_output)

        best_model = trainer.train_with_augmentation(
            dataset_yaml_for_training,
            args.images,
            args.ply_dir if args.ply_dir else Path("data/raw/3d_models"),
        )

        if not best_model:
            logger.error("Training failed")
            return

        logger.info(f"  3D-Enhanced model: {best_model}\n")
    else:
        logger.info("Step 3b: Skipping training\n")
        best_model = args.models_output / "train" / "weights" / "best.pt"

    # Step 4: Evaluation with 3D analysis
    if not args.skip_training and args.ply_dir:
        logger.info("Step 4: Evaluating with 3D model analysis...")

        train_config = TrainingConfig(device=args.device)
        aug_config = AugmentationConfig()
        trainer = Enhanced3DTrainer(train_config, aug_config, args.models_output)

        metrics = trainer.evaluate_with_3d_analysis(
            best_model,
            dataset_yaml_for_training,
            args.images,
            args.ply_dir,
        )

        logger.info("  Evaluation Results:")
        for key, value in metrics.items():
            if key != "3d_analysis":
                logger.info(f"    {key}: {value:.4f}")

        if "3d_analysis" in metrics:
            logger.info("  3D Model Analysis:")
            for key, value in metrics["3d_analysis"].items():
                logger.info(f"    {key}: {value}")

        logger.info()

    # Summary
    logger.info("=== TRAINING COMPLETE ===")
    logger.info(f"Models saved to: {args.models_output}")

    # Save configuration
    config_summary = {
        "dataset": str(args.dataset_output),
        "augmented_dataset": str(args.augmented_output) if args.ply_dir else None,
        "ply_directory": str(args.ply_dir) if args.ply_dir else None,
        "training_config": {
            "model": args.model,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "device": args.device,
        },
        "augmentation_config": {
            "enabled": args.enable_augmentation and args.ply_dir is not None,
            "variations": args.augmentation_variations,
            "depth_resolution": args.depth_resolution,
        },
        "options": {
            "train_baseline": args.train_baseline,
            "skip_conversion": args.skip_conversion,
            "skip_augmentation": args.skip_augmentation,
            "skip_training": args.skip_training,
        },
    }

    config_path = args.models_output / "step4_config.json"
    with open(config_path, "w") as f:
        json.dump(config_summary, f, indent=2)

    logger.info(f"Configuration saved to: {config_path}")


if __name__ == "__main__":
    main()
