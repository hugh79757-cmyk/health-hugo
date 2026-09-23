#!/usr/bin/env python3
"""Dynamic expression tracker for T5.5 — 최근 N편 표현 기록.

Tracks key expressions from recent articles and provides them
to the next generation prompt as avoidance instructions.

Location: scripts/expression_tracker.py
Used by: health_post_processor.py (T5.5 integration point)
"""
import json
import os
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
TRACKER_PATH = PROJECT / ".planning" / "phase5" / "expression_log.json"
TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)

RECENT_N = 5

_FORBIDDEN_EFFICACY = ["치료", "개선", "향상", "예방", "완화", "효과가 있습니다"]


def load_log():
    if TRACKER_PATH.exists():
        try:
            with open(TRACKER_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_log(entries):
    TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def extract_expressions(text: str, n: int = 10) -> list:
    """Extract 10 most common nouns/verbs from text (excluding efficacy claims)."""
    words = re.findall(r"[가-힣]{2,}", text)
    filtered = [w for w in words if w not in _FORBIDDEN_EFFICACY]
    counter = Counter(filtered)
    return [w for w, _ in counter.most_common(n)]


def track_article(keyword: str, body: str, title: str = "") -> dict:
    """Track expressions from one article. Returns the entry."""
    expressions = extract_expressions(body + " " + title)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "keyword": keyword,
        "expressions": expressions,
    }
    log = load_log()
    log.append(entry)
    log = log[-RECENT_N:]
    save_log(log)
    return entry


def get_avoidance_instruction() -> str:
    """Generate avoidance instruction from last N articles' expressions."""
    log = load_log()
    if not log:
        return ""
    all_expressions = []
    for entry in log:
        all_expressions.extend(entry.get("expressions", []))
    unique = list(dict.fromkeys(all_expressions))
    if not unique:
        return ""
    return f"[이 표현들은 최근 {len(log)}편에서 사용했습니다 — 피하라] {', '.join(unique[:10])}"


def get_rolling_expressions() -> list:
    """Return all expressions from last N articles (for verification)."""
    log = load_log()
    all_expressions = []
    for entry in log:
        all_expressions.extend(entry.get("expressions", []))
    return list(dict.fromkeys(all_expressions))


def clear_log():
    """Clear tracker log (for testing)."""
    if TRACKER_PATH.exists():
        TRACKER_PATH.unlink()


if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        clear_log()
        track_article("test_kw", "테스트 제품 비교입니다. 좋은 제품입니다.", "테스트 제목")
        log = load_log()
        assert len(log) == 1, f"Expected 1 entry, got {len(log)}"
        instruction = get_avoidance_instruction()
        assert "피하라" in instruction, f"Instruction missing: {instruction}"
        expressions = get_rolling_expressions()
        assert len(expressions) > 0, "No expressions tracked"
        print(f"Tracker test passed: {len(expressions)} expressions")
    elif "--demo":
        clear_log()
        for i in range(7):
            track_article(f"demo_{i}", f"제품 {i} 비교 결과 좋습니다. 건강에 도움됩니다.", f"제목 {i}")
        instruction = get_avoidance_instruction()
        print(f"Avoidance instruction:\n{instruction}")
        print(f"Log entries: {len(load_log())} (max {RECENT_N})")
