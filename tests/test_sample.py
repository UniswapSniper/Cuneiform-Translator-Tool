"""
Test for tablet record loading and validation.
"""

import json
import pathlib

def test_sample_tablet_loads():
    """Verify sample tablet JSON is valid."""
    sample_path = pathlib.Path(__file__).parent.parent / "data/processed/sample_tablet_record.json"
    with open(sample_path) as f:
        tablet = json.load(f)
    
    assert tablet["tablet_id"] == "sample_001"
    assert len(tablet["regions"]) > 0
    assert tablet["regions"][0]["transliteration"] == "ra"
    print("✓ Sample tablet loaded successfully")

if __name__ == "__main__":
    test_sample_tablet_loads()
