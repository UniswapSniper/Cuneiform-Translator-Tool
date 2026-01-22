# CDLI REST API Integration Guide

## Status

**Current:** Fallback to mock data (placeholder implementation)  
**Next:** Real CDLI REST API integration

## CDLI API Documentation

- **Main docs:** https://cdli.earth/docs/api
- **Search guide:** https://cdli.earth/docs/search
- **Base URL:** `https://cdli.earth`

## Available Endpoints

### Metadata (JSON)
```
GET /artifacts/P000001.json         # Single artifact
GET /artifacts/                     # List (with query params)
```

### Other formats
- CSV/TSV/Excel: `/artifacts/` with format query param
- RDF/Linked Data: `/artifacts/P000001.rdf`
- Inscriptions: `/artifacts/P000001/inscription/` (C-ATF, CDLI-CoNLL)

## How to Integrate Real API

### Step 1: Query Search Endpoint
```python
# Search for tablets by period/language
url = "https://cdli.earth/search"
params = {
    "period": "Ur III",
    "language": "Sumerian",
    "offset": 0,
    "limit": 100
}
```

### Step 2: Extract P-numbers from Results
```python
# Parse search results to get P-numbers (artifact IDs)
# Example: P100001, P100002, etc.
```

### Step 3: Fetch Individual Artifacts
```python
# Once you have P-numbers, fetch metadata
url = f"https://cdli.earth/artifacts/{p_number}.json"
response = requests.get(url)
metadata = response.json()
```

### Step 4: Download Images
```python
# Images available at standard URLs
obverse = f"https://cdli.earth/images/{p_number}_l.jpg"
reverse = f"https://cdli.earth/images/{p_number}_r.jpg"
edge = f"https://cdli.earth/images/{p_number}_e.jpg"
```

## Code Stub for Real Implementation

```python
def search_tablets_via_api(period, language, limit):
    """Fetch real tablet list from CDLI."""
    url = f"{CDLI_API_BASE}/search/advanced"
    
    params = {
        "period": period,
        "language": language,
        "limit": limit,
    }
    
    # Different endpoint for CSV/JSON export?
    # Try: https://cdli.earth/artifacts?period=Ur%20III&format=json
    
    response = requests.get(url, params=params, timeout=10)
    return parse_results(response)
```

## Known Issues

1. **CDLI API Response Format**: Varies depending on endpoint/format
   - Solution: Test with actual requests, handle multiple response types

2. **Large Dataset**: 500k+ tablets
   - Solution: Use pagination (offset/limit)
   - Consider download full CSV snapshot if available

3. **Rate Limiting**: 0.5s delay between requests
   - May need adjustment based on CDLI's actual limits

## Future: Bulk Download

CDLI may provide:
- SQLite database snapshot
- CSV export of all metadata
- Git repository with data files

Check: https://github.com/cdli-data (if accessible) or contact cdli@ames.ox.ac.uk

## Testing Real Integration

Once implemented, test with:
```bash
python scripts/download_cdli_tablets.py --period "Ur III" --limit 100
```

Should fetch real tablet P-numbers and metadata instead of mock data.
