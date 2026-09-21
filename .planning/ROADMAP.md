# ROADMAP — Health-Hugo Enriched Content System

## Overview

4-phase plan over 4 weeks. All phases are additive (non-destructive) to current pipeline. Each phase has a dry-run gate before proceeding.

## Phase 1: Foundation (Week 1)

**Goal**: Ingredient DB + keyword mapping + health enricher module

### Tasks

| Task | Description | Depends | Est. |
|------|-------------|---------|------|
| T1.1 | Design ingredient DB schema | None | 0.5d |
| T1.2 | Seed DB from 식약처 public API | T1.1 | 1d |
| T1.3 | Build keyword→condition mapping config | None | 0.5d |
| T1.4 | Create `health_enricher.py` | T1.2, T1.3 | 1d |
| T1.5 | Integrate into pipeline (collector → enricher → health_enricher) | T1.4 | 0.5d |
| T1.6 | Dry-run: generate 3 articles with enrichment data | T1.5 | 1d |

### Deliverables
- `data/health_ingredients.db` — SQLite with seeded ingredients
- `config/prompts/health_conditions.yaml` — keyword mapping
- `pipelines/curation/health_enricher.py` — new module
- Pipeline flow updated to call health_enricher

### Gate Criteria
- [ ] ≥50% health-hugo keywords have ingredient data
- [ ] 3 dry-run articles contain enrichment sections
- [ ] No pipeline regression (existing articles still generate)

### Risk
- 식약처 API quota or format changes → fallback to manual seeding

---

## Phase 2: Output Enhancement (Week 2)

**Goal**: Post-processor + section rotation + situational matching + claim compliance

### Tasks

| Task | Description | Depends | Est. |
|------|-------------|---------|------|
| T2.1 | Design enrichment section templates | T1.6 | 0.5d |
| T2.2 | Build `health_post_processor.py` | T1.6, T2.1 | 1.5d |
| T2.3 | Implement section rotation logic | T2.2 | 0.5d |
| T2.4 | Implement Condition×Persona matcher | T1.3, T2.2 | 0.5d |
| T2.5 | Health claim compliance filter | T2.2 | 0.5d |
| T2.6 | Register new H2 patterns in `_ALLOWED_H2_PATTERNS` | T2.1 | 0.5d |
| T2.7 | Dry-run: 5 articles with rotation | T2.2-T2.6 | 1d |

### Deliverables
- `pipelines/curation/health_post_processor.py` — new module
- `shared/hugo_writer.py` — updated `_ALLOWED_H2_PATTERNS` with new H2
- Rotation logic (deterministic, hash-based)
- Health claim compliance filter

### Gate Criteria
- [ ] 5 dry-run articles show different section orders
- [ ] Each article has 2-3 enrichment sections
- [ ] Zero efficacy claim violations
- [ ] All enrichment H2 patterns in `_ALLOWED_H2_PATTERNS`

### Risk
- New H2 patterns conflict with existing → validate with H2-GUARD test

---

## Phase 3: Quality & Anti-Automation (Week 3)

**Goal**: Review system, variation mechanics, quality gates

### Tasks

| Task | Description | Depends | Est. |
|------|-------------|---------|------|
| T3.1 | Implement hybrid review template | T2.7 | 0.5d |
| T3.2 | Real data injection into product blocks | T2.7 | 0.5d |
| T3.3 | A/B dry-run (3 variants × 3 articles) | T3.1, T3.2 | 1d |
| T3.4 | Quality checklist entries for health-hugo | T3.3 | 0.5d |
| T3.5 | Automated health claim scan | T2.5, T3.4 | 0.5d |
| T3.6 | Full quality audit | T3.5 | 1d |

### Deliverables
- Enhanced product block template with real data
- A/B dry-run results
- Updated `config/quality_checklist.yaml` (health-hugo section)
- Automated health claim validation script

### Gate Criteria
- [ ] A/B dry-run shows measurable improvement
- [ ] Quality checklist: health-hugo 100% PASS
- [ ] 0 hallucinations on ingredient/dosage data
- [ ] Content length 2500-3500 chars maintained

### Risk
- A/B results inconclusive → increase variant count or sample size

---

## Phase 4: Rollout & Monitoring (Week 4)

**Goal**: Deploy, monitor, expand

### Tasks

| Task | Description | Depends | Est. |
|------|-------------|---------|------|
| T4.1 | Deploy to health-hugo pipeline | T3.6 | 0.5d |
| T4.2 | Monitor first 5 published articles | T4.1 | 1d |
| T4.3 | Metrics dashboard (length, violations, rotation entropy) | T4.2 | 0.5d |
| T4.4 | Expand to beauty-hugo / fitness-hugo | T4.3 | 2d |
| T4.5 | Documentation & handoff | T4.4 | 0.5d |

### Deliverables
- health-hugo producing enriched content via live pipeline
- Monitoring metrics operational
- beauty-hugo / fitness-hugo enrichment framework adapted
- Project documentation complete

### Gate Criteria
- [ ] Live articles publish successfully
- [ ] Monitoring metrics within targets (0 violations, 2500-3500 chars)
- [ ] beauty-hugo / fitness-hugo enrichment configured
- [ ] Rollback plan documented

### Risk
- Live violations detected → immediate rollback to Phase 2 config

---

## Summary Timeline

```
Week 1: [Phase 1] ━━━━━━━━━━━━ Foundation (DB + Mapper + Enricher)
Week 2: [Phase 2] ━━━━━━━━━━━━ Enhancement (Post-processor + Rotation)
Week 3: [Phase 3] ━━━━━━━━━━━━ Quality (A/B + Audit + Gates)
Week 4: [Phase 4] ━━━━━━━━━━━━ Rollout (Deploy + Monitor + Expand)
```

## Dependencies

```
Phase 1 → Phase 2 → Phase 3 → Phase 4
  ↓         ↓         ↓         ↓
 DB     Post-    Quality   Live
 Schema Processor  Gates    Content
```

Each phase requires prior phase's gate criteria to be met.
No parallel phases — sequential dependency chain.