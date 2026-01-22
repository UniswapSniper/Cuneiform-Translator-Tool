#!/usr/bin/env python3
"""
Annotation tool for manual tablet annotation.

Provides a CLI for:
- Loading tablet images
- Drawing/defining regions (bounding boxes or polygons)
- Entering transliterations
- Saving annotated records

Usage:
    python scripts/annotate_tablets.py --tablet P100001 --image data/raw/cdli/P100001_obverse.jpg
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from cuneiform_translator.io import DataPipeline, TabletRecord, TabletProvenance, TabletMetadata, Region

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


class AnnotationTool:
    """Interactive annotation tool for cuneiform tablets."""

    def __init__(self, data_dir: Path = DATA_DIR):
        """Initialize annotation tool."""
        self.data_dir = Path(data_dir)
        self.pipeline = DataPipeline(data_dir)
        self.current_tablet: Optional[TabletRecord] = None

    def new_tablet(
        self,
        tablet_id: str,
        period: str = "Ur III",
        language: str = "Sumerian",
        genre: str = "administrative",
        museum: Optional[str] = None,
        museum_id: Optional[str] = None,
    ) -> TabletRecord:
        """Create a new tablet record."""
        logger.info(f"Creating new tablet: {tablet_id}")

        provenance = TabletProvenance(
            tablet_id=tablet_id,
            period=period,
            museum=museum,
            museum_id=museum_id,
            source_license="CC0 1.0 Universal",
        )

        metadata = TabletMetadata(
            language=language,
            genre=genre,
            date_created=datetime.now().isoformat(),
            status="draft",
        )

        tablet = TabletRecord(
            tablet_id=tablet_id,
            provenance=provenance,
            image_paths={},
            regions=[],
            metadata=metadata,
        )

        self.current_tablet = tablet
        return tablet

    def add_region(
        self,
        region_id: str,
        coordinates: list[list[float]],
        transliteration: str = "",
        sign_candidate: Optional[str] = None,
        region_type: str = "box",
        damaged: bool = False,
        uncertain: bool = False,
        notes: str = "",
        annotated_by: str = "user@example.com",
    ) -> None:
        """Add a region to the current tablet."""
        if not self.current_tablet:
            raise ValueError("No tablet loaded. Call new_tablet() first.")

        region = Region(
            region_id=region_id,
            type=region_type,
            coordinates=coordinates,
            transliteration=transliteration,
            sign_candidate=sign_candidate,
            damaged=damaged,
            uncertain=uncertain,
            notes=notes,
            annotated_by=annotated_by,
            timestamp=datetime.now().isoformat(),
        )

        self.current_tablet.regions.append(region)
        logger.info(f"Added region {region_id}: {transliteration}")

    def set_image_path(self, image_type: str, path: str) -> None:
        """Set image path (obverse, reverse, edge)."""
        if not self.current_tablet:
            raise ValueError("No tablet loaded. Call new_tablet() first.")

        self.current_tablet.image_paths[image_type] = path
        logger.info(f"Set {image_type} image: {path}")

    def save_tablet(self, output_dir: Optional[Path] = None) -> Path:
        """Save the current tablet."""
        if not self.current_tablet:
            raise ValueError("No tablet loaded. Call new_tablet() first.")

        if output_dir is None:
            output_dir = self.data_dir / "processed"

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{self.current_tablet.tablet_id}.json"

        success = self.pipeline.save_tablet_record(self.current_tablet, output_path)
        if success:
            logger.info(f"Saved tablet to {output_path}")
        else:
            logger.error(f"Failed to save tablet to {output_path}")

        return output_path

    def load_tablet(self, tablet_path: Path) -> Optional[TabletRecord]:
        """Load an existing tablet."""
        tablet = self.pipeline.load_tablet_record(tablet_path)
        if tablet:
            self.current_tablet = tablet
            logger.info(f"Loaded tablet {tablet.tablet_id}")
        return tablet

    def interactive_annotate(self, tablet_id: str, image_path: Optional[Path] = None) -> None:
        """Interactive annotation session (simplified CLI version)."""
        print("\n" + "=" * 60)
        print(f"ANNOTATION TOOL - Tablet {tablet_id}")
        print("=" * 60)

        # Create new tablet
        self.new_tablet(tablet_id=tablet_id)

        if image_path:
            self.set_image_path("primary", str(image_path))

        # Interactive menu
        while True:
            print("\nOptions:")
            print("  1. Add region")
            print("  2. List regions")
            print("  3. Edit region")
            print("  4. Delete region")
            print("  5. Set metadata")
            print("  6. Save and exit")
            print("  7. Cancel")

            choice = input("\nEnter choice (1-7): ").strip()

            if choice == "1":
                self._interactive_add_region()
            elif choice == "2":
                self._interactive_list_regions()
            elif choice == "3":
                self._interactive_edit_region()
            elif choice == "4":
                self._interactive_delete_region()
            elif choice == "5":
                self._interactive_set_metadata()
            elif choice == "6":
                output_path = self.save_tablet()
                print(f"\n✓ Tablet saved to {output_path}")
                break
            elif choice == "7":
                print("Annotation cancelled.")
                break
            else:
                print("Invalid choice. Try again.")

    def _interactive_add_region(self) -> None:
        """Interactive region addition."""
        region_id = input("Region ID (e.g., r001): ").strip()
        transliteration = input("Transliteration (e.g., 'ra'): ").strip()
        sign_candidate = input("Sign candidate (optional, e.g., 'RA'): ").strip() or None
        damaged = input("Damaged? (y/n): ").strip().lower() == "y"
        uncertain = input("Uncertain? (y/n): ").strip().lower() == "y"
        notes = input("Notes (optional): ").strip()

        # For simplicity, use a box with mock coordinates
        x1 = float(input("Box top-left X: ") or "0")
        y1 = float(input("Box top-left Y: ") or "0")
        x2 = float(input("Box bottom-right X: ") or "100")
        y2 = float(input("Box bottom-right Y: ") or "100")

        coordinates = [[x1, y1], [x2, y2]]

        self.add_region(
            region_id=region_id,
            coordinates=coordinates,
            transliteration=transliteration,
            sign_candidate=sign_candidate,
            damaged=damaged,
            uncertain=uncertain,
            notes=notes,
        )

        print(f"✓ Region {region_id} added")

    def _interactive_list_regions(self) -> None:
        """List all regions in current tablet."""
        if not self.current_tablet or not self.current_tablet.regions:
            print("No regions in current tablet.")
            return

        print(f"\nRegions in {self.current_tablet.tablet_id}:")
        for i, region in enumerate(self.current_tablet.regions, 1):
            status = f"[{'DAMAGED' if region.damaged else ''}{'UNCERTAIN' if region.uncertain else ''}]".strip()
            print(
                f"  {i}. {region.region_id}: '{region.transliteration}' {status} - {region.notes[:30]}"
            )

    def _interactive_edit_region(self) -> None:
        """Edit an existing region."""
        if not self.current_tablet or not self.current_tablet.regions:
            print("No regions to edit.")
            return

        region_id = input("Region ID to edit: ").strip()
        region = next((r for r in self.current_tablet.regions if r.region_id == region_id), None)

        if not region:
            print(f"Region {region_id} not found.")
            return

        new_transliteration = input(f"New transliteration (current: '{region.transliteration}'): ").strip()
        if new_transliteration:
            region.transliteration = new_transliteration

        new_notes = input(f"New notes (current: '{region.notes}'): ").strip()
        if new_notes:
            region.notes = new_notes

        print(f"✓ Region {region_id} updated")

    def _interactive_delete_region(self) -> None:
        """Delete a region."""
        if not self.current_tablet or not self.current_tablet.regions:
            print("No regions to delete.")
            return

        region_id = input("Region ID to delete: ").strip()
        original_count = len(self.current_tablet.regions)

        self.current_tablet.regions = [
            r for r in self.current_tablet.regions if r.region_id != region_id
        ]

        if len(self.current_tablet.regions) < original_count:
            print(f"✓ Region {region_id} deleted")
        else:
            print(f"Region {region_id} not found.")

    def _interactive_set_metadata(self) -> None:
        """Set tablet metadata."""
        if not self.current_tablet:
            print("No tablet loaded.")
            return

        print("\nCurrent metadata:")
        print(f"  Language: {self.current_tablet.metadata.language}")
        print(f"  Genre: {self.current_tablet.metadata.genre}")
        print(f"  Period: {self.current_tablet.provenance.period}")

        language = input("Language (Sumerian/Akkadian, or leave blank): ").strip()
        if language:
            self.current_tablet.metadata.language = language

        genre = input("Genre (administrative/literary, or leave blank): ").strip()
        if genre:
            self.current_tablet.metadata.genre = genre

        print("✓ Metadata updated")

    def batch_export_jsonl(self, output_path: Path = DATA_DIR / "processed" / "annotated.jsonl") -> int:
        """Export all annotated tablets to JSONL."""
        processed_dir = self.data_dir / "processed"
        if not processed_dir.exists():
            logger.warning(f"No processed directory: {processed_dir}")
            return 0

        count = 0
        with open(output_path, "w") as f:
            for json_file in sorted(processed_dir.glob("*.json")):
                if json_file.name == "sample_tablet_record.json":
                    continue
                record = self.pipeline.load_tablet_record(json_file)
                if record:
                    f.write(json.dumps(record.model_dump()) + "\n")
                    count += 1

        logger.info(f"Exported {count} tablets to {output_path}")
        return count


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Cuneiform tablet annotation tool")
    parser.add_argument("--tablet", help="Tablet ID (e.g., P100001)")
    parser.add_argument("--image", type=Path, help="Path to tablet image")
    parser.add_argument("--period", default="Ur III", help="Time period")
    parser.add_argument("--language", default="Sumerian", help="Language")
    parser.add_argument("--genre", default="administrative", help="Genre")
    parser.add_argument("--museum", help="Museum name")
    parser.add_argument("--museum-id", help="Museum ID")
    parser.add_argument("--batch-export", action="store_true", help="Export all tablets to JSONL")
    parser.add_argument("--output", type=Path, help="Output file path")
    parser.add_argument("--interactive", action="store_true", help="Interactive annotation mode")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Data directory")

    args = parser.parse_args()

    tool = AnnotationTool(data_dir=args.data_dir)

    if args.batch_export:
        count = tool.batch_export_jsonl(args.output or args.data_dir / "processed" / "annotated.jsonl")
        print(f"✓ Exported {count} tablets")
    elif args.interactive or args.tablet:
        if not args.tablet:
            print("Error: --tablet required for interactive mode")
            return
        tool.interactive_annotate(args.tablet, args.image)
    else:
        # Simple mode: create tablet and show structure
        tablet = tool.new_tablet(
            args.tablet,
            period=args.period,
            language=args.language,
            genre=args.genre,
            museum=args.museum,
            museum_id=args.museum_id,
        )
        if args.image:
            tool.set_image_path("primary", str(args.image))
        
        # Example region
        tool.add_region(
            region_id="r001",
            coordinates=[[10, 20], [50, 60]],
            transliteration="ra",
            sign_candidate="RA",
        )

        output_path = tool.save_tablet(args.output.parent if args.output else None)
        print(f"✓ Tablet created and saved to {output_path}")


if __name__ == "__main__":
    main()
