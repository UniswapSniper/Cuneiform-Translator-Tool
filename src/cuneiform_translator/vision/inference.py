"""
Inference pipeline for cuneiform sign detection.

Provides high-level API for detecting signs in tablets and generating
annotated outputs.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DetectedSign(BaseModel):
    """A detected cuneiform sign."""

    sign_id: str
    bbox: list[float]  # [x_min, y_min, x_max, y_max]
    confidence: float
    center_x: float
    center_y: float
    width: float
    height: float


class PredictionResult(BaseModel):
    """Results from predicting signs on a tablet."""

    tablet_id: str
    image_path: str
    num_detections: int
    detections: list[DetectedSign]
    inference_time: float  # milliseconds
    mean_confidence: float


class SignDetector:
    """High-level API for sign detection."""

    def __init__(self, model_path: Path):
        """
        Initialize detector with trained model.

        Args:
            model_path: Path to trained YOLOv8 weights
        """
        self.model_path = Path(model_path)

        try:
            from ultralytics import YOLO

            self.model = YOLO(str(model_path))
            logger.info(f"Loaded model from {model_path}")
        except ImportError:
            logger.error("ultralytics not installed")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None

    def detect(
        self,
        image_path: Path,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.5,
    ) -> Optional[PredictionResult]:
        """
        Detect signs in a single image.

        Args:
            image_path: Path to tablet image
            conf_threshold: Minimum confidence
            iou_threshold: NMS IoU threshold

        Returns:
            PredictionResult with detections
        """
        if not self.model:
            logger.error("Model not available")
            return None

        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            return None

        try:
            import time

            start_time = time.time()

            results = self.model.predict(
                source=str(image_path),
                conf=conf_threshold,
                iou=iou_threshold,
                verbose=False,
            )

            inference_time = (time.time() - start_time) * 1000  # milliseconds

            detections = []
            confidences = []

            for result in results:
                if result.boxes is not None:
                    for i, box in enumerate(result.boxes):
                        xyxy = box.xyxy.cpu().numpy()[0]
                        conf = float(box.conf.cpu().numpy()[0])

                        x_min, y_min, x_max, y_max = xyxy
                        center_x = (x_min + x_max) / 2
                        center_y = (y_min + y_max) / 2
                        width = x_max - x_min
                        height = y_max - y_min

                        detection = DetectedSign(
                            sign_id=f"{image_path.stem}_sign_{i:04d}",
                            bbox=xyxy.tolist(),
                            confidence=conf,
                            center_x=center_x,
                            center_y=center_y,
                            width=width,
                            height=height,
                        )

                        detections.append(detection)
                        confidences.append(conf)

            mean_conf = np.mean(confidences) if confidences else 0.0

            result = PredictionResult(
                tablet_id=image_path.stem,
                image_path=str(image_path),
                num_detections=len(detections),
                detections=detections,
                inference_time=inference_time,
                mean_confidence=float(mean_conf),
            )

            logger.info(
                f"Detected {len(detections)} signs in {image_path.name} "
                f"({inference_time:.1f}ms, conf={mean_conf:.3f})"
            )

            return result

        except Exception as e:
            logger.error(f"Detection failed for {image_path}: {e}")
            return None

    def detect_batch(
        self,
        image_dir: Path,
        conf_threshold: float = 0.5,
        output_dir: Optional[Path] = None,
    ) -> dict:
        """
        Detect signs in multiple images.

        Args:
            image_dir: Directory with images
            conf_threshold: Minimum confidence
            output_dir: Optional directory to save annotated images

        Returns:
            Dict mapping image path to PredictionResult
        """
        image_files = sorted(image_dir.glob("*.jpg")) + sorted(image_dir.glob("*.png"))

        results = {}
        total_signs = 0

        logger.info(f"Processing {len(image_files)} images")

        for image_path in image_files:
            result = self.detect(image_path, conf_threshold)
            if result:
                results[image_path.name] = result
                total_signs += result.num_detections

                # Save annotated image if output dir specified
                if output_dir:
                    self._save_annotated_image(image_path, result, output_dir)

        logger.info(f"Detected {total_signs} total signs")

        return results

    def _save_annotated_image(
        self,
        image_path: Path,
        result: PredictionResult,
        output_dir: Path,
    ):
        """Save image with bounding boxes drawn."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            img = cv2.imread(str(image_path))
            if img is None:
                return

            # Draw bounding boxes
            for detection in result.detections:
                x_min, y_min, x_max, y_max = (
                    int(detection.bbox[0]),
                    int(detection.bbox[1]),
                    int(detection.bbox[2]),
                    int(detection.bbox[3]),
                )

                # Green box for detection
                cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                # Confidence label
                label = f"{detection.confidence:.2f}"
                cv2.putText(
                    img,
                    label,
                    (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

            output_path = output_dir / image_path.name
            cv2.imwrite(str(output_path), img)
            logger.debug(f"Saved annotated image: {output_path}")

        except Exception as e:
            logger.error(f"Failed to save annotated image: {e}")

    def export_predictions(
        self,
        results: dict,
        output_path: Path,
        format: str = "json",
    ):
        """
        Export predictions to file.

        Args:
            results: Dict mapping image paths to PredictionResult
            output_path: Output file path
            format: Export format (json, jsonl, csv)
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            data = {
                img_name: {
                    "tablet_id": result.tablet_id,
                    "num_detections": result.num_detections,
                    "mean_confidence": result.mean_confidence,
                    "inference_time": result.inference_time,
                    "detections": [det.model_dump() for det in result.detections],
                }
                for img_name, result in results.items()
            }
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

        elif format == "jsonl":
            with open(output_path, "w") as f:
                for img_name, result in results.items():
                    record = {
                        "image": img_name,
                        "tablet_id": result.tablet_id,
                        "num_detections": result.num_detections,
                        "detections": [det.model_dump() for det in result.detections],
                    }
                    f.write(json.dumps(record) + "\n")

        elif format == "csv":
            import csv

            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "image",
                        "tablet_id",
                        "sign_id",
                        "confidence",
                        "x_min",
                        "y_min",
                        "x_max",
                        "y_max",
                    ]
                )

                for img_name, result in results.items():
                    for detection in result.detections:
                        writer.writerow(
                            [
                                img_name,
                                result.tablet_id,
                                detection.sign_id,
                                detection.confidence,
                                detection.bbox[0],
                                detection.bbox[1],
                                detection.bbox[2],
                                detection.bbox[3],
                            ]
                        )

        logger.info(f"Exported predictions to {output_path}")


def main():
    """CLI for inference."""
    import argparse

    parser = argparse.ArgumentParser(description="Sign detection inference")
    parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Path to trained model weights",
    )
    parser.add_argument(
        "--image",
        type=Path,
        help="Single image file",
    )
    parser.add_argument(
        "--batch",
        type=Path,
        help="Directory with images",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.5,
        help="Confidence threshold",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for annotated images",
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Export predictions to file (json/jsonl/csv)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="json",
        choices=["json", "jsonl", "csv"],
        help="Export format",
    )

    args = parser.parse_args()

    detector = SignDetector(args.model)

    if args.image:
        result = detector.detect(args.image, args.conf)
        if result:
            print(f"Found {result.num_detections} signs")
            print(f"Inference time: {result.inference_time:.1f}ms")
            print(f"Mean confidence: {result.mean_confidence:.3f}")

            if args.output:
                detector._save_annotated_image(args.image, result, args.output)

    elif args.batch:
        results = detector.detect_batch(args.batch, args.conf, args.output)

        total_signs = sum(r.num_detections for r in results.values())
        mean_time = np.mean([r.inference_time for r in results.values()])

        print(f"\n=== BATCH DETECTION RESULTS ===")
        print(f"Images processed: {len(results)}")
        print(f"Total signs detected: {total_signs}")
        print(f"Mean inference time: {mean_time:.1f}ms")

        if args.export:
            detector.export_predictions(results, args.export, args.format)


if __name__ == "__main__":
    main()
