# Health-Hugo Content Enrichment Project

## Project Overview

**Goal**: Transform health-hugo (health.informationhot.kr) from template-feeling curation posts to enriched, human-like content with problem/solution framing, situational matching, and varied structures — while preserving CUAP pipeline compatibility.

**Target Blog**: health-hugo (CUAP pipeline, curation type)
- Domain: health.informationhot.kr
- Pipeline: `pipelines/curation/` (shared with 14 other CUAP blogs)
- Schedule: 5 posts/day at 07:10, 10:50, 14:15, 18:00, 21:25
- Publisher: ca-pub-6677996696534146 (informationhot 계열)

## Current State Analysis

### Data Flow (Current)
```
Coupang API → collector.py → enricher.py (parse_specs + Naver Shopping) → writer.py → Hugo → Deploy
```

### Coupang API Returns (search_products)
- productId, productName, productPrice, productImage, productUrl
- categoryName, keyword, rank, isRocket, isFreeShipping
- **MISSING**: Nutritional info, ingredients, dosage, form (rTG/EE), EPA/DHA amounts, capsule count, origin

### Enricher Adds (enricher.py)
- `parsed_specs`: Regex extraction from product_name (e.g., "1040mg" → spec)
- `brand`/`maker`: Via Naver Shopping API (top 5 products only)
- `naver_lprice`, `naver_mall`: Price comparison data

### Writer Uses for health-hugo
- product_name, brand/maker, price, category, rocket/free_shipping, rank
- parsed_specs, product_url, product_image, naver_lprice

### Health-Hugo Rules REQUIRE but MISSING (writer.py lines 107-122)
| Required Field | Current Status |
|---|---|
| 주성분명과 함량(mg/mcg/IU) | ❌ Only partial from product_name regex |
| 복용 대상(연령/성별/건강상태) 구체적 생활장면 | ❌ Not in data |
| 섭취방법(1일 몇회 몇정) | ❌ Not in data |
| 성분 형태(rTG vs EE) | ❌ Not in data |
| EPA/DHA 별도 함량 | ❌ Not in data |
| 원료 원산지 | ❌ Not in data |
| 캡슐 크기/목넘김 | ❌ Not in data |

### Unused Available Data
- Naver Shopping `brand`/`maker` (only top 5 products)
- `naver_lprice` for price comparison messaging
- `isRocket`/`isFreeShipping` for delivery context
- `rank` as popularity signal

## User Requirements (From Deep Questioning)

### 1. Structure: Hybrid — Core Sections Fixed, Variable Order
- Keep CUAP 5-section structure (intro, 비교표, 상세비교, 체크리스트, 마무리)
- Add enrichment sub-sections with **rotating order** per post
- Enrichment sub-sections: `실제 후기`, `성분 분석`, `가격 비교`, `복용 가이드`, `상황별 추천`

### 2. Review Sourcing: Hybrid Templates + Real Data Points
- Structured review templates with variables filled from actual product data
- Variables: price, specs (mg, form), delivery (rocket/free), rank, naver_lprice
- No scraping — use template patterns with real data injection

### 3. Situational Matching: Condition × Persona Matrix
- Cross product of health need × user profile = targeted recommendation
- Health conditions: 눈 피로, 장 건강, 면역력, 혈행 개선, 관절 건강, 수면/스트레스
- Personas: 30대 직장인(야근 잦음), 40대 주부, 50대 부모님, 임신 준비 여성, 운동하는 20대, 수험생

### 4. Enrichment Point: Both Pre + Post Processing
- **Pre**: Enrich product data with structured fields before writer
- **Post**: Enhance generated content with reviews, scenarios, comparisons

## Technical Architecture

### New Components Needed

```
enricher.py (extended) → health_enricher.py (new)
    ↓
writer.py (extended) → health_writer.py (new) OR pre/post processors
    ↓
post_processor.py (new) — injects reviews, scenarios, rotations
```

### Data Models to Add

```python
# Health supplement structured data
HealthSupplement = {
    "main_ingredients": [{"name": "EPA", "amount": "500mg", "unit": "mg"}],
    "ingredient_form": "rTG",  # rTG, EE, TG, PL
    "dosage": {"daily_count": 2, "per_count": 1, "timing": "식후"},
    "target_conditions": ["혈행개선", "눈건강"],
    "target_personas": ["야근 잦은 30대 직장인", "컴퓨터 작업 많은 40대"],
    "capsule_info": {"size": "중", "swallow_ease": "보통"},
    "origin": "노르웨이",
    "price_per_day": 1200,  # calculated
}
```

### Enrichment Sources

| Source | What It Provides | Integration Method |
|---|---|---|
| Coupang product_name | Partial specs via regex | Already in enricher.py |
| Naver Shopping API | Brand, maker, naver_lprice, mall | Already in enricher.py (top 5) |
| **NEW: Ingredient DB** | Standardized ingredient profiles | Local JSON/DB lookup by product_name keywords |
| **NEW: Dosage patterns** | Common dosage by supplement type | Rule-based mapping |
| **NEW: Condition mapping** | Ingredient → health condition | Knowledge base |
| **NEW: Persona templates** | Condition × persona → scenario text | Template library |

## Anti-Automation Strategy

### Structure Rotation
- 5 core H2s fixed (CUAP compliance)
- 5 enrichment sub-sections → pick 2-3 per post, rotate order
- Example rotations:
  - Post A: 비교표 → 성분분석 → 상세비교 → 실제후기 → 체크리스트 → 복용가이드 → 마무리
  - Post B: 비교표 → 상세비교 → 상황별추천 → 체크리스트 → 가격비교 → 마무리
  - Post C: 비교표 → 복용가이드 → 상세비교 → 실제후기 → 가격비교 → 체크리스트 → 마무리

### Tone Variation
- 3 tone presets: 전문적/정보전달, 친근한/공감형, 분석적/비교중심
- Rotate per post, avoid repetition within 7 days

### Real Data Injection
- Every claim tied to actual product data field
- No hallucinated review scores, sales numbers
- Price comparisons use real naver_lprice vs Coupang price

## Acceptance Criteria

- [ ] Health-hugo posts pass CUAP quality gate (2500-3500 chars, H2 count, no banned phrases)
- [ ] Each post includes ≥2 enrichment sub-sections from pool of 5
- [ ] Situational matching: condition × persona matrix evident in 상세비교 section
- [ ] Review templates use real data points (price, specs, delivery, rank)
- [ ] No "추천 대상:", "페르소나:" labels (CUAP rule)
- [ ] 건강기능식품 표시광고 규칙 준수 (no efficacy claims)
- [ ] Structure rotation: no identical sub-section order within 7 days
- [ ] Pipeline integration: zero breaking changes to existing CUAP blogs

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Breaking existing CUAP blogs | Additive changes only; health-hugo specific code paths |
| Ingredient data accuracy | Fail-open: if ingredient DB lookup fails, skip enrichment section |
| Content length explosion | Enrichment sections capped at 300 chars each; total 3500 char hard limit |
| AdSense compliance | No changes to ad placement; Publisher ID unchanged (6677) |
| Hugo build failures | Dry-run validation before deploy; H2-GUARD patterns updated |

## Next Steps

1. Create detailed SPEC.md with exact data models, enrichment logic, rotation algorithms
2. Build health_enricher.py with ingredient DB, condition mapping, persona templates
3. Build post_processor.py for review injection, structure rotation, tone variation
4. Integrate into pipeline.py with health-hugo conditional routing
5. A/B dry-run with quality checklist validation
6. Deploy to health-hugo only, monitor for 7 days