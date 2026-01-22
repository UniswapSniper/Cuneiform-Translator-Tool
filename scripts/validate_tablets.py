#!/usr/bin/env python3
"""
Tablet annotation quality and inter-annotator agreement analyzer.

Provides CLI tools for:
- Data quality checks (overlaps, bounds validation)
- Inter-annotator agreement metrics (Fleiss' kappa, position agreement)
- Annotation comparison reports
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from cuneiform_translator.io import DataPipeline, IAA, TabletRecord

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TabletValidator:
    """Command-line interface for tablet validation and IAA analysis."""

    def __init__(self, data_dir: Path = Path("data")):
        """Initialize validator with data directory."""
        self.data_dir = Path(data_dir)
        self.pipeline = DataPipeline(self.data_dir)

    def check_quality(
        self,
        tablet_path: Path,
        image_width: int = 1024,
        image_height: int = 768,
        output: Optional[Path] = None,
    ) -> dict:
        """
        Check data quality of a single tablet.

        Args:
            tablet_path: Path to tablet JSON file
            image_width: Expected image width
            image_height: Expected image height
            output: Optional output file for report

        Returns:
            Quality report dict
        """
        logger.info(f"Checking quality of {tablet_path}")

        record = self.pipeline.load_tablet_record(tablet_path)
        if not record:
            logger.error(f"Failed to load tablet from {tablet_path}")
            return {}

        report = self.pipeline.generate_quality_report(record, image_width, image_height)

        logger.info(
            f"Quality score: {report['quality_score']:.1f} [{report['quality_status'].upper()}]"
        )
        logger.info(f"Total regions: {report['checks']['overlapping_regions']['total_regions']}")

        if report["issues"]:
            logger.warning("Issues found:")
            for issue in report["issues"]:
                logger.warning(f"  - {issue}")

        if output:
            with open(output, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output}")

        return report

    def check_batch_quality(
        self, input_dir: Path, output_dir: Optional[Path] = None
    ) -> dict:
        """
        Check quality of all tablets in a directory.

        Args:
            input_dir: Directory containing tablet JSON files
            output_dir: Optional directory to save individual reports

        Returns:
            Summary statistics
        """
        logger.info(f"Checking quality of tablets in {input_dir}")

        tablet_files = sorted(input_dir.glob("*.json"))
        if not tablet_files:
            logger.warning(f"No JSON files found in {input_dir}")
            return {}

        reports = []
        summary = {
            "total_tablets": len(tablet_files),
            "quality_distribution": {"pass": 0, "warning": 0, "fail": 0},
            "average_score": 0.0,
            "tablets_with_overlaps": 0,
            "tablets_with_bounds_errors": 0,
            "tablet_reports": [],
        }

        for tablet_file in tablet_files:
            report = self.check_quality(tablet_file, output=None)
            reports.append(report)

            if report:
                summary["quality_distribution"][report["quality_status"]] += 1
                summary["tablet_reports"].append(
                    {
                        "tablet_id": report["tablet_id"],
                        "quality_score": report["quality_score"],
                        "status": report["quality_status"],
                        "num_issues": len(report["issues"]),
                    }
                )

                if report["checks"]["overlapping_regions"]["has_overlaps"]:
                    summary["tablets_with_overlaps"] += 1
                if report["checks"]["bounds_validity"]["has_errors"]:
                    summary["tablets_with_bounds_errors"] += 1

                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / f"{report['tablet_id']}_quality.json"
                    with open(output_file, "w") as f:
                        json.dump(report, f, indent=2)

        # Calculate summary stats
        if reports:
            scores = [r.get("quality_score", 0) for r in reports if r]
            summary["average_score"] = sum(scores) / len(scores) if scores else 0

        logger.info(f"\n=== BATCH QUALITY SUMMARY ===")
        logger.info(f"Total tablets: {summary['total_tablets']}")
        logger.info(
            f"Pass: {summary['quality_distribution']['pass']}, "
            f"Warning: {summary['quality_distribution']['warning']}, "
            f"Fail: {summary['quality_distribution']['fail']}"
        )
        logger.info(f"Average score: {summary['average_score']:.1f}/100")
        logger.info(f"Tablets with overlaps: {summary['tablets_with_overlaps']}")
        logger.info(f"Tablets with bounds errors: {summary['tablets_with_bounds_errors']}")

        return summary

    def compare_annotators(
        self,
        annotator_a: str,
        annotator_b: str,
        annotator_a_dir: Path,
        annotator_b_dir: Path,
        output: Optional[Path] = None,
    ) -> dict:
        """
        Compare annotations between two annotators.

        Args:
            annotator_a: Name of first annotator
            annotator_b: Name of second annotator
            annotator_a_dir: Directory with annotator A's tablets
            annotator_b_dir: Directory with annotator B's tablets
            output: Optional output file for report

        Returns:
            Comparison report
        """
        logger.info(f"Comparing {annotator_a} vs {annotator_b}")

        # Load tablets from both annotators
        records_a = {}
        records_b = {}

        for tablet_file in annotator_a_dir.glob("*.json"):
            record = self.pipeline.load_tablet_record(tablet_file)
            if record:
                records_a[record.tablet_id] = record

        for tablet_file in annotator_b_dir.glob("*.json"):
            record = self.pipeline.load_tablet_record(tablet_file)
            if record:
                records_b[record.tablet_id] = record

        logger.info(f"Loaded {len(records_a)} tablets from {annotator_a}")
        logger.info(f"Loaded {len(records_b)} tablets from {annotator_b}")

        # Find common tablets
        common_tablets = set(records_a.keys()) & set(records_b.keys())
        logger.info(f"Common tablets: {len(common_tablets)}")

        if not common_tablets:
            logger.warning("No common tablets between annotators")
            return {}

        report = {
            "annotator_a": annotator_a,
            "annotator_b": annotator_b,
            "common_tablets": len(common_tablets),
            "pairwise_comparisons": [],
            "overall_stats": {
                "mean_position_agreement": 0.0,
                "mean_transliteration_agreement": 0.0,
                "mean_uncertainty_agreement": 0.0,
                "mean_damage_agreement": 0.0,
                "median_position_agreement": 0.0,
                "mean_matched_regions": 0.0,
                "mean_unmatched_regions": 0.0,
            },
        }

        position_vals = []
        trans_vals = []
        uncertain_vals = []
        damage_vals = []
        matched_counts = []
        unmatched_counts = []

        for tablet_id in sorted(common_tablets):
            comparison = IAA.calculate_agreement_on_pair(
                records_a[tablet_id].regions, records_b[tablet_id].regions
            )

            report["pairwise_comparisons"].append(
                {
                    "tablet_id": tablet_id,
                    "num_regions_a": comparison["num_regions_a"],
                    "num_regions_b": comparison["num_regions_b"],
                    "matches": comparison["matches"],
                    "unmatched_a": comparison["unmatched_a"],
                    "unmatched_b": comparison["unmatched_b"],
                    "position_agreement": comparison["position_agreement"],
                    "transliteration_agreement": comparison["transliteration_agreement"],
                    "uncertainty_agreement": comparison["uncertainty_agreement"],
                    "damage_agreement": comparison["damage_agreement"],
                }
            )

            position_vals.append(comparison["position_agreement"])
            trans_vals.append(comparison["transliteration_agreement"])
            uncertain_vals.append(comparison["uncertainty_agreement"])
            damage_vals.append(comparison["damage_agreement"])
            matched_counts.append(comparison["matches"])
            unmatched_counts.append(
                comparison["unmatched_a"] + comparison["unmatched_b"]
            )

        # Calculate summary stats
        if position_vals:
            import statistics

            report["overall_stats"]["mean_position_agreement"] = (
                sum(position_vals) / len(position_vals)
            )
            report["overall_stats"]["mean_transliteration_agreement"] = (
                sum(trans_vals) / len(trans_vals)
            )
            report["overall_stats"]["mean_uncertainty_agreement"] = (
                sum(uncertain_vals) / len(uncertain_vals)
            )
            report["overall_stats"]["mean_damage_agreement"] = (
                sum(damage_vals) / len(damage_vals)
            )
            report["overall_stats"]["median_position_agreement"] = (
                statistics.median(position_vals)
            )
            report["overall_stats"]["mean_matched_regions"] = (
                sum(matched_counts) / len(matched_counts)
            )
            report["overall_stats"]["mean_unmatched_regions"] = (
                sum(unmatched_counts) / len(unmatched_counts)
            )

        logger.info(f"\n=== ANNOTATOR COMPARISON SUMMARY ===")
        logger.info(f"Mean position agreement: {report['overall_stats']['mean_position_agreement']:.3f}")
        logger.info(f"Mean transliteration agreement: {report['overall_stats']['mean_transliteration_agreement']:.3f}")
        logger.info(f"Mean uncertainty agreement: {report['overall_stats']['mean_uncertainty_agreement']:.3f}")
        logger.info(f"Mean damage agreement: {report['overall_stats']['mean_damage_agreement']:.3f}")
        logger.info(f"Mean matched regions: {report['overall_stats']['mean_matched_regions']:.1f}")

        if output:
            with open(output, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output}")

        return report


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Tablet annotation quality and IAA analyzer"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Quality check commands
    quality_parser = subparsers.add_parser("quality", help="Check data quality")
    quality_parser.add_argument(
        "--tablet",
        type=Path,
        help="Path to single tablet JSON file",
    )
    quality_parser.add_argument(
        "--batch",
        type=Path,
        help="Directory containing multiple tablet JSON files",
    )
    quality_parser.add_argument(
        "--output",
        type=Path,
        help="Output file or directory for reports",
    )
    quality_parser.add_argument(
        "--image-width",
        type=int,
        default=1024,
        help="Expected image width (default: 1024)",
    )
    quality_parser.add_argument(
        "--image-height",
        type=int,
        default=768,
        help="Expected image height (default: 768)",
    )

    # IAA comparison commands
    compare_parser = subparsers.add_parser(
        "compare", help="Compare annotations between annotators"
    )
    compare_parser.add_argument(
        "--annotator-a",
        type=str,
        required=True,
        help="Name of first annotator",
    )
    compare_parser.add_argument(
        "--annotator-a-dir",
        type=Path,
        required=True,
        help="Directory with first annotator's tablets",
    )
    compare_parser.add_argument(
        "--annotator-b",
        type=str,
        required=True,
        help="Name of second annotator",
    )
    compare_parser.add_argument(
        "--annotator-b-dir",
        type=Path,
        required=True,
        help="Directory with second annotator's tablets",
    )
    compare_parser.add_argument(
        "--output",
        type=Path,
        help="Output file for comparison report",
    )

    args = parser.parse_args()
    validator = TabletValidator()

    if args.command == "quality":
        if args.tablet:
            validator.check_quality(
                args.tablet,
                image_width=args.image_width,
                image_height=args.image_height,
                output=args.output,
            )
        elif args.batch:
            validator.check_batch_quality(args.batch, output_dir=args.output)
        else:
            logger.error("Must specify --tablet or --batch")

    elif args.command == "compare":
        validator.compare_annotators(
            args.annotator_a,
            args.annotator_b,
            args.annotator_a_dir,
            args.annotator_b_dir,
            output=args.output,
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
