# REQUIREMENTS — Health-Hugo Enriched Content System

## Problem Statement

health-hugo (pet.informationhot.kr) publishes health/supplement comparison articles via CUAP curation pipeline. Current content is template-feel, lacks real user context, and has weak situational matching. Health-specific requirements (ingredients, dosage, conditions) from `BLOG_EXTRA_RULES` in `writer.py` are specified but NOT met because data sources don't provide them.

## Goals

1. **Enriched content**: Every article addresses a specific health problem → products as solutions
2. **Anti-automation**: Hybrid structure rotation + tone variation + real data injection
3. **All data sources**: Coupang API, Naver Shopping, review scraping, ingredient DB, price history
4. **Incremental**: Augment current pipeline with pre/post processors, NOT rewrite
5. **CUAP spec compliant**: All output passes through existing Hugo pipeline → publish

## Functional Requirements

### R1: Problem/Solution Framing
- **Priority**: Must Have
- **Description**: Articles open with a health problem statement, position products as solutions
- **Data**: Keyword → Condition mapping (config)
- **Validation**: Intro section contains problem framing sentence + keyword condition match

### R2: Condition × Persona Matrix
- **Priority**: Must Have
- **Description**: Each product recommendation tied to (health condition × user persona) pair
- **Data**: Config-based matrix; 5 conditions × 3 personas minimum
- **Validation**: Article contains ≥2 persona×condition statements per post

### R3: Varied Content Structures
- **Priority**: Must Have
- **Description**: Core 5 CUAP sections fixed; enrichment sub-sections rotate order (2-3 per post)
- **Data**: Section templates + rotation logic (hash-based)
- **Validation**: ≥2 enrichment H2 sections per post; section order varies across consecutive posts

### R4: Hybrid Reviews (Template + Real Data)
- **Priority**: Must Have
- **Description**: Product blocks use template structure but inject real data (price, specs, delivery, rank, naver_price)
- **Data**: Enricher adds brand/maker/naver_lprice; ingredient DB provides dosage/form/origin
- **Validation**: Every product block references ≥2 real data points; no invented specs

### R5: Pre-Processing Enrichment (Data)
- **Priority**: Must Have
- **Description**: New `health_enricher.py` enriches product data before writer generation
- **Data**: Ingredient DB (SQLite), keyword→condition config, Naver Shopping (if quota)
- **Validation**: Products have `health_enrichment` dict with condition, ingredients, dosage, personas

### R6: Post-Processing Enhancement (Output)
- **Priority**: Must Have
- **Description**: New `health_post_processor.py` injects enrichment sections into generated markdown
- **Data**: Generated body + enriched product data
- **Validation**: Body contains enrichment H2 sections in rotated order; health claim compliance filter active

### R7: Health Claim Compliance
- **Priority**: Must Have (Regulatory)
- **Description**: No efficacy claims (치료/개선/향상/예방); only 식약처 인증 기능성 원료 expressions
- **Data**: Forbidden word list + allowed pattern list (config)
- **Validation**: Automated scan of generated body; fail on violation

### R8: Ingredient Database
- **Priority**: Should Have (Phase 1)
- **Description**: SQLite table with product ingredients, dosage, form, origin
- **Data**: 식약처 public data API + manual curation top 100 keywords
- **Validation**: ≥80% of health-hugo keywords have ingredient data available

### R9: Real Review Data Injection
- **Priority**: Should Have (Phase 2)
- **Description**: Inject review ratings, review snippets (real, not fabricated) into product blocks
- **Data**: Coupang review API (if available), Naver Shopping review count/rating
- **Validation**: ≥70% of product blocks contain real review data when available

### R10: Expandable to Other CUAP Blogs
- **Priority**: Should Have
- **Description**: System designed for beauty-hugo, fitness-hugo (similar structure needs)
- **Data**: Abstract enrichment interfaces
- **Validation**: beauty-hugo health/beauty claim rules can use same framework

## Non-Functional Requirements

### Performance
- **N1**: Pipeline end-to-end < 5 min per article (same as current)
- **N2**: Ingredient DB lookup < 50ms
- **N3**: Post-processor < 10 seconds per article

### Reliability
- **N4**: Enrichment failures degrade gracefully (skip section, don't fail post)
- **N5**: No API rate limit violations (shared DB limiter)
- **N6**: LLM fallback chain works with enriched prompts

### Quality
- **N7**: 0 health claim violations per article
- **N8**: 0 hallucinations on ingredient/dosage data
- **N9**: Content length 2500-3500 chars (CUAP standard)

### Compatibility
- **N10**: All output passes H2-GUARD (180 allowed patterns)
- **N11**: Uses same Coupang/Naver APIs (no new API keys required for Phase 1)
- **N12**: Hugo build succeeds without errors

## Constraints

- Must use existing CUAP curation pipeline (collector.py → enricher.py → writer.py)
- Must comply with 식약처 표시광고 규칙 (health claim regulation)
- AdSense publisher: ca-pub-6677996696534146 (informationhot family)
- Content published via existing shared/publisher.py
- All new modules in /Users/twinssn/Projects/5000/ directory structure

## Success Criteria

1. health-hugo articles show problem framing in intro
2. Enrichment sections rotate (different order across consecutive posts)
3. All product blocks contain real data points (price, specs, delivery, rank)
4. 0 efficacy claim violations in generated content
5. Ingredient data (mg/mcg/IU) present for ≥80% of keywords
6. Articles feel varied (not template-identical) by manual review
7. Pipeline completes within current time budget
8. Hugo build + deploy succeed