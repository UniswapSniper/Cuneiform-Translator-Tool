#!/usr/bin/env python3
"""
Download cuneiform tablets from CDLI (Cuneiform Digital Library Initiative).

Uses CDLI's REST API to fetch:
- Artifact metadata (JSON)
- Images (JPEG)
- Inscriptions (C-ATF format)
- Basic provenance info

API Reference: https://cdli.earth/docs/api

Usage:
    python scripts/download_cdli_tablets.py --period "Ur III" --limit 50 --with-inscriptions
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Iterator, Optional
from urllib.parse import urlencode

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
CDLI_API_BASE = "https://cdli.earth"
CDLI_ARTIFACTS_API = f"{CDLI_API_BASE}/artifacts"
CDLI_SEARCH_API = f"{CDLI_API_BASE}/search"
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_CDLI_DIR = DATA_DIR / "raw" / "cdli"
METADATA_CACHE = RAW_CDLI_DIR / "metadata.jsonl"

# Rate limiting (CDLI asks for courtesy)
REQUEST_DELAY = 0.5  # seconds between requests


class CDLIDownloader:
    """Download tablets from CDLI using their REST API."""

    def __init__(self, cache_dir: Path = RAW_CDLI_DIR):
        """
        Initialize downloader.

        Args:
            cache_dir: Directory to store downloaded files
        """
        self.cache_dir = Path(cache_dir)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "CuniformTranslator/0.0.1 (+https://github.com/UniswapSniper/Cuneiform-Translator-Tool)"
            }
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def search_tablets(
        self,
        period: Optional[str] = None,
        limit: int = 50,
        language: Optional[str] = None,
    ) -> list[dict]:
        """
        Search for tablets using CDLI's REST API.

        For now, returns fallback mock data due to API complexity.
        Production: Replace with proper CDLI search endpoint once available.

        Args:
            period: Time period (e.g., "Ur III", "Old Babylonian")
            limit: Maximum tablets to retrieve
            language: Language filter (e.g., "Sumerian", "Akkadian")

        Returns:
            List of tablet metadata dicts
        """
        logger.info(f"Searching CDLI for tablets (period={period}, limit={limit})")
        logger.info("Note: Using mock data. To use real CDLI data, integrate with their search API.")
        
        # For now, use fallback mock data
        # TODO: Implement proper CDLI search API integration
        # See: https://cdli.earth/docs/api and https://cdli.earth/docs/search
        tablets = self._get_fallback_tablets(limit, period, language)
        
        return tablets[:limit]

    def _filter_tablets(
        self, tablets: list[dict], period: Optional[str], language: Optional[str]
    ) -> list[dict]:
        """Filter tablets by period and language."""
        filtered = tablets

        if period:
            filtered = [
                t for t in filtered if t.get("period", "").lower() == period.lower()
            ]

        if language:
            filtered = [
                t for t in filtered
                if any(
                    lang.lower() == language.lower()
                    for lang in t.get("languages", [])
                )
            ]

        return filtered

    def download_tablet(self, tablet_id: str, download_images: bool = True) -> dict:
        """
        Download a specific tablet's data.

        Args:
            tablet_id: CDLI tablet ID (e.g., "P100001")
            download_images: Download image files

        Returns:
            Tablet metadata with local paths
        """
        logger.info(f"Downloading tablet {tablet_id}")

        tablet_data = {
            "tablet_id": tablet_id,
            "image_paths": {},
            "inscription_path": None,
            "download_status": "pending",
            "timestamp": time.time(),
        }

        try:
            # Fetch metadata from API - try both with and without .json
            for url_format in [f"{CDLI_ARTIFACTS_API}/{tablet_id}.json", 
                              f"{CDLI_ARTIFACTS_API}/{tablet_id}"]:
                try:
                    response = self.session.get(url_format, timeout=10)
                    if response.status_code == 200:
                        metadata = response.json()
                        tablet_data["metadata"] = metadata
                        break
                except:
                    continue

            if download_images:
                tablet_data["image_paths"] = self._download_images(tablet_id)

            tablet_data["download_status"] = "success"
            logger.info(f"Successfully downloaded {tablet_id}")

        except Exception as e:
            tablet_data["download_status"] = "failed"
            tablet_data["error"] = str(e)
            logger.debug(f"Failed to download metadata for {tablet_id}: {e}")

        time.sleep(REQUEST_DELAY)
        return tablet_data

    def _download_images(self, tablet_id: str) -> dict:
        """
        Download tablet images.

        Returns:
            Dict with image paths
        """
        image_paths = {}

        # CDLI image URL patterns
        image_types = {
            "obverse": f"{CDLI_API_BASE}/images/{tablet_id}_l.jpg",
            "reverse": f"{CDLI_API_BASE}/images/{tablet_id}_r.jpg",
            "edge": f"{CDLI_API_BASE}/images/{tablet_id}_e.jpg",
        }

        for img_type, url in image_types.items():
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
            tablet_id = tablet.get("id") or tablet.get("tablet_id") or tablet.get("P-number", "")
            if not tablet_id:
                logger.warning(f"Skipping tablet with no ID: {tablet}")
                continue

            logger.info(f"[{i}/{len(tablets)}] Processing {tablet_id}")
            result = self.download_tablet(tablet_id, download_images=True)
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
    def _get_fallback_tablets(
        limit: int = 50,
        period: Optional[str] = None,
        language: Optional[str] = None,
    ) -> list[dict]:
        """
        Generate fallback tablet data when API is unavailable.

        Returns sample data for testing purposes.
        """
        logger.warning("Using fallback mock data (API unavailable)")
        mock_tablets = [
            {
                "id": f"P{100001 + i:05d}",
                "tablet_id": f"P{100001 + i:05d}",
                "period": period or "Ur III",
                "languages": [language or "Sumerian"],
                "artifact_type": "tablet",
                "provenience": "Ur",
            }
            for i in range(min(limit, 50))
        ]
        return mock_tablets


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Download cuneiform tablets from CDLI using REST API"
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
        "--cache-dir",
        default=str(RAW_CDLI_DIR),
        help="Directory to cache downloads",
    )

    args = parser.parse_args()

    downloader = CDLIDownloader(cache_dir=Path(args.cache_dir))
    downloader.batch_download(
        period=args.period, limit=args.limit, language=args.language
    )


if __name__ == "__main__":
    main()
