"""
Inter-Annotator Agreement (IAA) metrics for multi-annotator tablet annotations.

This module provides statistical measures to assess agreement between multiple
annotators on tablet region annotations, including:
- Fleiss' kappa for categorical agreement
- Position-based agreement for region coordinates
- Transliteration agreement metrics
"""

import logging
from collections import Counter, defaultdict
from typing import Any, Optional

import numpy as np
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AnnotatorComparison(BaseModel):
    """Result of comparing annotations from multiple annotators."""

    tablet_id: str
    annotators: list[str]
    num_annotators: int
    num_regions: dict[str, int]  # Count of regions per annotator
    categorical_agreement: float  # Fleiss' kappa
    transliteration_agreement: float  # Percentage match
    region_position_agreement: float  # Mean IoU of regions
    issues: list[str] = []


class IAA:
    """Inter-Annotator Agreement metrics calculator."""

    @staticmethod
    def fleiss_kappa(matrix: list[list[int]]) -> float:
        """
        Calculate Fleiss' kappa for categorical agreement.

        This metric assesses the agreement between multiple raters for
        categorical outcomes, accounting for chance agreement.

        Args:
            matrix: m x k matrix where m is number of subjects (regions),
                   k is number of categories (e.g., sign types)
                   Each cell [i,j] is the count of raters selecting category j for subject i

        Returns:
            Kappa value (-1 to 1), where:
            - 1.0 = perfect agreement
            - 0.0 = chance agreement
            - < 0 = worse than chance
        """
        if not matrix or len(matrix) == 0:
            return 0.0

        matrix = np.array(matrix, dtype=float)
        m, k = matrix.shape  # m subjects, k categories

        # Number of raters per subject
        n = matrix.sum(axis=1)[0]  # Assumes same n for all subjects

        # Proportion of agreements for each subject
        p_o = (np.sum(matrix * (matrix - 1), axis=1) / (n * (n - 1))).mean()

        # Marginal proportions
        p_e = np.sum((matrix.sum(axis=0) / (m * n)) ** 2)

        if p_e == 1:
            return 0.0

        # Fleiss' kappa
        kappa = (p_o - p_e) / (1 - p_e)
        return float(np.clip(kappa, -1, 1))

    @staticmethod
    def iou(region_i: list[list[float]], region_j: list[list[float]]) -> float:
        """
        Calculate Intersection over Union (IoU) for two regions.

        Args:
            region_i: List of [x, y] coordinates for region i
            region_j: List of [x, y] coordinates for region j

        Returns:
            IoU value (0 to 1)
        """
        try:
            from shapely.geometry import Polygon
        except ImportError:
            logger.warning("Shapely not available for IoU calculation, returning 0")
            return 0.0

        if len(region_i) < 3 or len(region_j) < 3:
            return 0.0

        try:
            poly_i = Polygon(region_i)
            poly_j = Polygon(region_j)

            if not (poly_i.is_valid and poly_j.is_valid):
                return 0.0

            intersection = poly_i.intersection(poly_j).area
            union = poly_i.union(poly_j).area

            if union == 0:
                return 0.0

            return float(intersection / union)
        except Exception as e:
            logger.warning(f"Error calculating IoU: {e}")
            return 0.0

    @staticmethod
    def match_regions(
        regions_a: list[Any], regions_b: list[Any], iou_threshold: float = 0.5
    ) -> tuple[list[tuple[Any, Any]], list[Any], list[Any]]:
        """
        Match regions between two annotators based on spatial overlap.

        Args:
            regions_a: Regions from annotator A
            regions_b: Regions from annotator B
            iou_threshold: Minimum IoU to consider regions matched

        Returns:
            (matches: list of (region_a, region_b) tuples,
             unmatched_a: regions from A with no match,
             unmatched_b: regions from B with no match)
        """
        matches = []
        matched_a = set()
        matched_b = set()

        # Find best matches based on IoU
        for i, region_a in enumerate(regions_a):
            best_j = -1
            best_iou = 0

            for j, region_b in enumerate(regions_b):
                if j in matched_b:
                    continue

                iou = IAA.iou(region_a.coordinates, region_b.coordinates)
                if iou > best_iou:
                    best_iou = iou
                    best_j = j

            if best_iou >= iou_threshold:
                matches.append((region_a, regions_b[best_j]))
                matched_a.add(i)
                matched_b.add(best_j)

        unmatched_a = [r for i, r in enumerate(regions_a) if i not in matched_a]
        unmatched_b = [r for j, r in enumerate(regions_b) if j not in matched_b]

        return matches, unmatched_a, unmatched_b

    @staticmethod
    def calculate_agreement_on_pair(
        regions_a: list[Any], regions_b: list[Any]
    ) -> dict[str, Any]:
        """
        Calculate agreement metrics between two annotators for a tablet.

        Args:
            regions_a: Regions from annotator A
            regions_b: Regions from annotator B

        Returns:
            Agreement report with various metrics
        """
        report = {
            "num_regions_a": len(regions_a),
            "num_regions_b": len(regions_b),
            "matches": 0,
            "unmatched_a": len(regions_a),
            "unmatched_b": len(regions_b),
            "position_agreement": 0.0,
            "transliteration_agreement": 0.0,
            "uncertainty_agreement": 0.0,
            "damage_agreement": 0.0,
            "issues": [],
        }

        if len(regions_a) == 0 and len(regions_b) == 0:
            report["position_agreement"] = 1.0
            return report

        if len(regions_a) == 0 or len(regions_b) == 0:
            report["issues"].append("One annotator provided no regions")
            return report

        # Match regions spatially
        matches, unmatched_a, unmatched_b = IAA.match_regions(regions_a, regions_b)
        report["matches"] = len(matches)
        report["unmatched_a"] = len(unmatched_a)
        report["unmatched_b"] = len(unmatched_b)

        if len(matches) == 0:
            report["issues"].append("No matching regions found between annotators")
            return report

        # Calculate position agreement (mean IoU of matched regions)
        ious = [
            IAA.iou(r_a.coordinates, r_b.coordinates) for r_a, r_b in matches
        ]
        report["position_agreement"] = float(np.mean(ious))

        # Calculate transliteration agreement
        trans_matches = 0
        for r_a, r_b in matches:
            if (r_a.transliteration or "").lower() == (
                r_b.transliteration or ""
            ).lower():
                trans_matches += 1
        report["transliteration_agreement"] = (
            trans_matches / len(matches) if matches else 0.0
        )

        # Calculate uncertainty agreement
        uncertain_matches = sum(
            1 for r_a, r_b in matches if r_a.uncertain == r_b.uncertain
        )
        report["uncertainty_agreement"] = (
            uncertain_matches / len(matches) if matches else 0.0
        )

        # Calculate damage agreement
        damage_matches = sum(1 for r_a, r_b in matches if r_a.damaged == r_b.damaged)
        report["damage_agreement"] = damage_matches / len(matches) if matches else 0.0

        return report

    @staticmethod
    def calculate_multi_annotator_agreement(
        records: dict[str, list[Any]],
    ) -> dict[str, Any]:
        """
        Calculate agreement metrics for multiple annotators on same tablets.

        Args:
            records: Dict mapping annotator_id -> list of TabletRecords

        Returns:
            Summary agreement statistics
        """
        annotator_ids = list(records.keys())

        if len(annotator_ids) < 2:
            return {"error": "Need at least 2 annotators"}

        summary = {
            "annotators": annotator_ids,
            "num_annotators": len(annotator_ids),
            "total_tablets_compared": 0,
            "pairwise_agreements": defaultdict(list),
            "overall_stats": {
                "mean_position_agreement": 0.0,
                "mean_transliteration_agreement": 0.0,
                "mean_uncertainty_agreement": 0.0,
                "mean_damage_agreement": 0.0,
            },
        }

        # Compare all pairs
        position_vals = []
        trans_vals = []
        uncertain_vals = []
        damage_vals = []

        for i, annotator_a in enumerate(annotator_ids):
            for annotator_b in annotator_ids[i + 1 :]:
                pair_key = f"{annotator_a}_{annotator_b}"

                # Find common tablets
                tablets_a = {r.tablet_id: r for r in records[annotator_a]}
                tablets_b = {r.tablet_id: r for r in records[annotator_b]}

                common_tablets = set(tablets_a.keys()) & set(tablets_b.keys())

                for tablet_id in common_tablets:
                    agreement = IAA.calculate_agreement_on_pair(
                        tablets_a[tablet_id].regions, tablets_b[tablet_id].regions
                    )

                    summary["pairwise_agreements"][pair_key].append(
                        {
                            "tablet_id": tablet_id,
                            "agreement": agreement,
                        }
                    )

                    position_vals.append(agreement["position_agreement"])
                    trans_vals.append(agreement["transliteration_agreement"])
                    uncertain_vals.append(agreement["uncertainty_agreement"])
                    damage_vals.append(agreement["damage_agreement"])

                summary["total_tablets_compared"] = len(common_tablets)

        # Calculate overall stats
        if position_vals:
            summary["overall_stats"]["mean_position_agreement"] = float(
                np.mean(position_vals)
            )
            summary["overall_stats"]["mean_transliteration_agreement"] = float(
                np.mean(trans_vals)
            )
            summary["overall_stats"]["mean_uncertainty_agreement"] = float(
                np.mean(uncertain_vals)
            )
            summary["overall_stats"]["mean_damage_agreement"] = float(
                np.mean(damage_vals)
            )

        return summary
