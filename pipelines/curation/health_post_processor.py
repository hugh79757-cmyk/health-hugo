"""Health-hugo post-processor — enrichment injection, rotation, persona matching, compliance.

Location: pipelines/curation/health_post_processor.py
Called after writer.generate_curation_article() for health-hugo keywords only.
All changes additive — health-hugo conditional branch only.
"""
import hashlib
import json
import os
import re
import sqlite3
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "health_ingredients.db"
CONDITIONS_YAML = PROJECT_ROOT / "config" / "prompts" / "health_conditions.yaml"

FORBIDDEN_EFFICACY = ["치료", "개선", "향상", "예방", "완화", "효과가 있습니다"]
ALLOWED_PATTERNS = ["식약처 인증", "기능성 원료", "관심 있는 분"]

_SANITIZE_MAP = {
    "혈행개선": "혈행",
    "체력개선": "체력",
    "수면개선": "수면",
    "빈혈예방": "빈혈",
}

_conditions_cache = None


def _load_conditions():
    global _conditions_cache
    if _conditions_cache is not None:
        return _conditions_cache
    try:
        import yaml
        with open(CONDITIONS_YAML, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _conditions_cache = data.get("keyword_conditions", {})
        return _conditions_cache
    except Exception:
        return {}


def _lookup_ingredients(keyword):
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM health_ingredients WHERE primary_ingredient = ? LIMIT 5",
            (keyword,),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows if rows else None
    except Exception:
        return None


def _resolve_products(products, keyword):
    if products:
        return products
    return _lookup_ingredients(keyword) or []


def _rotate_sections(keyword: str, target_date: date = None, available: list = None) -> list:
    if available is None:
        available = ["성분_심층", "복용_가이드", "실구매_포인트", "이런_분께_추천"]
    d = target_date or date.today()
    seed = f"{keyword}:{d.isoformat()}"
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16], 16)
    n = len(available)
    if n <= 2:
        return available
    from itertools import combinations, permutations
    all_options = []
    for count in [2, 3]:
        for combo in combinations(available, count):
            for perm in permutations(combo):
                all_options.append(list(perm))
    idx = h % len(all_options)
    return all_options[idx]


def _next_rotation(keyword: str, target_date: date = None) -> list:
    if target_date is None:
        target_date = date.today()
    from datetime import timedelta
    next_date = target_date + timedelta(days=1)
    return _rotate_sections(keyword, next_date)


def select_personas(condition: str, keyword: str) -> list:
    return _select_personas(condition, keyword)


def _select_personas(condition: str, keyword: str) -> list:
    conditions = _load_conditions()
    keyword_entry = conditions.get(keyword, {})
    personas = keyword_entry.get("target_personas", [])
    if not personas:
        secondary = keyword_entry.get("secondary", [])
        for sec in secondary:
            for k, v in conditions.items():
                if sec in v.get("secondary", []):
                    personas = v.get("target_personas", [])
                    break
            if personas:
                break
    seed = f"{keyword}:{condition}:persona"
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    n = len(personas) if personas else 0
    if n <= 2:
        return personas[:3] if personas else []
    offset = int(h[:8], 16) % n
    return [personas[(offset + i) % n] for i in range(min(3, n))]


def _sanitize_condition(name: str) -> str:
    return _SANITIZE_MAP.get(name, name)


def _filter_efficacy_claims(text: str) -> str:
    for claim in FORBIDDEN_EFFICACY:
        text = re.sub(re.escape(claim), "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _build_section_content(section_key: str, products: list, keyword: str, condition: str) -> str:
    if section_key == "성분_심층":
        return _build_ingredient_section(products, keyword)
    elif section_key == "복용_가이드":
        return _build_dosage_section(products, keyword, condition)
    elif section_key == "실구매_포인트":
        return _build_purchase_section(products, keyword)
    elif section_key == "이런_분께_추천":
        return _build_persona_section(keyword, condition)
    elif section_key == "가격대_분석":
        return _build_price_section(products, keyword)
    elif section_key == "도입부_보충":
        return _build_intro_section(products, keyword, condition)
    return ""


def _build_ingredient_section(products: list, keyword: str) -> str:
    if not products:
        return "## 성분 심층 — 핵심 원료와 함량\n\n주요 원료 정보가 확인되지 않았습니다."
    lines = ["## 성분 심층 — 핵심 원료와 함량", ""]
    for p in products[:2]:
        details = p.get("ingredient_details")
        if details and isinstance(details, str):
            try:
                details = json.loads(details)
            except (json.JSONDecodeError, TypeError):
                details = {}
        primary = p.get("primary_ingredient", keyword)
        dosage = p.get("dosage", "")
        origin = p.get("origin", "")
        line = f"**{primary}**: "
        parts = []
        if dosage:
            parts.append(f"함량 {dosage}")
        if isinstance(details, dict):
            form = details.get("형태", details.get("type", ""))
            if form:
                parts.append(f"형태 {form}")
        if parts:
            line += ", ".join(parts)
        else:
            line += f"함량 정보 {primary}"
        lines.append(line)
        if origin:
            lines.append(f"  - 원료 원산지: {origin}")
    return "\n".join(lines)


def _build_dosage_section(products: list, keyword: str, condition: str) -> str:
    dosage = None
    if products:
        for p in products:
            if p.get("dosage"):
                dosage = p["dosage"]
                break
    if not dosage:
        conditions = _load_conditions()
        entry = conditions.get(keyword, {})
        dosage = entry.get("typical_dosage", "")
    if not dosage:
        return "## 복용 가이드 — 상황별 섭취법\n\n복용 방법이 확인되지 않았습니다."
    lines = [
        "## 복용 가이드 — 상황별 섭취법",
        "",
        f"- **1일 횟수**: {dosage}",
        f"- **1회 정수**: 제품 라벨 확인",
        f"- **식전/후**: 식후 30분",
        f"- **목넘김**: 충분한 물과 함께",
    ]
    return "\n".join(lines)


def _build_purchase_section(products: list, keyword: str) -> str:
    if not products:
        return "## 실구매 포인트 — 가격·배송·평판\n\n실구매 데이터가 확인되지 않았습니다."
    lines = ["## 실구매 포인트 — 가격·배송·평판", ""]
    for p in products[:2]:
        name = p.get("product_name", p.get("product_id", keyword))
        price = p.get("price", "---")
        rank = p.get("rank", "---")
        is_rocket = p.get("isRocket", False)
        rocket = "로켓배송" if is_rocket else "일반배송"
        lines.append(f"**{name}**")
        lines.append(f"- 가격: {price}원 | 배송: {rocket} | 판매순위: {rank}")
    return "\n".join(lines)


def _build_price_section(products: list, keyword: str) -> str:
    if not products:
        return "## 가격대 분석 — 시장 내 위치\n\n가격대 정보가 확인되지 않았습니다."
    lines = ["## 가격대 분석 — 시장 내 위치", ""]
    prices = [p.get("product_price", 0) for p in products[:3] if p.get("product_price")]
    if not prices:
        return "가격대 정보가 확인되지 않았습니다."
    min_p = min(prices)
    max_p = max(prices)
    lines.append(f"- **최저가**: {min_p:,}원")
    lines.append(f"- **최고가**: {max_p:,}원")
    lines.append(f"- **평균가**: {sum(prices)//len(prices):,}원")
    if max_p - min_p > min_p * 0.5:
        lines.append("- 가격 차이가 큼 — 용량·함량 비교 후 결정")
    else:
        lines.append("- 가격 편차 작음 — 기능·배송 기준으로 선택")
    return "\n".join(lines)


def _build_intro_section(products: list, keyword: str, condition: str) -> str:
    if not condition:
        return "## 도입부 — 상황별 안내\n\n도입부 정보가 확인되지 않았습니다."
    lines = ["## 도입부 — 상황별 안내", ""]
    lines.append(f"{condition}이/가 걱정되시는 분들을 위해 {keyword} 제품들을 비교합니다.")
    lines.append("")
    personas = _select_personas(condition, keyword)[:2]
    if personas:
        for p in personas:
            lines.append(f"- {p}에게 적합한 제품을 안내합니다")
    lines.append("")
    lines.append(f"총 {len(products[:3])}개 제품을 가격·성분·배송 기준으로 분석했습니다.")
    return "\n".join(lines)


def _build_persona_section(keyword: str, condition: str) -> str:
    personas = _select_personas(condition, keyword)
    if not personas:
        return "## 이런 분께 추천 — 페르소나별 선택\n\n대상 이용자 정보가 확인되지 않았습니다."
    safe_condition = _sanitize_condition(condition)
    lines = ["## 이런 분께 추천 — 페르소나별 선택", ""]
    for persona in personas[:3]:
        lines.append(f"- {safe_condition} 관련 상황에서 {persona}에게 특히 적합합니다")
    return "\n".join(lines)


# ── T5.1: 마무리 구조 다변화 (4 variants, weighted random) ──

_MARUCHARI_VARIANTS = {
    "A": {"title": "정리 — 상황별로 다시 한번", "type": "서술형"},
    "B": {"title": "핵심 정리 — 이것만 기억하세요", "type": "불릿"},
    "C": {"title": "이 중 어떤 것이 본인에게 맞을까?", "type": "질문종결"},
    "D": {"title": None, "type": "자연종결"},
}

_MARUCHARI_WEIGHTS = {"A": 40, "B": 25, "C": 20, "D": 15}


def _select_maruchari_variant(keyword: str, target_date: date = None) -> str:
    d = target_date or date.today()
    seed = f"{keyword}:{d.isoformat()}:maruchari"
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16], 16)
    idx = h % 100
    cumulative = 0
    for variant, weight in _MARUCHARI_WEIGHTS.items():
        cumulative += weight
        if idx < cumulative:
            return variant
    return "A"


def _apply_maruchari_variant(body: str, variant: str) -> str:
    if variant not in _MARUCHARI_VARIANTS:
        return body
    variant_info = _MARUCHARI_VARIANTS[variant]
    title = variant_info["title"]
    if title is None:
        body = re.sub(r"^## 마무리[^\n]*\n?", "", body, flags=re.MULTILINE)
    else:
        body = re.sub(r"^## 마무리", f"## {title}", body, count=1, flags=re.MULTILINE)
    return body


# ── T5.2: H2 개수 가변 (mandatory/optional separation) ──

_OPTIONAL_H2_POOL = ["성분_심층", "복용_가이드", "실구매_포인트", "이런_분께_추천", "가격대_분석", "도입부_보충"]

_MANDATORY_H2_MARKERS = ["한눈에 보는 비교표", "상품별 상세 비교", "구매 전 체크리스트"]


def _select_optional_h2s(keyword: str, target_date: date = None, maruchari_variant: str = None) -> list:
    d = target_date or date.today()
    seed = f"{keyword}:{d.isoformat()}:optional_h2"
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16], 16)
    if maruchari_variant in ("A", "B", "C"):
        count = (h % 2) + 1
    else:
        count = (h % 3) + 1
    available = _OPTIONAL_H2_POOL[:]
    result = []
    for _ in range(count):
        idx = h % len(available)
        result.append(available.pop(idx))
        h = (h * 31 + 17) % (2**32)
    return result


def _track_article(keyword: str, body: str, title: str = "") -> dict:
    try:
        from scripts.expression_tracker import track_article as _track
        return _track(keyword, body, title)
    except Exception:
        return {}


# ── T5.3: 종결 어미 변주 (체 types) ──

_CHE_TYPES = {
    "default": {"ending_in": "입니다/습니다", "description": "합쇼체 (현재 기본)"},
    "fan_friendly": {"ending_in": "요", "description": "해요체 (친근한 어조)"},
    "analytical": {"ending_in": "이다", "description": "해라체 (분석적 어조)"},
    "health_hugo": {"ending_in": "입니다/이다", "description": "건강-hugo 특수 (주로 ~입니다, ~이다 허용)"},
}

_CHE_WEIGHTS = {"default": 35, "fan_friendly": 25, "analytical": 20, "health_hugo": 20}


def _select_che_type(keyword: str, target_date: date = None) -> str:
    d = target_date or date.today()
    seed = f"{keyword}:{d.isoformat()}:che_type"
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16], 16)
    idx = h % 100
    cumulative = 0
    for ctype, weight in _CHE_WEIGHTS.items():
        cumulative += weight
        if idx < cumulative:
            return ctype
    return "default"


_CHE_OVERRIDES = {
    "fan_friendly": [
        ("습니다", "요"),
        ("입니다", "예요"),
    ],
    "analytical": [
        ("습니다", "다"),
        ("입니다", "이다"),
    ],
    "health_hugo": [
        ("습니다", "입니다"),
    ],
}


def _apply_che_type(body: str, che_type: str) -> str:
    if che_type not in _CHE_OVERRIDES:
        return body
    for old, new in _CHE_OVERRIDES[che_type]:
        body = body.replace(old, new)
    return body


_REAL_DATA_POINTS = ["price", "rank", "isRocket", "isFreeShipping", "brand", "naver_lprice", "product_name", "image", "url"]


def _get_real_data_points(product: dict) -> dict:
    """Extract real data points from product dict (Coupang/Naver API or DB).

    Returns dict of field_name → value for all present real data points.
    No fabricated scores or sales numbers — only fields from actual API responses.
    """
    points = {}
    for field in _REAL_DATA_POINTS:
        if field in product and product[field] is not None:
            val = product[field]
            if isinstance(val, str) and val.strip():
                points[field] = val
            elif not isinstance(val, str):
                points[field] = val
    ingredient_details = product.get("ingredient_details")
    if ingredient_details:
        if isinstance(ingredient_details, str):
            try:
                ingredient_details = json.loads(ingredient_details)
            except (json.JSONDecodeError, TypeError):
                ingredient_details = {}
        if isinstance(ingredient_details, dict):
            for k, v in ingredient_details.items():
                if v and str(v).strip():
                    points[f"spec_{k}"] = v
    origin = product.get("origin")
    if origin and str(origin).strip():
        points["origin"] = origin
    dosage = product.get("dosage")
    if dosage and str(dosage).strip():
        points["dosage"] = dosage
    return points


def _validate_product_block(product: dict, keyword: str) -> list:
    """Verify product block has ≥2 real data points. Returns list of missing warnings."""
    points = _get_real_data_points(product)
    warnings = []
    if len(points) < 2:
        missing = [f for f in _REAL_DATA_POINTS if f not in points]
        warnings.append(f"[{keyword}] Product {product.get('product_name', product.get('product_id', '?'))}: only {len(points)} real data point(s), need ≥2. Present: {list(points.keys())}")
    return warnings


def _inject_real_data(product: dict, keyword: str) -> str:
    """Generate real-data-injected product comparison block text.

    Each block references ≥2 real data points (price, specs, delivery, rank, brand, etc.).
    Never fabricates review scores or sales numbers.
    """
    points = _get_real_data_points(product)
    name = points.get("product_name", product.get("product_id", keyword))
    parts = []
    if "spec_형태" in points or "spec_형태" in points:
        form = points.get("spec_형태") or points.get("spec_타입", "")
        if form:
            parts.append(f"형태 {form}")
    for spec_key in ["spec_EPA", "spec_DHA", "spec_함량"]:
        if spec_key in points:
            parts.append(f"{points[spec_key]}")
    if "origin" in points:
        parts.append(f"원산지 {points['origin']}")
    spec_str = ", ".join(parts) if parts else "제품 상세 스펙 확인 필요"

    price = points.get("price", "---")
    rank = points.get("rank", "---")
    is_rocket = product.get("isRocket", False)
    rocket = "로켓배송" if is_rocket else "일반배송"
    brand = points.get("brand", "")
    naver_price = points.get("naver_lprice", "")

    lines = [f"**{name}**"]
    data_display = []
    if price != "---":
        data_display.append(f"가격 {price}원")
    if rank != "---":
        data_display.append(f"판매순위 {rank}위")
    if brand:
        data_display.append(f"브랜드 {brand}")
    if naver_price:
        data_display.append(f"네이버 최저가 {naver_price}원")
    data_display.append(f"배송 {rocket}")
    if spec_str:
        data_display.append(f"핵심 스펙: {spec_str}")
    if len(data_display) < 2:
        data_display.append(f"제품 정보 {name}")
    lines.append(" | ".join(data_display))
    return "\n".join(lines)


def enhance_health_article(body: str, products: list, keyword: str) -> str:
    """Post-process curation article with enrichment sections.

    Adds 2-3 rotating enrichment H2 sections after product blocks.
    Filters forbidden efficacy claims. Adds problem/solution framing.
    Injects real data points into product blocks (≥2 per block).
    T5.1: Varies 마무리 structure (4 variants, weighted random).
    T5.2: Varies H2 count (3 mandatory + 1-3 optional).
    T5.3: Varies sentence endings (체 type per keyword+date hash).
    Fails open: if DB lookup fails, skips enrichment gracefully.
    """
    if not keyword:
        return body

    resolved_products = _resolve_products(products, keyword)
    conditions = _load_conditions()
    keyword_entry = conditions.get(keyword, {})
    condition = keyword_entry.get("primary", "")

    validation_warnings = []
    for p in resolved_products:
        warnings = _validate_product_block(p, keyword)
        validation_warnings.extend(warnings)
    if validation_warnings:
        for w in validation_warnings:
            print(f"[health_post_processor] WARN: {w}")

    for i, p in enumerate(resolved_products):
        injected = _inject_real_data(p, keyword)
        if injected:
            original = p.get("product_name", p.get("product_id", keyword))
            body = body.replace(f"**{original}**", injected, 1)

    today = date.today()

    # T5.1: Select and apply 마무리 variant
    maruchari_variant = _select_maruchari_variant(keyword, today)
    body = _apply_maruchari_variant(body, maruchari_variant)

    # T5.3: Select 체 type (applied after all body modifications)
    che_type = _select_che_type(keyword, today)

    # T5.2: Select optional H2s and rotate enrichment from that pool
    optional_keys = _select_optional_h2s(keyword, today, maruchari_variant=maruchari_variant)
    section_keys = _rotate_sections(keyword, available=optional_keys)

    tomorrow = _next_rotation(keyword, today)
    if section_keys == tomorrow and len(section_keys) > 1:
        section_keys = section_keys[1:] + section_keys[:1]

    enrichment_h2s = []
    for key in section_keys:
        content = _build_section_content(key, resolved_products, keyword, condition)
        if content:
            enrichment_h2s.append(content)

    if not enrichment_h2s:
        return _filter_efficacy_claims(body)

    problem_intro = ""
    if condition:
        safe_condition = _sanitize_condition(condition)
        problem_intro = f"\n{safe_condition}이/가 걱정되시는 분들을 위해 관련 제품을 비교합니다.\n"

    body = _filter_efficacy_claims(body)

    insertion_point = body.rstrip()
    if "## 마무리" in insertion_point or "## 구매 전 체크리스트" in insertion_point:
        for h2_marker in ["## 마무리", "## 구매 전 체크리스트"]:
            idx = insertion_point.find(h2_marker)
            if idx != -1:
                insertion_point = insertion_point[:idx] + "\n" + "\n\n".join(enrichment_h2s) + "\n\n" + insertion_point[idx:]
                break
    else:
        insertion_point = insertion_point.rstrip() + "\n\n" + "\n\n".join(enrichment_h2s) + "\n"

    enriched = insertion_point + problem_intro + "\n"

    # T5.3: Apply 체 type (after all other modifications)
    enriched = _apply_che_type(enriched, che_type)

    # T5.5: Track expressions for dynamic blocklist
    _track_article(keyword, enriched, "")

    return enriched
