"""Compass health claim scanner — independent compliance checker.

Reimplemented from scripts/health_claim_scan.py for compass isolation.
Scans body text for forbidden efficacy claim patterns.
"""

import re

FORBIDDEN_PATTERNS = [
    ("개선됩니다", "efficacy claim: 개선됩니다"),
    ("향상됩니다", "efficacy claim: 향상됩니다"),
    ("효과가 있습니다", "efficacy claim: 효과가 있습니다"),
    ("치료", "efficacy claim: 치료"),
    ("예방", "efficacy claim: 예방"),
    ("완화", "efficacy claim: 완화"),
]


def scan(text: str) -> list:
    """Scan text for forbidden health claim patterns.

    Returns list of tuples (description, pattern, line_number, line_text).
    """
    violations = []
    lines = text.split("\n")
    for line_num, line in enumerate(lines, 1):
        for pattern, description in FORBIDDEN_PATTERNS:
            if pattern in line:
                violations.append((description, pattern, line_num, line.strip()))
    return violations


def scan_file(filepath: str) -> list:
    """Scan a file for forbidden health claim patterns."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return scan(text)


def is_pass(violations: list) -> bool:
    """Return True if no violations."""
    return len(violations) == 0


def format_report(filepath: str, violations: list) -> str:
    """Format scan results as human-readable report."""
    status = "PASS" if is_pass(violations) else "FAIL"
    lines = [f"File: {filepath}", f"Status: {status}", f"Violations: {len(violations)}"]
    for desc, pattern, line_num, line_text in violations:
        lines.append(f"  L{line_num}: [{pattern}] {desc}")
    return "\n".join(lines)
