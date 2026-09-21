# Stack Research — Health-Hugo Content Enrichment

## Current Stack (CUAP Curation Pipeline)

### Core Components
| Layer | Technology | Location | Role |
|-------|------------|----------|------|
| **Data Source** | Coupang Affiliate API | `pipelines/curation/coupang_client.py` | Product search & best-seller |
| **Cache/DB** | SQLite (curation.db) | `/Users/twinssn/Projects/5000/data/curation.db` | Keyword→products, 3-day TTL |
| **Enrichment** | Naver Shopping API + Regex | `pipelines/curation/enricher.py` | Brand/maker, parsed specs |
| **Generation** | AI Writer (multi-tier fallback) | `shared/ai_writer.py` | LLM content generation |
| **Quality Gates** | Validators + Relevance Scorer | `shared/validators.py`, `shared/relevance_scorer.py` | Title validation, relevance filtering |
| **Publishing** | Hugo + Cloudflare Pages | `shared/publisher.py`, `shared/hugo_writer.py` | Markdown → Hugo → Deploy |
| **Scheduling** | launchd + scheduler.py | `/Users/twinssn/Projects/5000/scheduler.py` | Daily runs per blog |

### Key Dependencies
- **Python 3.11+**: Core runtime
- **requests**: HTTP client for Coupang/Naver APIs
- **python-dotenv**: Env var loading
- **PyYAML**: Config parsing
- **LLM Providers**: Multi-tier fallback chain (16 models)
- **Hugo Extended**: Static site generator
- **wrangler**: Cloudflare Pages deployment

### Existing Data Flow
```
Keyword → Coupang API (10 products) → SQLite cache (3 days)
    → Enricher: regex specs + Naver Shopping (top 5) → brand/maker/naver_lprice
    → Writer: builds prompt with enriched products → AI generates article
    → Hugo: renders markdown → Cloudflare Pages deploy
```

---

## Missing Data for Health-Hugo Requirements

### Required by health-hugo Rules (BLOG_EXTRA_RULES)
| Required Field | Current Source | Status |
|----------------|----------------|--------|
| 주성분명과 함량 (mg/mcg/IU) | ❌ Not in Coupang | **MISSING** |
| 복용 대상 구체적 생활 장면 | ❌ Not in Coupang | **MISSING** |
| 섭취 방법 (1일 몇 회, 몇 정) | ❌ Not in Coupang | **MISSING** |
| 성분 형태 (rTG vs EE) | ❌ Not in Coupang | **MISSING** |
| EPA/DHA 별도 함량 | ❌ Not in Coupang | **MISSING** |
| 원료 원산지 | ❌ Not in Coupang | **MISSING** |
| 캡슐 크기/목넘김 | ❌ Not in Coupang | **MISSING** |

### Available but Underutilized
| Data | Source | Current Use | Potential |
|------|--------|-------------|-----------|
| `isRocket` / `isFreeShipping` | Coupang API | Badge display only | Delivery context in body |
| `rank` | Coupang API | Table ordering | Popularity signal in text |
| `naver_lprice` | Naver Shopping | Price comparison | "네이버 최저가 OO원" context |
| `brand` / `maker` | Naver Shopping | Table column | Brand authority mention |
| `parsed_specs` (regex from name) | Product name | Basic specs table | Extract EPA/DHA if in name |

### External Data Sources (Investigation Needed)
| Source | Data Type | Access Method | Feasibility |
|--------|-----------|---------------|-------------|
| **식약처 건강기능식품 공공데이터** | Ingredients, dosage, claims | Open API (data.go.kr) | High - official, structured |
| **네이버 쇼핑 상품 상세** | Full spec sheet, reviews | Shopping API v1 (need higher quota) | Medium - quota limited |
| **쿠팡 리뷰 크롤링** | Real user reviews | Browser automation (Aside MCP) | Low - anti-bot, fragile |
| **제조사 공식 사이트** | Detailed specs, origin | Manual/API per brand | Low - fragmented |
| **원료 원산지 DB** | Ingredient sourcing | Custom build needed | Low - new infrastructure |

---

## Content Enrichment Patterns in Other Pipelines

### Travel Pipeline (TAP)
- **Structured API data**: 한국관광공사 API provides festival dates, heritage info, course details
- **Enrichment**: Area codes, seasonal filtering, regional grouping
- **Quality**: Anti-hallucination rules per topic type (festival/heritage/food/course)

### Senior Pipeline (SEAP)
- **Enrichment in writer**: `_append_links()` adds Coupang affiliate links, `_clean_vague_phrases()` removes marketing speak
- **No separate enrich step** - pass-through placeholder

### ETAP Pipeline
- **Editorial synthesis**: `pipelines/etap/editorial_synthesis.py` appends deterministic paragraph from unique data points
- **Data adapters**: `pipelines/etap/data_adapters.py` extracts unique data per topic type

### CUAP (Current) - Phase 70 Wave 3
- **Editorial synthesis injection**: `writer.py:_inject_editorial_synthesis()` appends paragraph after body generation
- **Trigger**: Topic carries `topic_type` (graceful degradation if no unique data)

---

## Anti-Automation Patterns

### Current (Problematic)
- Fixed 5-section structure every post
- Same H2 titles: "한눈에 보는 비교표", "상품별 상세 비교", "구매 전 체크리스트"
- Template-like title patterns despite diversification rules
- No real user review data - all spec-based

### Desired (From User Requirements)
1. **Hybrid structure**: Core 5 sections fixed, enrichment sub-sections order varies
2. **Hybrid reviews**: Template structure + real data points (price, specs, delivery, rank)
3. **Situational matching**: Condition × Persona matrix (health needs × user profiles)
4. **Dual enrichment**: Pre-processing (data enrichment) + Post-processing (output enhancement)

---

## Technical Constraints

### Hard Constraints
- **Coupang API rate limit**: 40/min, 300/hour (shared DB-backed)
- **Naver Shopping API**: Top 5 products only (quota saving)
- **LLM token limits**: max_tokens 4800 (current), ~6000 target
- **Health claims**: Must comply with 식약처 표시광고 rules (no efficacy claims)
- **Hugo build**: Must pass H2-GUARD patterns (180 allowed patterns)

### Soft Constraints
- **Content length**: 2500-3500 chars (Korean)
- **Quality gates**: 0 hallucinations, min 3 H2, min 3 H3
- **Title**: 10-35 chars, no parens, no banned patterns
- **AdSense**: ca-pub-6677996696534146 (informationhot family)

---

## Recommended Stack Extensions

### Minimal (Pre-processing only)
- Add ingredient DB (SQLite) seeded from 식약처 open data
- Extend enricher.py to join ingredient data by product name matching
- Add situational matching rules to writer prompt

### Full (Pre + Post processing)
- Pre: Ingredient DB + Naver Shopping deep specs (if quota allows)
- Post: Editorial synthesis step (like ETAP) for situational matching paragraph
- Post: Review simulation using real data points (price comparison, rank, delivery)

### Infrastructure
- New table: `health_ingredients` in curation.db (or separate health.db)
- New module: `pipelines/curation/health_enricher.py`
- New prompt templates: `config/prompts/health.yaml` with anti-hallucination rules