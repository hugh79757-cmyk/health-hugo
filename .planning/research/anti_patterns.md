# Anti-Pattern Research — Health-Hugo Content Enrichment

## Patterns to Avoid (From 5000 Project History)

### 1. Template Detection Signals (What Makes Content Feel "Automated")

#### Fixed Structural Patterns
| Pattern | Detection Method | Why It Fails |
|---------|------------------|--------------|
| Same 5 H2 titles every post | H2 sequence fingerprinting | Predictable, no variety |
| Same intro sentence structure | N-gram overlap analysis | "이번에는 OO 기준으로 골랐습니다" repetition |
| Same CTA every post | Exact string match | "아래 링크에서 가격을 확인해 보세요" × 100 posts |
| Fixed product block template | DOM structure comparison | All H3 blocks identical structure |

#### Language Patterns
| Pattern | Examples | Fix |
|---------|----------|-----|
| Marketing filler | "추천드립니다", "인기가 많습니다", "좋은", "훌륭한" | Replace with neutral/specific |
| First-person fake experience | "써보니", "실사용", "직접 사용해보니" | Third-person spec-based |
| Vague superlatives | "최고의", "최상급", "완벽한" | Quantified specs only |
| Meta-commentary | "스펙 정보가 부족합니다", "무게 범위가 불확실" | Omit unknown, don't mention |

#### Content Patterns
| Pattern | Signal | Fix |
|---------|--------|-----|
| No real user data | Only specs, no review quotes/ratings | Inject real data points |
| No situational context | Generic "추천 대상" lists | Condition×Persona matrix |
| Same comparison angle | Always price vs spec | Rotate: brand vs brand, use case vs use case |
| No problem framing | Product-first, not problem-first | Lead with health concern |

---

### 2. Historical Failures in 5000 Project

#### Phase 40-44 Quality Audit Findings
- **travel-hugo**: Fixed camping gear template → Added seasonal filtering, regional grouping
- **travel1-hugo**: Festival posts hallucinated booking info → Added anti-hallucination rules per topic
- **travel3-hugo**: Food posts used "맛있는", "인생맛집" → 34-word forbidden list, price format validation
- **travel4-hugo**: Course posts invented walking times → Forbidden movement patterns (regex)
- **CUAP blogs**: Title template repetition → Title diversification rules + recent title avoidance

#### Recurring Root Causes
1. **Single prompt template** → All posts use same system prompt structure
2. **No post-generation variation** → Output goes straight to publish
3. **Data poverty** → LLM hallucinates when data missing
4. **No quality feedback loop** → Defects accumulate until audit

---

### 3. Anti-Automation Strategies (Proven in Project)

#### Strategy A: Deterministic Variation (Rotation)
- Hash-based section ordering: `hash(keyword + date) % N`
- Title structure rotation: 4 patterns, pick by hash
- Enrichment section selection: weighted random with memory

#### Strategy B: Data-Driven Variation
- Different data → different output naturally
- Ingredient profiles vary → different emphasis
- Price ranges vary → different comparison angles
- Rank positions vary → different "bestseller" framing

#### Strategy C: Post-Processing Injection
- ETAP editorial synthesis: deterministic paragraph from unique data
- CUAP Phase 70: inject after generation, before publish
- Health: inject situational matching + enrichment sections

#### Strategy E: Constraint-Based Generation
- Forbidden word lists (34 for travel3, 6 global + blog-specific)
- Regex pattern bans (movement times, booking channels)
- Required data field checks (must have X, Y, Z or fail)

---

### 4. Health-Specific Anti-Patterns

#### Regulatory (식약처 표시광고법)
| Forbidden | Allowed Alternative |
|-----------|---------------------|
| "혈액 순환에 도움을 줍니다" | "식약처 인증 EPA/DHA 원료 함유" |
| "기억력이 향상됩니다" | "오메가-3 지방산 함유" |
| "면역력이 강화됩니다" | "기능성 원료 비타민D 포함" |
| "눈 피로가 개선됩니다" | "루테인/지아잔틴 함유량 확인" |
| "관절 통증 완화" | "글루코사민/콘드로이틴 함유" |

#### Credibility Patterns
| Fake Credibility | Real Credibility |
|------------------|------------------|
| "전문가 추천" (no source) | "식약처 기능성 인정 원료" |
| "베스트셀러 1위" (vague) | "쿠팡 판매순위 3위 (2026-09 기준)" |
| "만족도 98%" (invented) | "네이버 쇼핑 리뷰 4.7점 (1200건)" — only if real |
| "의사도 먹는" | "약사/영양사 상담 후 섭취 권장" |

---

### 5. Variation Mechanics Design

#### Title Variation (4 Patterns, Hash-Selected)
```python
TITLE_PATTERNS = [
    "{year}년 {month}월 {condition} {ingredient} — {benefit}",  # "2026년 9월 혈행 오메가3 — EPA 600mg 고함량"
    "{ingredient_a} vs {ingredient_b} — {comparison_point}",      # "rTG 오메가3 vs EE 오메가3 — 흡수율 비교"
    "{persona}을 위한 {condition} {form} — {price_tier}",        # "40대 직장인을 위한 혈행 rTG — 3만원대 실속"
    "{condition} 관리 {ingredient} — {specific_angle}",           # "혈행 관리 오메가3 — 원료 원산지·함량 따져보기"
]
```

#### Section Order Variation (Enrichment Sub-Sections)
```python
ENRICHMENT_SECTIONS = [
    ("## 성분 심층 — 핵심 원료와 함량", 0.4),
    ("## 복용 가이드 — 상황별 섭취법", 0.35),
    ("## 실구매 포인트 — 가격·배송·평판", 0.3),
    ("## 이런 분께 추천 — 페르소나별 선택", 0.35),
]

def select_sections(keyword, date, min_sections=2, max_sections=3):
    seed = hash(f"{keyword}{date.isoformat()}") % 10000
    random.seed(seed)
    selected = random.sample(ENRICHMENT_SECTIONS, k=random.randint(min_sections, max_sections))
    # Sort by original weight for consistency
    selected.sort(key=lambda x: -x[1])
    return [s[0] for s in selected]
```

#### Persona Focus Rotation (Per Post)
```python
PERSONA_POOL = {
    "혈행개선": ["40대 사무직 직장인", "고지혈증 관리 중인 50대", "부모님 건강 선물 찾는 30대"],
    "눈건강": ["하루 10시간 모니터 보는 직장인", "수험생 자녀 둔 학부모", "노안 시작 50대"],
    # ...
}

def select_personas(condition, count=2):
    pool = PERSONA_POOL.get(condition, [])
    # Rotate based on keyword hash
    seed = hash(condition) % len(pool) if pool else 0
    return pool[seed:seed+count] + pool[:max(0, count-len(pool[seed:]))]
```

---

### 6. Quality Validation Rules (Automated)

#### Pre-Publish Checks (Extend quality_gate.py)
```python
def validate_health_article(body, products, keyword):
    checks = []
    
    # 1. Health claim compliance
    forbidden_claims = ["개선됩니다", "향상됩니다", "효과가 있습니다", "치료", "예방", "완화"]
    for claim in forbidden_claims:
        if claim in body:
            checks.append(("FAIL", f"Forbidden efficacy claim: {claim}"))
    
    # 2. Required enrichment sections (2-3)
    enrichment_h2 = [h for h in extract_h2(body) if h in ENRICHMENT_H2_SET]
    if len(enrichment_h2) < 2 or len(enrichment_h2) > 3:
        checks.append(("FAIL", f"Enrichment sections count: {len(enrichment_h2)} (need 2-3)"))
    
    # 3. Situational matching present
    if not any(p in body for p in ["직장인", "수험생", "부모님", "관리 중인", "선물"]):
        checks.append(("WARN", "No situational persona reference found"))
    
    # 4. Real data points in product blocks
    for i, p in enumerate(products):
        block = extract_product_block(body, i)
        has_real_data = any(x in block for x in ["네이버 최저가", "판매순위", "로켓배송", "리뷰"])
        if not has_real_data and p.get("naver_lprice"):
            checks.append(("WARN", f"Product {i+1}: naver_lprice available but not used"))
    
    # 5. Ingredient data present
    if not any(kw in body for kw in ["mg", "mcg", "IU", "rTG", "EE", "EPA", "DHA"]):
        checks.append(("WARN", "No specific ingredient amounts found"))
    
    return checks
```

---

### 7. Monitoring Metrics (Post-Launch)

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Avg content length | 3000 chars | < 2500 or > 4000 |
| Enrichment sections/post | 2.5 | < 2 or > 3 |
| Hallucination rate | 0% | > 0 |
| Health claim violations | 0 | > 0 |
| Title uniqueness (30-day) | 100% | < 100% |
| Section order entropy | High | Low (repeating patterns) |
| Persona variation rate | > 60% | < 40% |

---

## Implementation Guardrails

### Code-Level
- All new H2 titles pre-registered in `_ALLOWED_H2_PATTERNS` (hugo_writer.py)
- Health claim filter runs in post-processor (non-removable)
- Forbidden word list loaded from config (not hardcoded)
- Variation logic deterministic (hash-based, testable)

### Process-Level
- Dry-run 5 articles per config change before deploy
- Weekly quality audit (automated + manual sample)
- Monthly pattern analysis (title n-grams, section orders)
- Rollback trigger: > 2 health claim violations in 24h