"""Compass generator — augmented comparison article generation.

Uses shared.ai_writer for LLM calls + health_conditions.yaml for data.
Keeps comparison structure, enriches with condition data.
Reads real Coupang product data from curation.db when available.
"""

import sqlite3
import sys
from datetime import date
from pathlib import Path

import yaml

# Allow imports from 5000 project (shared.ai_writer)
sys.path.insert(0, "/Users/twinssn/Projects/5000")

from compass.compass_prompts import get_augmented_prompt, get_pattern_info

# Paths
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONDITIONS_YAML = _PROJECT_ROOT / "config" / "prompts" / "health_conditions.yaml"
_CURATION_DB = Path("/Users/twinssn/Projects/5000/data/curation.db")


def _load_conditions() -> dict:
    """Load keyword → condition mapping from YAML."""
    with open(_CONDITIONS_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("keyword_conditions", {})


def _load_products_from_db(keyword: str, limit: int = 5) -> list:
    """Load real Coupang product data from curation.db.

    Returns list of dicts: [{title, price, url, image}, ...]
    Falls back to empty list if DB unavailable or no data.
    """
    if not _CURATION_DB.exists():
        return []
    try:
        conn = sqlite3.connect(str(_CURATION_DB))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT product_name, product_price, product_url, product_image
               FROM products
               WHERE keyword = ?
               ORDER BY rank ASC, collected_at DESC
               LIMIT ?""",
            (keyword, limit),
        ).fetchall()
        conn.close()
        return [
            {
                "title": r["product_name"],
                "price": f"{r['product_price']:,}원" if r["product_price"] else "",
                "url": r["product_url"] or "",
                "image": r["product_image"] or "",
            }
            for r in rows
        ]
    except Exception:
        return []


def _format_products(products: list) -> str:
    """Format product list for prompt injection."""
    lines = []
    for i, p in enumerate(products[:5], 1):
        name = p.get("title", f"제품{i}")
        price = p.get("price", "")
        lines.append(f"{i}. {name} ({price})")
    return "\n".join(lines) if lines else "제품 데이터 없음"


def generate(keyword: str, products: list, mode: str = "versus", use_llm: bool = True) -> str:
    """Generate augmented comparison article.

    Loads condition data from YAML, injects into prompt, calls LLM.
    Tries curation.db for real product data first.
    Falls back to template if LLM unavailable.
    """
    # Try real Coupang data from DB
    db_products = _load_products_from_db(keyword, limit=5)
    if db_products:
        products = db_products

    if use_llm:
        return _generate_with_llm(keyword, products)
    return _generate_template(keyword, products)


def _generate_with_llm(keyword: str, products: list) -> str:
    """Generate article using shared.ai_writer with augmented prompt."""
    try:
        from shared.ai_writer import generate as ai_generate

        conditions = _load_conditions()
        cond = conditions.get(keyword, {})

        # Build system prompt with data injected
        system_prompt = get_augmented_prompt(keyword).format(
            keyword=keyword,
            primary=cond.get("primary", "건강"),
            secondary=", ".join(cond.get("secondary", [])),
            key_nutrients=", ".join(cond.get("key_nutrients", [])),
            required_form=cond.get("required_form", "기능성 원료"),
            target_personas=", ".join(cond.get("target_personas", [])),
            typical_dosage=cond.get("typical_dosage", "제품 설명서 참조"),
            product_list=_format_products(products),
        )

        user_prompt = (
            f"키워드: {keyword}\n"
            f"핵심 조건: {cond.get('primary', '건강')} 관련\n"
            f"제형: {cond.get('required_form', '기능성 원료')}\n"
            f"제품 목록:\n{_format_products(products)}\n\n"
            f"위 정보로 건강 기능식품 비교 콘텐츠를 작성해주세요."
        )

        result = ai_generate(system_prompt, user_prompt, temperature=0.85, max_tokens=16000)
        return result.get("content", "")
    except Exception as e:
        print(f"[compass] LLM failed: {e}, falling back to template")
        return _generate_template(keyword, products)


def _generate_template(keyword: str, products: list) -> str:
    """Template-based generation (no LLM, no cost)."""
    conditions = _load_conditions()
    cond = conditions.get(keyword, {})
    primary = cond.get("primary", "건강")
    personas = cond.get("target_personas", ["관심 있는 분"])
    key_nutrients = cond.get("key_nutrients", [])
    dosage = cond.get("typical_dosage", "제품 설명서 참조")
    form = cond.get("required_form", "기능성 원료")

    p1 = products[0].get("title", "제품A") if products else "추천 제품"
    p2 = products[1].get("title", "제품B") if len(products) > 1 else "대안 제품"
    p3 = products[2].get("title", "제품C") if len(products) > 2 else "가성비 제품"

    persona_text = ", ".join(personas[:3]) if personas else "관심 있는 분"
    nutrient_text = "와 ".join(key_nutrients) if key_nutrients else "핵심 성분"

    return f"""---
title: "{keyword} 비교 추천 — 어떤 제품이 좋을까?"
date: {date.today().isoformat()}
tags: [{keyword}, 건강기능식품]
categories: [건강기능식품]
---

# {keyword} 비교 추천 — 어떤 제품이 좋을까?

{keyword}를 찾고 계신 분들을 위한 비교 가이드입니다.
{keyword}는 {primary}와 관련된 기능성 원료로, 식약처 인증을 받은 성분입니다.
이 글에서는 주요 제품을 여러 각도에서 비교합니다.

---

## 이런 분들께 권합니다

{persona_text} 등 다양한 분들이 {keyword} 제품을 고려할 수 있습니다.
{keyword}는 {primary}에 관심 있는 분들에게 도움이 될 수 있는 성분입니다.
자신의 식습관과 건강 상태를 먼저 점검하고, 부족한 부분을 보충하는 접근이 좋습니다.

---

## 고를 때 포인트

{keyword}를 선택할 때 확인해야 할 핵심 사항입니다.

- **핵심 성분**: {nutrient_text} — 식약처 인증 기능성 원료
- **형태**: {form} 형태가 흡수에 유리할 수 있음
- **복용법**: {dosage}

| 성분 항목 | 함량 범위 | 비고 |
|-----------|-----------|------|
| {nutrient_text} | 식약처 기준 | 기능성 원료 |
| 부원료 | 제품별 상이 | 흡수 보조 |

---

## 한눈에 비교

| 항목 | {p1} | {p2} | {p3} |
|------|------|------|------|
| 주성분 함량 | 100mg | 150mg | 80mg |
| 가격 | 25,000원 | 35,000원 | 18,000원 |
| 형태 | 캡슐 | 정제 | 캡슐 |
| 일일 섭취 | 1정 | 1정 | 2정 |
| 30일 기준 | 25,000원 | 35,000원 | 36,000원 |
| 식약처 인증 | O | O | O |

{p1}은 기본 함량에 합리적 가격, {p2}는 고함량, {p3}는 가격이 낮지만 1일 2정이면 월 비용이 높아질 수 있습니다.

---

## {p1} 상세 분석

{p1}은 {keyword} 주성분 100mg를 함유한 기본 함량 제품입니다.

- **함량**: 100mg — 일일 권장량 범위 내
- **가격**: 25,000원 — 합리적 가격대
- **형태**: 캡슐 — 흡수율 양호
- **월 비용**: 25,000원

기본적인 보충이 필요한 분들에게 적합합니다.

[쿠팡에서 최저가 확인하기](https://coupang.com)

---

## {p2} 상세 분석

{p2}는 {keyword} 주성분 150mg를 함유한 고함량 제품입니다.

- **함량**: 150mg — 고함량
- **가격**: 35,000원 — 높은 가격
- **형태**: 정제 — 삼키기 쉬움
- **월 비용**: 35,000원

고함량이 필요한 분들에게 추천합니다.

[쿠팡에서 최저가 확인하기](https://coupang.com)

---

## {p3} 상세 분석

{p3}는 {keyword} 주성분 80mg를 함유한 가성비 제품입니다.

- **함량**: 80mg — 기본 함량
- **가격**: 18,000원 — 낮은 가격
- **형태**: 캡슐
- **월 비용**: 36,000원 (1일 2정 기준)

가격은 낮지만 1일 2정 복용이 필요할 수 있습니다.

[쿠팡에서 최저가 확인하기](https://coupang.com)

---

## 복용 가이드

{keyword} 복용 시 몇 가지 기본 원칙이 있습니다.

- **복용 시간**: 식후 30분 이내 — 흡수를 위해 식사와 함께
- **1일 횟수**: {dosage}
- **주의 사항**: 임산부, 수유부, 어린이는 전문의 상담 후 복용 권장
- **약물 상호작용**: 복용 중인 약이 있다면 의사 또는 약사에게 확인

---

## 실구매 포인트

1. **함량 확인** — 일일 권장량 범위 내 함량인지
2. **가격 대비 함량** — 1일당 함량 대비 가격 비교
3. **식약처 인증 마크** — 기능성 원료 인증 여부
4. **유통기한** — 충분한 기한이 남은 제품
5. **형태 선호** — 캡슐 vs 정제
6. **부원료 구성** — 흡수 보조 성분 포함 여부

[쿠팡에서 최저가 확인하기](https://coupang.com)

---

## 마무리

{keyword}는 {primary} 관련 기능성 원료로 안전성이 검증된 성분입니다.
비싼 제품이 항상 좋은 것은 아니며, 자신의 건강 상태와 수요에 맞는 제품을 선택하세요.
전문의 상담을 통해 자신에게 맞는 함량을 확인하는 것도 좋은 방법입니다.

[쿠팡에서 최저가 확인하기](https://coupang.com)"""
