"""Compass post-processor — independent article post-processing.

NOT a copy of health_post_processor.py.
Designed specifically for compass modes with simpler, mode-aware logic.
"""

import re
from datetime import date


def process_article(body: str, keyword: str, products: list, mode: str = "versus") -> str:
    """Post-process generated article body.

    Steps:
    1. Sanitize forbidden efficacy claims
    2. Ensure affiliate link placeholders exist
    3. Add enrichment H2s if missing (mode-aware pool)
    4. Clean whitespace
    """
    body = _sanitize_efficacy(body)
    body = _ensure_affiliate_links(body, keyword)
    body = _enrich_h2s(body, keyword, mode)
    body = _clean_whitespace(body)
    return body


FORBIDDEN = ["치료", "개선", "향상", "예방", "완화", "효과가 있습니다"]

SANITIZE_MAP = {
    "혈행개선": "혈행",
    "체력개선": "체력",
    "수면개선": "수면",
    "빈혈예방": "빈혈",
}


def _sanitize_efficacy(text: str) -> str:
    """Remove forbidden efficacy claims."""
    for key, val in SANITIZE_MAP.items():
        text = text.replace(key, val)
    for claim in FORBIDDEN:
        text = re.sub(re.escape(claim), "", text)
    return text


def _ensure_affiliate_links(body: str, keyword: str) -> str:
    """Ensure body contains at least one affiliate link."""
    if "[AFFILIATE_LINK]" in body or "쿠팡" in body:
        return body
    # Add affiliate CTA before closing
    closing_marker = "## 마무리"
    if closing_marker in body:
        body = body.replace(
            closing_marker,
            "[쿠팡에서 최저가 확인하기](https://coupang.com)\n\n"
            "## 마무리",
        )
    return body


# Mode-aware optional H2 pools
_OPTIONAL_POOLS = {
    "ingredient_dive": [
        "흡수율과 생체이용률",
        "주의할 점",
        "성분 조합 팁",
        "가격대 분석",
        "도입부 보충",
    ],
    "symptom_care": [
        "원인부터 짚어보기",
        "생활습관 체크리스트",
        "도입부 보충",
        "가격대 분석",
    ],
    "versus": [
        "성분 심층",
        "복용 가이드",
        "실구매 포인트",
        "이런 분께 추천",
        "가격대 분석",
        "도입부 보충",
    ],
}


def _enrich_h2s(body: str, keyword: str, mode: str) -> str:
    """Add optional H2 sections if missing. Mode-aware pool selection."""
    pool = _OPTIONAL_POOLS.get(mode, _OPTIONAL_POOLS["versus"])
    existing_h2s = re.findall(r"^## (.+)$", body, re.MULTILINE)

    lines = body.split("\n")
    # Find the last H2 before closing
    insert_idx = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("## "):
            insert_idx = i
            break

    added = 0
    for h2 in pool:
        if added >= 2:
            break
        if h2 not in " ".join(existing_h2s):
            lines.insert(insert_idx, f"\n## {h2}\n")
            lines.insert(insert_idx + 1, f"{keyword}에 대한 추가 정보를 정리했습니다.\n")
            insert_idx += 3
            added += 1

    return "\n".join(lines)


def _clean_whitespace(text: str) -> str:
    """Normalize whitespace."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()
