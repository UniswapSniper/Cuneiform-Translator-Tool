# Project Roadmap

## Vision

Build an open-source pipeline to digitize, annotate, and translate ancient cuneiform tablets at scale, leveraging both human expertise and machine learning.

---

## Phases & Milestones

### M0: MVP Foundation (Current — Jan/Feb 2026)

**Goal:** Establish the data pipeline, annotation schema, and test infrastructure.

#### Deliverables
- [x] Project structure & package setup
- [x] Annotation format specification (JSON schema)
- [x] Data provenance tracking (CDLI, ORACC)
- [x] Sample tablet record for testing
- [x] Development environment (uv/pip, venv)
- [x] Basic test suite
- [ ] CDLI download script (metadata + photos + 3D models)
- [ ] 3D rendering extraction pipeline (GigaMesh integration)
- [ ] Git hooks & CI/CD (linting, tests)
- [ ] Data pipeline directory structure (raw → processed)

#### Acceptance criteria
- All unit tests pass
- Code passes `black`, `isort`, `ruff`, `mypy`
- Sample tablet loads and validates correctly
- Documentation complete for each module

---

### M1: Enhanced Annotation (Feb/Mar 2026)

**Goal:** Build annotation tools and establish data quality standards.

#### Deliverables
- [ ] Annotation CLI tool
  - Load tablet image + metadata
  - Draw regions on tablet
  - Input transliterations
  - Save/validate records
- [ ] Batch import from CDLI
  - Fetch metadata & images
  - Generate baseline regions
  - Seed sign candidates
- [ ] Data quality checks
  - Overlapping region detection
  - Coordinate bounds validation
  - Transliteration normalization
- [ ] Inter-annotator agreement (IAA) metrics
  - Fleiss' kappa for categorical regions
  - Edit distance for transliterations
  - Agreement reports & dashboards

#### Acceptance criteria
- Can annotate a full tablet (image → regions → transliterations → save)
- Can import 100+ tablets from CDLI
- IAA metrics calculated for test set
- Documentation updated

---

### M2: Machine Learning Infrastructure (Mar/Apr 2026)

**Goal:** Add vision and NLP models for semi-automated translation.

#### Deliverables
- [ ] Vision module enhancements
  - YOLOv8 for sign region localization (baseline)
  - RepPoints detector for advanced sign detection (Stötzner et al. architecture)
  - Multi-image fusion (photos + 3D renderings)
  - Sign candidate ranking & confidence scores
  - Post-processing (NMS, filtering)
- [ ] Transliteration RNN/Transformer
  - Sequence labeling model (BIO tagging)
  - Lexicon-aware beam search decoding
  - Cross-validation on ORACC corpus
- [ ] Model evaluation
  - Character error rate (CER), word error rate (WER)
  - Inter-model agreement
  - Benchmark datasets & leaderboards
- [ ] Integration with annotation tool
  - Offer ML predictions in UI
  - Allow rapid human review & correction
  - Retrain on human feedback (v2)

#### Acceptance criteria
- Sign recognition model achieves >85% top-1 accuracy on test set
- Transliteration model achieves <15% CER
- UI shows predictions alongside manual controls
- Retraining pipeline documented

---

### M3: Web UI & Community (Apr/May 2026)

**Goal:** Public-facing interface for annotation, review, and translation.

#### Deliverables
- [ ] Streamlit web app
  - Image upload & region drawing
  - Multi-user annotation with login
  - Real-time IAA tracking
  - Leaderboard for contributors
- [ ] API server
  - REST endpoints for tablet CRUD
  - Batch annotation jobs
  - Model inference API
- [ ] Community features
  - Issue/discussion board for ambiguous cases
  - Contributor guidelines & attribution
  - Data export (JSONL, CSV)

#### Acceptance criteria
- Web UI accessible & usable by non-technical users
- API responds to 100+ concurrent requests
- Documentation for contributors
- Community users can export annotated data

---

### M4: English Glossing (May/Jun 2026)

**Goal:** Add optional English translation layer.

#### Deliverables
- [ ] Historical English gloss corpus
  - Curate lexical database (Sumerian → English)
  - Map to sign lexicon
  - Handle polysemy & context
- [ ] Gloss model
  - Context-aware word embedding
  - Gloss ranking for transliterations
  - Confidence scoring
- [ ] Integration
  - Add gloss field to annotation schema
  - Gloss predictions in UI
  - Gloss validation & benchmarking

#### Acceptance criteria
- Gloss predictions available for 90%+ of transliteration tokens
- Benchmark gloss accuracy on gold standard
- Schema backward-compatible with M2 annotations

---

### M5: Production & Scale (Jun+ 2026)

**Goal:** Hardened production system, large-scale ingestion, public release.

#### Deliverables
- [ ] Performance optimization
  - Model quantization (int8, pruning)
  - Batch inference pipeline
  - Caching & CDN for images
- [ ] Data management
  - DVC integration for large datasets
  - Automated backups & archiving
  - Data lineage tracking
- [ ] Scalability
  - Kubernetes deployment (optional)
  - Load balancing for API
  - Async job queues (Celery)
- [ ] Public release
  - GitHub publication with cleanup
  - Academic paper / preprint
  - Benchmark leaderboard
  - User survey & feedback

#### Acceptance criteria
- System handles 1M+ tablets
- <100ms inference per tablet
- >95% uptime SLA
- Public dataset & models available under CC0/MIT

---

## Open questions & future directions

### Near-term (M1/M2)
- Should we pre-segment tablets or let annotators draw regions?
- How to handle multi-language tablets (Sumerian + Akkadian)?
- Real-time collaboration in annotation tool?

### Medium-term (M3/M4)
- Should we integrate with ORACC's web API for live validation?
- Multi-modal embeddings (image + text)?
- Unsupervised sign clustering to discover new signs?

### Long-term (M5+)
- Historical language change & diachronic models?
- Cross-cultural sign borrowing (Egyptian, Hittite)?
- Tablet reconstruction (filling damaged areas)?
- Interactive story browser (linked tablets)?

---

## Milestones by date

| Milestone | Target date | Status |
|-----------|-------------|--------|
| M0: MVP Foundation | Jan 31, 2026 | 🚧 In progress |
| M1: Enhanced Annotation | Mar 15, 2026 | ⏳ Pending |
| M2: ML Infrastructure | Apr 30, 2026 | ⏳ Pending |
| M3: Web UI & Community | May 31, 2026 | ⏳ Pending |
| M4: English Glossing | Jun 30, 2026 | ⏳ Pending |
| M5: Production & Scale | Jul 31, 2026+ | ⏳ Pending |

---

## Dependency graph

```
M0 (Foundation)
  ↓
M1 (Annotation tools)
  ↓
M2 (ML models) ← Can start in parallel with M1b
  ↓
M3 (Web UI) ← Depends on M1 + M2
  ↓
M4 (Glossing) ← Depends on M2 + M3
  ↓
M5 (Production) ← Depends on M3 + M4
```

---

## Key metrics

### Data quality
- Annotation coverage: tablets with ≥2 annotators
- Inter-annotator agreement (Fleiss' kappa): >0.80 for sign identity
- Transliteration error rate: <5% (manual review)

### Model performance
- Sign recognition accuracy: >85% (top-1)
- Character error rate (transliteration): <15%
- Gloss accuracy: >70% (on polysemous words)

### Community
- Active contributors: >10
- Tablets annotated: >10k
- Community-sourced issues resolved: >80%

---

## Known risks & mitigation

| Risk | Likelihood | Impact | Mitigation |, use downloads |
| 3D model availability | Medium | Limited training data | Prioritize tablets with both photos + 3D; use photo-only fallback |
| Model overfitting on Ur III texts | Medium | Poor generalization | Use diverse periods from ORACC + multiple languages |
| Annotator fatigue | Medium | Quality degradation | Rotate annotators, limit sessions |
| GigaMesh dependency | Low | Rendering pipeline failure | Keep fallback to raw 3D modelse periods from ORACC |
| Annotator fatigue | Medium | Quality degradation | Rotate annotators, limit sessions |
| Licensing complications | Low | Legal blockers | Vet all data sources upfront |
| Community drop-off | Medium | Incomplete annotations | Gamification, leaderboards, credits |

---

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup.

- **Data annotation:** Start with M1 tools (coming soon)
- **ML engineering:** Help with vision/NLP models (M2)
- **Web development:** UI/UX work (M3)
- **Scholarly input:** Validate transliterations, lexicon building (M4)
- **DevOps:** Infrastructure & deployment (M5)

---

Last updated: 2026-01-21
