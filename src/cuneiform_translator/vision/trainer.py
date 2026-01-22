"""
YOLOv8 trainer for cuneiform sign detection.

Handles model training, validation, and evaluation metrics specific to
cuneiform sign detection task.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TrainingConfig(BaseModel):
    """Training configuration for YOLOv8."""

    model_name: str = "yolov8n"  # nano for quick iteration
    epochs: int = 50
    batch_size: int = 16
    imgsz: int = 640
    device: str = "cpu"  # or "cuda" for GPU
    patience: int = 20  # Early stopping patience
    save_period: int = 10
    workers: int = 4
    learning_rate: float = 0.001
    momentum: float = 0.937
    weight_decay: float = 0.0005
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.5


class TrainingMetrics(BaseModel):
    """Training metrics and results."""

    epoch: int
    train_loss: float
    val_loss: float
    precision: float
    recall: float
    map50: float  # mAP @ IoU=0.5
    map: float  # mAP @ IoU=0.5:0.95
    learning_rate: float


class YOLOTrainer:
    """Train YOLOv8 for sign detection."""

    def __init__(
        self,
        config: TrainingConfig = TrainingConfig(),
        output_dir: Path = Path("models/cuneiform_sign_detector"),
    ):
        """
        Initialize trainer.

        Args:
            config: Training configuration
            output_dir: Directory to save trained models
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Import ultralytics here (allows graceful degradation if not installed)
        try:
            from ultralytics import YOLO

            self.YOLO = YOLO
        except ImportError:
            logger.error("ultralytics not installed. Install with: pip install ultralytics")
            self.YOLO = None

        self.model = None
        self.training_history = []

    def initialize_model(self):
        """Load YOLOv8 model."""
        if not self.YOLO:
            logger.error("YOLOv8 not available")
            return False

        try:
            model_path = f"{self.config.model_name}.pt"
            self.model = self.YOLO(model_path)
            logger.info(f"Loaded {self.config.model_name} model")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def train(self, dataset_yaml: Path) -> Optional[Path]:
        """
        Train YOLOv8 on cuneiform dataset.

        Args:
            dataset_yaml: Path to dataset.yaml (from TrainingDataConverter)

        Returns:
            Path to best model weights
        """
        if not self.model:
            if not self.initialize_model():
                return None

        logger.info(f"Starting training with config: {self.config}")

        try:
            results = self.model.train(
                data=str(dataset_yaml),
                epochs=self.config.epochs,
                batch=self.config.batch_size,
                imgsz=self.config.imgsz,
                device=self.config.device,
                patience=self.config.patience,
                save_period=self.config.save_period,
                workers=self.config.workers,
                lr0=self.config.learning_rate,
                momentum=self.config.momentum,
                weight_decay=self.config.weight_decay,
                project=str(self.output_dir),
                name="train",
                exist_ok=True,
                verbose=True,
            )

            best_model_path = self.output_dir / "train" / "weights" / "best.pt"
            logger.info(f"Training complete. Best model: {best_model_path}")

            return best_model_path if best_model_path.exists() else None

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return None

    def evaluate(self, model_path: Path, dataset_yaml: Path) -> dict:
        """
        Evaluate trained model.

        Args:
            model_path: Path to trained model weights
            dataset_yaml: Path to dataset.yaml

        Returns:
            Evaluation metrics
        """
        if not self.YOLO:
            return {}

        try:
            model = self.YOLO(str(model_path))
            results = model.val(
                data=str(dataset_yaml),
                batch=self.config.batch_size,
                imgsz=self.config.imgsz,
                device=self.config.device,
            )

            metrics = {
                "precision": float(results.results_dict.get("metrics/precision(B)", 0)),
                "recall": float(results.results_dict.get("metrics/recall(B)", 0)),
                "map50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
                "map": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
            }

            logger.info(f"Evaluation results: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {}

    def predict(
        self,
        model_path: Path,
        image_path: Path,
        conf_threshold: Optional[float] = None,
    ) -> list:
        """
        Predict signs in an image.

        Args:
            model_path: Path to trained model weights
            image_path: Path to image
            conf_threshold: Confidence threshold override

        Returns:
            List of detections (boxes, confidence, class)
        """
        if not self.YOLO:
            return []

        try:
            model = self.YOLO(str(model_path))
            conf = conf_threshold or self.config.confidence_threshold

            results = model.predict(
                source=str(image_path),
                conf=conf,
                iou=self.config.iou_threshold,
                device=self.config.device,
            )

            detections = []
            for result in results:
                if result.boxes:
                    for box in result.boxes:
                        detection = {
                            "bbox": box.xyxy.cpu().numpy()[0].tolist(),
                            "confidence": float(box.conf.cpu().numpy()[0]),
                            "class": int(box.cls.cpu().numpy()[0]),
                        }
                        detections.append(detection)

            logger.info(f"Found {len(detections)} signs in {image_path.name}")
            return detections

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return []

    def predict_batch(
        self,
        model_path: Path,
        image_dir: Path,
        conf_threshold: Optional[float] = None,
    ) -> dict:
        """
        Predict on batch of images.

        Args:
            model_path: Path to trained model
            image_dir: Directory with images
            conf_threshold: Confidence threshold override

        Returns:
            Dict mapping image path to detections
        """
        if not self.YOLO:
            return {}

        results = {}
        image_files = sorted(image_dir.glob("*.jpg")) + sorted(image_dir.glob("*.png"))

        logger.info(f"Processing {len(image_files)} images")

        for image_path in image_files:
            detections = self.predict(model_path, image_path, conf_threshold)
            results[image_path.name] = detections

        return results


def main():
    """CLI for model training and prediction."""
    import argparse

    parser = argparse.ArgumentParser(description="YOLOv8 trainer for cuneiform signs")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Training command
    train_parser = subparsers.add_parser("train", help="Train model")
    train_parser.add_argument(
        "--dataset-yaml",
        type=Path,
        required=True,
        help="Path to dataset.yaml (from data_converter)",
    )
    train_parser.add_argument(
        "--model",
        type=str,
        default="yolov8n",
        help="YOLOv8 model size (n/s/m/l/x)",
    )
    train_parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Number of epochs",
    )
    train_parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size",
    )
    train_parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Device (cpu/cuda/mps)",
    )
    train_parser.add_argument(
        "--output",
        type=Path,
        default=Path("models/cuneiform_sign_detector"),
        help="Output directory",
    )

    # Prediction command
    predict_parser = subparsers.add_parser("predict", help="Predict on image(s)")
    predict_parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Path to trained model weights",
    )
    predict_parser.add_argument(
        "--image",
        type=Path,
        help="Single image file",
    )
    predict_parser.add_argument(
        "--batch",
        type=Path,
        help="Directory with images",
    )
    predict_parser.add_argument(
        "--conf",
        type=float,
        default=0.5,
        help="Confidence threshold",
    )

    # Evaluation command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate model")
    eval_parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Path to trained model weights",
    )
    eval_parser.add_argument(
        "--dataset-yaml",
        type=Path,
        required=True,
        help="Path to dataset.yaml",
    )
    eval_parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Device (cpu/cuda/mps)",
    )

    args = parser.parse_args()

    config = TrainingConfig(
        model_name=getattr(args, "model", "yolov8n"),
        epochs=getattr(args, "epochs", 50),
        batch_size=getattr(args, "batch_size", 16),
        device=getattr(args, "device", "cpu"),
    )

    trainer = YOLOTrainer(config, getattr(args, "output", Path("models")))

    if args.command == "train":
        best_model = trainer.train(args.dataset_yaml)
        if best_model:
            print(f"✓ Training complete: {best_model}")

    elif args.command == "predict":
        if args.image:
            detections = trainer.predict(args.model, args.image, args.conf)
            print(f"Found {len(detections)} signs:")
            for det in detections:
                print(f"  - Box: {det['bbox']}, Conf: {det['confidence']:.3f}")

        elif args.batch:
            results = trainer.predict_batch(args.model, args.batch, args.conf)
            total = sum(len(v) for v in results.values())
            print(f"Found {total} total signs in {len(results)} images")

    elif args.command == "evaluate":
        config.device = args.device
        trainer = YOLOTrainer(config)
        metrics = trainer.evaluate(args.model, args.dataset_yaml)
        print("\n=== EVALUATION RESULTS ===")
        for key, value in metrics.items():
            print(f"{key}: {value:.4f}")


if __name__ == "__main__":
    main()
