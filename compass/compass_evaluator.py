"""Compass evaluator — auto-evaluate generated articles.

5 checks:
1. Compliance: forbidden efficacy patterns
2. Entropy: H2 section diversity
3. Affiliate: affiliate link presence
4. Length: word count 2500+ chars
5. Similarity: H2 overlap with other modes
"""

import json
import math
import re
from collections import Counter
from pathlib import Path

from compass.compass_claim_scanner import scan


def evaluate(body: str, keyword: str, mode: str) -> dict:
    """Run all 5 checks and return evaluation result."""
    compliance = _check_compliance(body)
    entropy = _check_entropy(body)
    affiliate = _check_affiliate(body)
    length = _check_length(body)
    similarity = _check_similarity(body, mode)

    all_pass = all([compliance["pass"], affiliate["pass"], length["pass"]])
    entropy_pass = entropy["value"] >= 2.34
    overall = all_pass and entropy_pass

    return {
        "keyword": keyword,
        "mode": mode,
        "overall": "PASS" if overall else "FAIL",
        "checks": {
            "compliance": compliance,
            "entropy": entropy,
            "affiliate": affiliate,
            "length": length,
            "similarity": similarity,
        },
        "word_count": length["chars"],
        "h2_count": entropy["h2_count"],
    }


def _check_compliance(body: str) -> dict:
    """Check for forbidden health claim patterns."""
    violations = scan(body)
    return {
        "pass": len(violations) == 0,
        "violations": len(violations),
        "details": [(v[0], v[2]) for v in violations],
    }


def _check_entropy(body: str) -> dict:
    """Check H2 section diversity (entropy)."""
    h2s = re.findall(r"^## (.+)$", body, re.MULTILINE)
    h2_count = len(h2s)

    if h2_count < 2:
        return {"pass": False, "value": 0.0, "h2_count": h2_count, "unique": 0}

    counter = Counter(h2s)
    total = sum(counter.values())
    probs = [c / total for c in counter.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)

    return {
        "pass": entropy >= 2.34,
        "value": round(entropy, 3),
        "h2_count": h2_count,
        "unique": len(counter),
    }


def _check_affiliate(body: str) -> dict:
    """Check affiliate link presence."""
    has_link = "쿠팡" in body or "AFFILIATE_LINK" in body or "coupang" in body
    return {"pass": has_link, "affiliate_links": body.count("쿠팡")}


def _check_length(body: str) -> dict:
    """Check content length (2500+ chars)."""
    # Remove frontmatter
    clean = re.sub(r"^---.*?---", "", body, flags=re.DOTALL).strip()
    chars = len(clean)
    return {"pass": chars >= 2500, "chars": chars, "target": "2500+"}


def _check_similarity(body: str, mode: str) -> dict:
    """Check H2 overlap with other modes (lower is better)."""
    h2s = set(re.findall(r"^## (.+)$", body, re.MULTILINE))

    # Reference H2 sets per mode
    ref_h2s = {
        "ingredient_dive": {"성분 심층", "복용 가이드", "제품 비교"},
        "symptom_care": {"상황별 추천 제품", "원인과 배경", "생활습관"},
        "versus": {"한눈에 비교", "제품별 상세", "실구매 포인트"},
    }

    other_modes = [m for m in ref_h2s if m != mode]
    overlaps = []
    for om in other_modes:
        overlap = h2s & ref_h2s[om]
        if overlap:
            overlaps.append({"mode": om, "shared_h2s": list(overlap)})

    return {"other_mode_overlaps": overlaps, "unique_h2s": len(h2s)}


def format_report(result: dict) -> str:
    """Format evaluation result as human-readable report."""
    lines = [
        "=== COMPASS EVALUATION ===",
        f"Keyword: {result['keyword']}",
        f"Mode: {result['mode']}",
        f"Overall: {result['overall']}",
        f"Word count: {result['word_count']}",
        f"H2 count: {result['h2_count']}",
        "",
    ]

    for name, check in result["checks"].items():
        status = "PASS" if check.get("pass", True) else "FAIL"
        extra = ""
        if name == "entropy":
            extra = f" (entropy={check['value']}, unique={check.get('unique', 0)})"
        elif name == "compliance":
            extra = f" (violations={check['violations']})"
        elif name == "length":
            extra = f" ({check['chars']} chars)"
        elif name == "affiliate":
            extra = f" (links={check['affiliate_links']})"
        lines.append(f"  [{status}] {name}{extra}")

    lines.append("==========================")
    return "\n".join(lines)


def save_evaluation(result: dict, output_dir: Path):
    """Save evaluation result as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    keyword = result["keyword"]
    mode = result["mode"]
    filepath = output_dir / f"{keyword}_{mode}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return filepath
