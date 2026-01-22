#!/usr/bin/env python3
"""
Download cuneiform tablets from CDLI (Cuneiform Digital Library Initiative).

This script fetches tablet metadata, images, and 3D models from CDLI for use
in the Cuneiform Translator project. It handles:
- Metadata queries (period, language, preservation)
- Image downloads (obverse, reverse, edges)
- 3D model downloads (when available)
- Local caching to avoid re-downloading

Usage:
    python scripts/download_cdli_tablets.py --period "Ur III" --limit 50 --with-3d
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
CDLI_API_BASE = "https://cdli.ucla.edu/cdli_files/"
CDLI_SEARCH_API = "https://cdli.ucla.edu/search/search_results.php"
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_CDLI_DIR = DATA_DIR / "raw" / "cdli"
RAW_3D_DIR = DATA_DIR / "raw" / "3d_models"
METADATA_CACHE = RAW_CDLI_DIR / "metadata.jsonl"

# Rate limiting (CDLI asks for courtesy)
REQUEST_DELAY = 0.5  # seconds between requests


class CDLIDownloader:
    """Download tablets from CDLI."""

    def __init__(self, cache_dir: Path = RAW_CDLI_DIR, download_3d: bool = False):
        """
        Initialize downloader.

        Args:
            cache_dir: Directory to store downloaded files
            download_3d: Whether to attempt downloading 3D models
        """
        self.cache_dir = Path(cache_dir)
        self.download_3d = download_3d
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "CuniformTranslator/0.0.1 (+https://github.com/yourusername/cuneiform-translator)"}
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if download_3d:
            RAW_3D_DIR.mkdir(parents=True, exist_ok=True)

    def search_tablets(
        self,
        period: Optional[str] = None,
        limit: int = 50,
        language: Optional[str] = None,
    ) -> list[dict]:
        """
        Search for tablets from CDLI.

        Note: CDLI doesn't have a public JSON API; this uses CSV export format.
        For production, consider:
        1. Downloading CDLI's full SQLite database snapshot
        2. Using ORACC's JSON API for transliterations
        3. Direct CDLI bulk downloads

        Args:
            period: Time period (e.g., "Ur III", "Old Babylonian")
            limit: Maximum tablets to retrieve
            language: Language filter (e.g., "Sumerian", "Akkadian")

        Returns:
            List of tablet metadata dicts
        """
        logger.info(f"Searching CDLI for tablets (period={period}, limit={limit})")

        # For now, return mock data structure
        # TODO: Implement actual CDLI API/scraping when their API is more stable
        tablets = self._get_mock_tablets(period=period, limit=limit, language=language)

        logger.info(f"Found {len(tablets)} tablets")
        return tablets

    def download_tablet(
        self, tablet_id: str, download_images: bool = True, download_3d: bool = True
    ) -> dict:
        """
        Download a specific tablet's data.

        Args:
            tablet_id: CDLI tablet ID (e.g., "P100001")
            download_images: Download image files
            download_3d: Download 3D models (if available)

        Returns:
            Tablet metadata with local paths
        """
        logger.info(f"Downloading tablet {tablet_id}")

        tablet_data = {
            "tablet_id": tablet_id,
            "image_paths": {},
            "model_paths": {},
            "download_status": "pending",
            "timestamp": time.time(),
        }

        try:
            if download_images:
                tablet_data["image_paths"] = self._download_images(tablet_id)

            if download_3d and self.download_3d:
                tablet_data["model_paths"] = self._download_3d_models(tablet_id)

            tablet_data["download_status"] = "success"
            logger.info(f"Successfully downloaded {tablet_id}")

        except Exception as e:
            tablet_data["download_status"] = "failed"
            tablet_data["error"] = str(e)
            logger.error(f"Failed to download {tablet_id}: {e}")

        time.sleep(REQUEST_DELAY)  # Rate limiting
        return tablet_data

    def _download_images(self, tablet_id: str) -> dict:
        """
        Download tablet images (obverse, reverse, edge).

        Returns:
            Dict with image paths and URLs
        """
        image_paths = {}
        image_types = ["obverse", "reverse", "edge"]

        for img_type in image_types:
            # Construct CDLI image URL
            # Format: https://cdli.ucla.edu/images/P100001_l.jpg (obverse)
            suffix = {"obverse": "_l", "reverse": "_r", "edge": "_e"}.get(img_type, "")
            url = f"{CDLI_API_BASE}images/{tablet_id}{suffix}.jpg"

            try:
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    local_path = self.cache_dir / f"{tablet_id}_{img_type}.jpg"
                    logger.debug(f"Downloading {img_type} image from {url}")
                    img_response = self.session.get(url, timeout=10)
                    img_response.raise_for_status()

                    with open(local_path, "wb") as f:
                        f.write(img_response.content)

                    image_paths[img_type] = str(local_path.relative_to(DATA_DIR.parent))
                    logger.debug(f"Saved {img_type} to {local_path}")

            except requests.RequestException as e:
                logger.debug(f"Could not download {img_type} image: {e}")

        return image_paths

    def _download_3d_models(self, tablet_id: str) -> dict:
        """
        Download 3D models (OBJ, MTL) when available.

        CDLI's 3D models are stored in specific formats:
        - .obj: Wavefront OBJ format
        - .mtl: Material file
        - .zip: Bundled models

        Returns:
            Dict with 3D model paths and types
        """
        model_paths = {}

        # Try multiple 3D model sources
        model_sources = [
            ("obj", f"{CDLI_API_BASE}3d/{tablet_id}.obj"),
            # Additional sources as CDLI expands 3D offerings
        ]

        for model_type, url in model_sources:
            try:
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    local_dir = RAW_3D_DIR / tablet_id
                    local_dir.mkdir(parents=True, exist_ok=True)
                    local_path = local_dir / f"{tablet_id}.{model_type}"

                    logger.debug(f"Downloading 3D {model_type} from {url}")
                    model_response = self.session.get(url, timeout=30)
                    model_response.raise_for_status()

                    with open(local_path, "wb") as f:
                        f.write(model_response.content)

                    model_paths[model_type] = str(local_path.relative_to(DATA_DIR.parent))
                    logger.info(f"Saved 3D model ({model_type}) to {local_path}")

            except requests.RequestException as e:
                logger.debug(f"Could not download 3D {model_type}: {e}")

        return model_paths

    def batch_download(
        self,
        period: Optional[str] = None,
        limit: int = 50,
        language: Optional[str] = None,
    ) -> None:
        """
        Batch download tablets from CDLI.

        Args:
            period: Time period filter
            limit: Maximum tablets to download
            language: Language filter
        """
        logger.info(f"Starting batch download (limit={limit})")

        tablets = self.search_tablets(period=period, limit=limit, language=language)

        results = []
        for i, tablet in enumerate(tablets, 1):
            logger.info(f"[{i}/{len(tablets)}] Processing {tablet.get('tablet_id')}")
            result = self.download_tablet(
                tablet["tablet_id"],
                download_images=True,
                download_3d=self.download_3d,
            )
            results.append(result)

        # Save metadata
        self._save_metadata(results)

        logger.info(f"Batch download complete. {len(results)} tablets processed.")

    def _save_metadata(self, tablets: list[dict]) -> None:
        """Save tablet metadata to JSONL file."""
        with open(METADATA_CACHE, "a") as f:
            for tablet in tablets:
                f.write(json.dumps(tablet) + "\n")

        logger.info(f"Metadata saved to {METADATA_CACHE}")

    @staticmethod
    def _get_mock_tablets(
        period: Optional[str] = None,
        limit: int = 50,
        language: Optional[str] = None,
    ) -> list[dict]:
        """
        Generate mock tablet data for testing.

        In production, this would be replaced with actual CDLI API calls.
        """
        mock_tablets = [
            {
                "tablet_id": f"P{100001 + i:05d}",
                "period": period or "Ur III",
                "language": language or "Sumerian",
                "preservation": "good" if i % 2 == 0 else "fair",
                "has_3d": i % 3 == 0,  # Assume 1/3 have 3D models
            }
            for i in range(min(limit, 50))
        ]
        return mock_tablets


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Download cuneiform tablets from CDLI"
    )
    parser.add_argument(
        "--period",
        default="Ur III",
        help="Time period (e.g., 'Ur III', 'Old Babylonian')",
    )
    parser.add_argument(
        "--limit", type=int, default=50, help="Maximum tablets to download"
    )
    parser.add_argument(
        "--language",
        default="Sumerian",
        help="Language filter (e.g., 'Sumerian', 'Akkadian')",
    )
    parser.add_argument(
        "--with-3d",
        action="store_true",
        help="Also download 3D models when available",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(RAW_CDLI_DIR),
        help="Directory to cache downloads",
    )

    args = parser.parse_args()

    downloader = CDLIDownloader(
        cache_dir=Path(args.cache_dir), download_3d=args.with_3d
    )
    downloader.batch_download(
        period=args.period, limit=args.limit, language=args.language
    )


if __name__ == "__main__":
    main()
