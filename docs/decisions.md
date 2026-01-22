# Project decisions

Record major technical, dataset, and process decisions here for future reference.

## Decision template
```
### Decision: [short title]
Date: YYYY-MM-DD
Context: [why this decision was needed]
Options: [options considered]
Chosen: [what was decided]
Rationale: [why]
Status: active | superseded
```

## Decisions

### Decision: Start with annotation MVP before ML
Date: 2026-01-21
Context: Many similar projects fail by jumping to models without clean data or eval infrastructure.
Options:
  1. Build ML models first (faster early results, but risky)
  2. Build annotation + data pipeline first, then models
Chosen: Option 2
Rationale: Reproducible data + clear evaluation metrics are prerequisites for meaningful ML.
Status: active

### Decision: Use public CDLI + ORACC datasets
Date: 2026-01-21
Context: Need authoritative, well-documented cuneiform data to start.
Options:
  1. Crowd-source new annotations (slow, but novel)
  2. Use existing CDLI/ORACC (fast, already vetted)
  3. Hybrid (use CDLI/ORACC as seed, extend with community)
Chosen: Option 2 initially, transition to Option 3 later
Rationale: Faster launch, proven methodology, avoids licensing headaches.
Status: active

### Decision: Store annotations in git (with size limits)
Date: 2026-01-21
Context: Need version control + collaboration for annotations.
Options:
  1. Git (simple, familiar)
  2. DVC (better for large data, overkill early)
  3. Database + API (adds complexity)
Chosen: Option 1 (git) for < 100MB, revisit if it grows
Rationale: Simplicity for now; upgrade to DVC if needed.
Status: active
