#!/usr/bin/env python3
"""
Complete Cuneiform Translator Pipeline Orchestration

Unified entry point for the entire workflow:
1. Download tablet data from CDLI
2. Annotate tablets (interactive mode)
3. Validate data quality
4. Train YOLOv8 model with optional 3D augmentation
5. Evaluate and generate reports

Usage:
    # Full pipeline with 3D augmentation
    python scripts/run_complete_pipeline.py --mode full --enable-augmentation

    # Skip to training only
    python scripts/run_complete_pipeline.py --mode train --skip-download --skip-annotation

    # Train both baseline and 3D-augmented for comparison
    python scripts/run_complete_pipeline.py --train-baseline --enable-augmentation

    # Interactive mode (prompts for each step)
    python scripts/run_complete_pipeline.py --mode interactive
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cuneiform_translator.io.pipeline import DataPipeline


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the complete cuneiform translator pipeline."""

    def __init__(
        self,
        project_root: Path,
        data_dir: Optional[Path] = None,
        models_dir: Optional[Path] = None,
        interactive: bool = False,
    ):
        """Initialize orchestrator.

        Args:
            project_root: Root directory of the project
            data_dir: Base data directory (default: project_root/data)
            models_dir: Models output directory (default: project_root/models)
            interactive: Whether to prompt for confirmation at each step
        """
        self.project_root = Path(project_root)
        self.data_dir = Path(data_dir) if data_dir else self.project_root / "data"
        self.models_dir = Path(models_dir) if models_dir else self.project_root / "models"
        self.scripts_dir = self.project_root / "scripts"
        self.interactive = interactive

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.results = {}
        self.start_time = None
        self.step_times = {}

    def _print_header(self, title: str, level: int = 1) -> None:
        """Print formatted header."""
        if level == 1:
            print("\n" + "=" * 70)
            print(f"  {title}")
            print("=" * 70)
        elif level == 2:
            print(f"\n▶ {title}")
            print("-" * 70)

    def _print_success(self, message: str) -> None:
        """Print success message."""
        print(f"✓ {message}")

    def _print_warning(self, message: str) -> None:
        """Print warning message."""
        print(f"⚠ {message}")

    def _print_error(self, message: str) -> None:
        """Print error message."""
        print(f"✗ {message}")

    def _confirm_step(self, step_name: str) -> bool:
        """Ask for user confirmation before proceeding."""
        if not self.interactive:
            return True
        response = input(f"\nProceed with {step_name}? [y/N]: ").strip().lower()
        return response == "y"

    def _run_command(self, cmd: List[str], description: str) -> Tuple[bool, str]:
        """Run external command and capture output.

        Args:
            cmd: Command as list of strings
            description: Description for logging

        Returns:
            Tuple of (success, output_or_error)
        """
        try:
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
            )
            if result.returncode == 0:
                self._print_success(description)
                return True, result.stdout
            else:
                self._print_error(f"{description} failed")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            self._print_error(f"{description} timed out")
            return False, "Command timed out"
        except Exception as e:
            self._print_error(f"{description} error: {e}")
            return False, str(e)

    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met."""
        self._print_header("Validating Prerequisites", level=2)

        checks = []

        # Check Python version
        if sys.version_info >= (3, 9):
            self._print_success("Python 3.9+")
            checks.append(True)
        else:
            self._print_error(f"Python 3.9+ required (have {sys.version_info.major}.{sys.version_info.minor})")
            checks.append(False)

        # Check project structure
        required_dirs = [
            self.scripts_dir,
            self.project_root / "src" / "cuneiform_translator",
            self.data_dir,
        ]
        for required_dir in required_dirs:
            if required_dir.exists():
                self._print_success(f"Found {required_dir.relative_to(self.project_root)}")
                checks.append(True)
            else:
                self._print_error(f"Missing {required_dir.relative_to(self.project_root)}")
                checks.append(False)

        # Check key modules
        try:
            import numpy
            self._print_success("NumPy installed")
            checks.append(True)
        except ImportError:
            self._print_error("NumPy not found")
            checks.append(False)

        try:
            import cv2
            self._print_success("OpenCV installed")
            checks.append(True)
        except ImportError:
            self._print_error("OpenCV not found")
            checks.append(False)

        all_valid = all(checks)
        if all_valid:
            self._print_success(f"All prerequisites met ({len(checks)}/{len(checks)})")
        else:
            self._print_error(f"Prerequisites check failed ({sum(checks)}/{len(checks)})")
        return all_valid

    def step_1_download_data(self, num_tablets: int = 50) -> bool:
        """Step 1: Download tablet data from CDLI."""
        step_name = "STEP 1: Download Tablet Data"
        self._print_header(step_name)

        if not self._confirm_step(step_name):
            self._print_warning("Skipped by user")
            return False

        step_start = time.time()

        # Check if data already exists
        raw_dir = self.data_dir / "raw" / "cdli"
        if raw_dir.exists() and list(raw_dir.glob("*.jpg")):
            existing_count = len(list(raw_dir.glob("*.jpg")))
            self._print_success(f"Found {existing_count} existing tablets in {raw_dir.relative_to(self.project_root)}")
            if self.interactive:
                response = input("Download more? [y/N]: ").strip().lower()
                if response != "y":
                    self.results["download"] = {"status": "skipped", "count": existing_count}
                    self.step_times["download"] = time.time() - step_start
                    return True

        # Run download script
        cmd = [
            sys.executable,
            str(self.scripts_dir / "download_cdli_tablets.py"),
            "--num-tablets", str(num_tablets),
            "--output-dir", str(raw_dir),
        ]

        success, output = self._run_command(cmd, f"Downloaded {num_tablets} tablets")
        if success:
            # Count downloaded files
            if raw_dir.exists():
                count = len(list(raw_dir.glob("*.jpg")))
                self.results["download"] = {"status": "success", "count": count}
            else:
                self.results["download"] = {"status": "partial", "count": 0}
        else:
            self.results["download"] = {"status": "failed", "error": output}

        self.step_times["download"] = time.time() - step_start
        return success

    def step_2_annotation(self, batch_mode: bool = False) -> bool:
        """Step 2: Annotate tablets."""
        step_name = "STEP 2: Annotate Tablets"
        self._print_header(step_name)

        if not self._confirm_step(step_name):
            self._print_warning("Skipped by user")
            return False

        step_start = time.time()

        # Check for existing annotations
        processed_dir = self.data_dir / "processed"
        if processed_dir.exists():
            existing_annotations = len(list(processed_dir.glob("*.json")))
            self._print_success(f"Found {existing_annotations} existing annotations")
            if self.interactive:
                response = input("Add more annotations? [y/N]: ").strip().lower()
                if response != "y":
                    self.results["annotation"] = {"status": "skipped", "count": existing_annotations}
                    self.step_times["annotation"] = time.time() - step_start
                    return True

        self._print_warning("Annotation is interactive - manual step required")
        print("\nTo annotate tablets:")
        print(f"  python {self.scripts_dir}/annotate_tablets.py")
        print("\nAnnotations will be saved to:")
        print(f"  {processed_dir}")

        if self.interactive:
            input("\nPress Enter once you've completed annotations...")

        # Check what was annotated
        if processed_dir.exists():
            count = len(list(processed_dir.glob("*.json")))
            self.results["annotation"] = {"status": "completed", "count": count}
            self.step_times["annotation"] = time.time() - step_start
            return True
        else:
            self.results["annotation"] = {"status": "pending", "count": 0}
            self.step_times["annotation"] = time.time() - step_start
            return False

    def step_3_quality_check(self) -> bool:
        """Step 3: Validate data quality."""
        step_name = "STEP 3: Data Quality Validation"
        self._print_header(step_name)

        if not self._confirm_step(step_name):
            self._print_warning("Skipped by user")
            return False

        step_start = time.time()

        processed_dir = self.data_dir / "processed"
        if not processed_dir.exists() or not list(processed_dir.glob("*.json")):
            self._print_warning("No annotated tablets found - skipping quality check")
            self.results["quality_check"] = {"status": "no_data"}
            self.step_times["quality_check"] = time.time() - step_start
            return True

        # Run quality validation
        cmd = [
            sys.executable,
            str(self.scripts_dir / "validate_tablets.py"),
            "quality",
            "--batch",
            "--input-dir", str(processed_dir),
        ]

        success, output = self._run_command(cmd, "Data quality validation")

        # Parse results
        quality_report = {"status": "success" if success else "failed"}
        if success:
            # Extract key metrics from output
            if "PASS" in output:
                quality_report["result"] = "PASS"
            elif "WARNING" in output:
                quality_report["result"] = "WARNING"
            else:
                quality_report["result"] = "FAIL"

        self.results["quality_check"] = quality_report
        self.step_times["quality_check"] = time.time() - step_start
        return success

    def step_4_train_model(
        self,
        enable_augmentation: bool = False,
        train_baseline: bool = False,
        model_size: str = "m",
        epochs: int = 50,
        batch_size: int = 16,
        device: str = "mps",
    ) -> bool:
        """Step 4: Train YOLOv8 model."""
        step_name = "STEP 4: Train YOLOv8 Sign Detection Model"
        self._print_header(step_name)

        if not self._confirm_step(step_name):
            self._print_warning("Skipped by user")
            return False

        step_start = time.time()

        # Prepare arguments
        cmd = [
            sys.executable,
            str(self.scripts_dir / "train_sign_detector_3d.py"),
            "--annotations", str(self.data_dir / "processed"),
            "--images", str(self.data_dir / "processed" / "images"),
            "--ply-dir", str(self.data_dir / "raw" / "3d_models"),
            "--models-output", str(self.models_dir),
            "--model", model_size,
            "--epochs", str(epochs),
            "--batch-size", str(batch_size),
            "--device", device,
        ]

        if enable_augmentation:
            cmd.append("--enable-augmentation")
            print(f"🎨 Training with 3D augmentation enabled")

        if train_baseline:
            cmd.append("--train-baseline")
            print(f"📊 Will train both baseline and 3D-augmented models for comparison")

        success, output = self._run_command(cmd, "Model training")

        training_result = {
            "status": "success" if success else "failed",
            "model_size": model_size,
            "epochs": epochs,
            "batch_size": batch_size,
            "device": device,
            "augmentation_enabled": enable_augmentation,
            "trained_baseline": train_baseline,
        }

        self.results["training"] = training_result
        self.step_times["training"] = time.time() - step_start
        return success

    def step_5_evaluate(self) -> bool:
        """Step 5: Evaluate model and generate summary."""
        step_name = "STEP 5: Evaluation & Summary"
        self._print_header(step_name)

        if not self._confirm_step(step_name):
            self._print_warning("Skipped by user")
            return False

        step_start = time.time()

        # Check for trained models
        if not self.models_dir.exists() or not list(self.models_dir.glob("best.pt")):
            self._print_warning("No trained model found")
            self.results["evaluation"] = {"status": "no_model"}
            self.step_times["evaluation"] = time.time() - step_start
            return False

        self._print_success("Found trained model(s)")
        self.results["evaluation"] = {"status": "complete"}
        self.step_times["evaluation"] = time.time() - step_start
        return True

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive pipeline report."""
        self._print_header("PIPELINE SUMMARY", level=1)

        total_time = time.time() - self.start_time if self.start_time else 0

        # Calculate aggregate statistics
        print("\n📊 EXECUTION TIMELINE")
        print("-" * 70)
        for step, elapsed in self.step_times.items():
            minutes, seconds = divmod(int(elapsed), 60)
            print(f"  {step:20} {minutes:2}m {seconds:02}s")

        print(f"\n  {'Total pipeline':20} {int(total_time // 60):2}m {int(total_time % 60):02}s")

        # Results summary
        print("\n📋 RESULTS")
        print("-" * 70)

        for step, result in self.results.items():
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                if status == "success":
                    icon = "✓"
                elif status in ("skipped", "pending"):
                    icon = "⊘"
                else:
                    icon = "✗"

                print(f"  {icon} {step}: {status}")
                for key, value in result.items():
                    if key != "status" and key != "error":
                        print(f"      {key}: {value}")

        # Recommendations
        print("\n💡 NEXT STEPS")
        print("-" * 70)

        if self.results.get("training", {}).get("status") == "success":
            print("  • Model training complete! Available models:")
            for model in sorted(self.models_dir.glob("*.pt")):
                print(f"    - {model.name}")
            print("\n  • To use the model for inference:")
            print(f"    python scripts/infer_signs.py --model {self.models_dir}/best.pt \\")
            print(f"      --image <tablet_image.jpg> --output predictions.json")
        else:
            print("  • Review training results above")

        if self.results.get("annotation", {}).get("status") == "completed":
            print("\n  • Review annotated data:")
            print(f"    ls {self.data_dir}/processed/")

        # Save report to JSON
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time_seconds": total_time,
            "step_times": self.step_times,
            "results": self.results,
        }

        report_path = self.project_root / "pipeline_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        self._print_success(f"\nReport saved to {report_path.relative_to(self.project_root)}")

        return report

    def run_full_pipeline(
        self,
        skip_download: bool = False,
        skip_annotation: bool = False,
        skip_quality: bool = False,
        skip_training: bool = False,
        skip_evaluation: bool = False,
        enable_augmentation: bool = False,
        train_baseline: bool = False,
        num_tablets: int = 50,
        model_size: str = "m",
        epochs: int = 50,
        batch_size: int = 16,
        device: str = "mps",
    ) -> bool:
        """Run complete pipeline with specified options."""
        self.start_time = time.time()

        self._print_header("CUNEIFORM TRANSLATOR PIPELINE", level=1)
        print(f"Project root: {self.project_root}")
        print(f"Data directory: {self.data_dir.relative_to(self.project_root)}")
        print(f"Models directory: {self.models_dir.relative_to(self.project_root)}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Validate prerequisites
        if not self.validate_prerequisites():
            self._print_error("Prerequisites validation failed")
            return False

        # Run pipeline steps
        steps = [
            (not skip_download, self.step_1_download_data, {"num_tablets": num_tablets}),
            (not skip_annotation, self.step_2_annotation, {}),
            (not skip_quality, self.step_3_quality_check, {}),
            (
                not skip_training,
                self.step_4_train_model,
                {
                    "enable_augmentation": enable_augmentation,
                    "train_baseline": train_baseline,
                    "model_size": model_size,
                    "epochs": epochs,
                    "batch_size": batch_size,
                    "device": device,
                },
            ),
            (not skip_evaluation, self.step_5_evaluate, {}),
        ]

        for should_run, step_func, kwargs in steps:
            if should_run:
                try:
                    step_func(**kwargs)
                except Exception as e:
                    logger.error(f"Step failed with error: {e}", exc_info=True)
                    self._print_error(f"Unexpected error: {e}")

        # Generate final report
        self.generate_report()

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cuneiform Translator Complete Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with all steps
  python scripts/run_complete_pipeline.py --mode full

  # Full pipeline with 3D augmentation
  python scripts/run_complete_pipeline.py --mode full --enable-augmentation

  # Compare baseline vs 3D-augmented training
  python scripts/run_complete_pipeline.py --mode full --enable-augmentation --train-baseline

  # Skip to training with existing data
  python scripts/run_complete_pipeline.py --skip-download --skip-annotation --skip-quality

  # Interactive mode (prompts for each step)
  python scripts/run_complete_pipeline.py --mode interactive
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["full", "interactive", "training-only"],
        default="full",
        help="Pipeline mode",
    )

    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip data download step",
    )

    parser.add_argument(
        "--skip-annotation",
        action="store_true",
        help="Skip annotation step",
    )

    parser.add_argument(
        "--skip-quality",
        action="store_true",
        help="Skip quality validation step",
    )

    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip model training step",
    )

    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Skip evaluation step",
    )

    parser.add_argument(
        "--enable-augmentation",
        action="store_true",
        help="Enable 3D augmentation during training",
    )

    parser.add_argument(
        "--train-baseline",
        action="store_true",
        help="Also train baseline model (for comparison)",
    )

    parser.add_argument(
        "--num-tablets",
        type=int,
        default=50,
        help="Number of tablets to download",
    )

    parser.add_argument(
        "--model",
        choices=["n", "s", "m", "l", "x"],
        default="m",
        help="YOLOv8 model size",
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
        choices=["cpu", "cuda", "mps"],
        default="mps",
        help="Training device",
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project root directory",
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Data directory (default: project_root/data)",
    )

    parser.add_argument(
        "--models-dir",
        type=Path,
        help="Models output directory (default: project_root/models)",
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = PipelineOrchestrator(
        project_root=args.project_root,
        data_dir=args.data_dir,
        models_dir=args.models_dir,
        interactive=(args.mode == "interactive"),
    )

    # Determine which steps to skip
    skip_download = args.skip_download or args.mode == "training-only"
    skip_annotation = args.skip_annotation or args.mode == "training-only"
    skip_quality = args.skip_quality or args.mode == "training-only"
    skip_training = args.skip_training
    skip_evaluation = args.skip_evaluation

    # Run pipeline
    success = orchestrator.run_full_pipeline(
        skip_download=skip_download,
        skip_annotation=skip_annotation,
        skip_quality=skip_quality,
        skip_training=skip_training,
        skip_evaluation=skip_evaluation,
        enable_augmentation=args.enable_augmentation,
        train_baseline=args.train_baseline,
        num_tablets=args.num_tablets,
        model_size=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        device=args.device,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
