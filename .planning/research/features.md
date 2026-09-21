# Features Research — Health-Hugo Enriched Content

## Target Feature Set

### 1. Problem/Solution Framing (Core Requirement)

**Current State**: Pure product listing with specs table
**Desired**: Each post addresses a specific health problem → presents products as solutions

**Implementation Approach**:
- Map keywords to health conditions (e.g., "오메가3" → "혈행/눈건강/두뇌", "루테인" → "눈 피로/황반변성 예방")
- Intro section: "OO 문제로 고민하는 분들을 위해..."
- Each product positioned as solution variant for different severity/budget

**Data Needed**: 
- Keyword → Health condition mapping (new config)
- Condition-specific selection criteria (e.g., EPA/DHA ratio for blood circulation)

---

### 2. Situational Matching — Condition × Persona Matrix

**Matrix Structure**:
| Health Condition (Row) | User Persona (Column) |
|---|---|
| 혈행 개선 | 40대 직장인(앉아있는 업무), 50대 부모님 선물, 고지혈증 관리자 |
| 눈 건강 | 장시간 모니터 직장인, 수험생, 노안 시작 50대 |
| 관절/연골 | 등산/골프 애호가, 계단 오르기 힘든 중년, 재활 중 |
| 면역/항산화 | 환절기 감기 잦은 직장인, 육아맘, 수술 후 회복 |
| 뼈 건강 | 골다공증 위험 50대 여성, 실내 생활 많은 직장인, 성장기 청소년 |

**Implementation**:
- Pre-processing: Tag each keyword with primary/secondary conditions
- Prompt: "이 제품은 [조건] 중 [페르소나]에게 특히 적합합니다" framing
- Variation: Rotate persona focus per post (not all 3×5 every time)

**Anti-Pattern Prevention**:
- Never claim medical treatment ("치료", "완치", "개선")
- Use "관심 있는 분", "관리하고 싶은 분", "챙기고 싶은 분"
- 식약처 인증 기능성 원료 명시만 허용

---

### 3. Varied Content Structures (Anti-Automation)

**Core 5 Sections (FIXED - CUAP Spec)**:
1. 도입부 — 문제 제기 + 선정 기준
2. `## 한눈에 보는 비교표` — 필수
3. `## 상품별 상세 비교` — 필수  
4. `## 구매 전 체크리스트` — 필수
5. 마무리 — 상황별 재확인 + CTA

**Variable Enrichment Sub-Sections (ROTATING ORDER)**:
| Sub-Section | Content | Rotation Weight |
|---|---|---|
| `## 성분 심층 — 핵심 원료와 함량` | EPA/DHA, rTG/EE, 원료 원산지 | 40% |
| `## 복용 가이드 — 상황별 섭취법` | 1일 횟수, 정수, 식전/후, 목넘김 팁 | 35% |
| `## 실구매 포인트 — 가격·배송·평판` | 네이버 최저가, 로켓배송, 판매순위, 리뷰 요약 | 30% |
| `## 이런 분께 추천 — 페르소나별 선택` | Condition×Persona 매트릭스에서 2~3개 추출 | 35% |

**Rotation Logic**:
- Hash(keyword + date) → deterministic but varied order
- Never same order 2 posts in a row
- At least 2 enrichment sections per post (max 3)

---

### 4. Hybrid Review System (Template + Real Data)

**Template Structure (Fixed)**:
```
### {상품명} — {한 줄 특징}
![이미지]({product_image})

**핵심 스펙**: {parsed_specs에서 추출}
**가격**: {product_price:,}원 {배송배지}
{브랜드 있으면: **브랜드**: {brand}}
{네이버최저가 있으면: **네이버 최저가**: {naver_lprice:,}원 ({naver_mall})}
{랭크 있으면: **쿠팡 판매순위**: {rank}위}

**장점**: {데이터 기반 1~2가지}
**아쉬운 점**: {데이터 기반 1가지}

{상황별 적합 문구 - Condition×Persona에서 1개}
[쿠팡에서 최저가 확인하기]({product_url})
```

**Real Data Injection Points**:
| Placeholder | Source | Fallback |
|---|---|---|
| 핵심 스펙 | parsed_specs + ingredient DB | "상품명에서 확인하세요" |
| 배송배지 | isRocket/isFreeShipping | "일반배송" |
| 브랜드 | Naver Shopping brand/maker | 생략 |
| 네이버 최저가 | naver_lprice/naver_mall | 생략 |
| 판매순위 | rank | 생략 |
| 장점/아쉬운점 | Spec-derived rules | 스펙 기반 추론만 |

**Anti-Hallucination Rules for Health**:
- 리뷰 점수/판매량 수치: 데이터에 있을 때만 사용 (절대 생성 금지)
- "리뷰 4.8점", "누적 판매 1만건+" — API 응답에 없으면 쓰지 않음
- 목넘김/캡슐 크기: ingredient DB에 있을 때만, 없으면 언급 안 함
- 효능 표현: "식약처 인증 OOO 원료 함유" 수준만 허용

---

### 5. Dual-Stage Enrichment Architecture

#### Stage 1: Pre-Processing (Data Enrichment)
**Location**: New `health_enricher.py` → called after `enricher.py` in pipeline

**Input**: Products with Coupang data + Naver Shopping brand/maker
**Output**: Products + `health_enrichment` dict per product

```python
health_enrichment = {
    "primary_condition": "혈행개선",           # from keyword mapping
    "secondary_conditions": ["눈건강", "두뇌"],  # from ingredient profile
    "key_ingredients": {                       # from ingredient DB
        "EPA": "600mg",
        "DHA": "400mg", 
        "형태": "rTG",
        "원료_원산지": "노르웨이"
    },
    "dosage": "1일 1회 2정",
    "capsule_info": "소형 캡슐, 목넘김 용이",
    "target_personas": ["40대 직장인", "고지혈증 관리자"],  # from matrix
    "selection_criteria": "EPA+DHA 1000mg 이상, rTG 형태"
}
```

**Data Sources Priority**:
1. 식약처 건강기능식품 공공데이터 (official, structured)
2. Naver Shopping 상품 상세 (if quota allows)
3. 상품명 regex parsing (fallback)
4. Keyword-based heuristics (last resort)

#### Stage 2: Post-Processing (Output Enhancement)
**Location**: New `health_post_processor.py` → called after `writer.generate_curation_article()`

**Input**: Generated markdown body + enriched product data
**Output**: Enhanced markdown body

**Operations**:
1. **Inject enrichment sub-sections** in rotated order (after 비교표, before 상품별 상세)
2. **Enhance product blocks** with situational matching sentences
3. **Add problem/solution framing** to intro
4. **Verify health claim compliance** (strip forbidden efficacy claims)
5. **Ensure H2-GUARD compliance** for new sub-section titles

---

### 6. Ingredient Database (New Infrastructure)

**Schema** (`health_ingredients` table):
```sql
CREATE TABLE health_ingredients (
    product_id TEXT PRIMARY KEY,      -- Coupang productId
    product_name_hash TEXT,           -- for fuzzy matching
    primary_ingredient TEXT,          -- 주성분 (오메가3, 루테인, 비타민D 등)
    ingredient_details JSON,          -- {EPA: "600mg", DHA: "400mg", 형태: "rTG"}
    dosage TEXT,                      -- 1일 1회 2정
    capsule_size TEXT,                -- 소형/중형/대형
    capsule_type TEXT,                -- 연질/경질
    origin TEXT,                      -- 원료 원산지
    target_conditions JSON,           -- ["혈행", "눈", "두뇌"]
    source TEXT,                      -- "식약처", "네이버쇼핑", "상품명파싱", "휴리스틱"
    confidence REAL,                  -- 0.0~1.0
    updated_at TEXT
);
```

**Seeding Strategy**:
1. **Phase 1**: 식약처 공공데이터 API → 제품명/업체명/성분/함량/기능성 매핑
2. **Phase 2**: Top 100 health-hugo keywords → manual curation for high-traffic products
3. **Phase 3**: Ongoing - pipeline writes back when new products appear

---

### 7. Keyword → Condition Mapping (Config)

**File**: `config/prompts/health_conditions.yaml`
```yaml
keyword_conditions:
  "오메가3": 
    primary: "혈행개선"
    secondary: ["눈건강", "두뇌건강", "면역"]
    key_nutrients: ["EPA", "DHA"]
    required_form: "rTG"
  "루테인":
    primary: "눈건강"
    secondary: ["황반색소밀도", "눈피로"]
    key_nutrients: ["루테인", "제아잔틴"]
  "비타민D":
    primary: "뼈건강"
    secondary: ["면역", "근기능"]
    key_nutrients: ["비타민D3"]
  "칼슘":
    primary: "뼈건강"
    secondary: ["골다공증예방"]
    key_nutrients: ["칼슘", "마그네슘", "비타민D"]
  "글루코사민":
    primary: "관절건강"
    secondary: ["연골보호"]
    key_nutrients: ["글루코사민", "콘드로이틴"]
  # ... more mappings
```

---

### 8. Quality Gates for Enriched Content

**Additional Checks** (extend `quality_checklist.yaml`):
```yaml
blogs:
  health-hugo:
    # Existing CUAP checks apply
    # NEW: Health-specific
    required_enrichment_sections_min: 2
    required_enrichment_sections_max: 3
    health_claim_compliance: true
    ingredient_data_present: true
    situational_matching_present: true
    forbidden_efficacy_claims:
      - "개선됩니다"
      - "향상됩니다" 
      - "효과가 있습니다"
      - "치료"
      - "예방"
      - "완화"
    allowed_claim_patterns:
      - "식약처 인증 .* 원료"
      - "기능성 원료 .* 함유"
      - ".*에 관심 있는 분"
      - "성분표를 확인하여"
```

---

## Integration Points

| Pipeline Stage | Current | New Addition |
|---|---|---|
| Keyword selection | `pipeline.py:_select_keyword()` | Tag keyword with condition |
| Collection | `collector.py:collect_keyword()` | Unchanged |
| Enrichment | `enricher.py:enrich_products()` | → `health_enricher.py:enrich_health_products()` |
| Generation | `writer.py:generate_curation_article()` | Pass enriched data to prompt |
| Post-generation | `_inject_editorial_synthesis()` | → `health_post_processor.py:enhance_health_article()` |
| Quality check | `shared/quality_gate.py` | Health-specific validators |
| Publish | `shared/publisher.py` | Unchanged |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| 식약처 API quota/structure changes | Medium | High | Cache locally, fallback to heuristics |
| Naver Shopping quota limits | High | Medium | Top 5 only, cache aggressively |
| LLM hallucination on health claims | High | Critical | Strict post-process filtering, prompt rules |
| Ingredient DB coverage gaps | High | Medium | Graceful degradation - skip enrichment section if no data |
| H2-GUARD pattern mismatch | Low | Medium | Pre-register new H2 patterns in `_ALLOWED_H2_PATTERNS` |
| Content length bloat | Medium | Low | Token budget management, section length caps |

---

## Implementation Priority

### Phase 1: Foundation (Week 1-2)
- [ ] Create `health_ingredients` table + seeding script
- [ ] Build `health_enricher.py` with 식약처 API integration
- [ ] Add keyword→condition mapping config
- [ ] Extend writer prompt with health rules

### Phase 2: Enrichment Sections (Week 2-3)
- [ ] Build `health_post_processor.py` for sub-section injection
- [ ] Implement rotation logic for enrichment sections
- [ ] Add situational matching (Condition×Persona)
- [ ] Health claim compliance filter

### Phase 3: Hybrid Reviews (Week 3)
- [ ] Enhance product block template with real data
- [ ] Add review simulation from data points
- [ ] A/B dry-run with quality checklist

### Phase 4: Validation & Rollout (Week 4)
- [ ] Full quality audit on health-hugo
- [ ] Expand to other CUAP health-related blogs (beauty, fitness)
- [ ] Monitor metrics: length, hallucination, engagement