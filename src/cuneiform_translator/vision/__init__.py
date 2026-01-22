"""Vision pipeline: image preprocessing, segmentation, region detection."""

from .data_converter import TrainingDataConverter
from .inference import DetectedSign, PredictionResult, SignDetector
from .model_3d import DepthAugmentationPipeline, PLYModel
from .renderer_3d import TabletRenderer
from .trainer import TrainingConfig, YOLOTrainer
from .trainer_3d import AugmentationConfig, Enhanced3DTrainer

__all__ = [
    "TrainingDataConverter",
    "YOLOTrainer",
    "Enhanced3DTrainer",
    "TrainingConfig",
    "AugmentationConfig",
    "SignDetector",
    "PredictionResult",
    "DetectedSign",
    "PLYModel",
    "DepthAugmentationPipeline",
    "TabletRenderer",
]

