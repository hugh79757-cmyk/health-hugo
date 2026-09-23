#!/usr/bin/env python3
"""Compass Runner — standalone CLI for compass writing modes.

Usage:
    python compass/compass_runner.py --keyword 루테인 --mode versus
    python compass/compass_runner.py --keyword 루테인 --mode all
    python compass/compass_runner.py --keyword 루테인 --mode all --real-llm
    python compass/compass_runner.py --evaluate compass/output/drafts/

Safe: no publish, no DB writes, no scheduler integration.
Output: compass/output/drafts/ and compass/output/evaluated/
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Setup paths — ensure parent dir is on sys.path so "compass.xxx" imports resolve
COMPASS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = COMPASS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))  # health-hugo/
sys.path.insert(0, "/Users/twinssn/Projects/5000")  # 5000/ for shared.ai_writer

from compass.compass_generator import generate
from compass.compass_post_processor import process_article
from compass.compass_evaluator import evaluate, format_report, save_evaluation
from compass.compass_claim_scanner import scan

OUTPUT_DRAFTS = COMPASS_DIR / "output" / "drafts"
OUTPUT_EVAL = COMPASS_DIR / "output" / "evaluated"
MODES = ["ingredient_dive", "symptom_care", "versus"]


def load_keyword_products(keyword: str) -> list:
    """Load mock product data for a keyword."""
    # In production, this would query the enrichment DB
    return [
        {"title": f"{keyword} 추천 제품 A", "price": "25,000원"},
        {"title": f"{keyword} 추천 제품 B", "price": "35,000원"},
        {"title": f"{keyword} 추천 제품 C", "price": "18,000원"},
    ]


def run_single(keyword: str, mode: str, use_llm: bool = False) -> dict:
    """Generate + process + evaluate a single article."""
    print(f"\n{'='*50}")
    print(f"[compass] Generating: {keyword} / {mode}")
    print(f"{'='*50}")

    products = load_keyword_products(keyword)

    # Generate
    body = generate(keyword, products, mode, use_llm=use_llm)
    print(f"  Generated: {len(body)} chars")

    # Log pattern info
    from compass.compass_prompts import get_pattern_info
    pi = get_pattern_info(keyword)
    print(f"  Pattern: {pi['key']} ({pi['description']})")

    # Post-process
    body = process_article(body, keyword, products, mode)
    print(f"  Processed: {len(body)} chars")

    # Evaluate
    result = evaluate(body, keyword, mode)
    print(format_report(result))

    # Save draft
    OUTPUT_DRAFTS.mkdir(parents=True, exist_ok=True)
    draft_path = OUTPUT_DRAFTS / f"{keyword}_{mode}.md"
    draft_path.write_text(body, encoding="utf-8")
    print(f"  Draft saved: {draft_path}")

    # Save evaluation
    eval_path = save_evaluation(result, OUTPUT_EVAL)
    print(f"  Eval saved: {eval_path}")

    return result


def run_evaluate(drafts_dir: str):
    """Evaluate all drafts in a directory."""
    drafts_path = Path(drafts_dir)
    if not drafts_path.exists():
        print(f"ERROR: Directory not found: {drafts_dir}")
        sys.exit(1)

    results = []
    for md_file in sorted(drafts_path.glob("*.md")):
        body = md_file.read_text(encoding="utf-8")
        # Extract keyword and mode from filename: {keyword}_{mode}.md
        # Mode may contain underscores (ingredient_dive, symptom_care)
        stem = md_file.stem
        keyword = "unknown"
        mode = "versus"
        for m in MODES:
            if stem.endswith("_" + m):
                keyword = stem[: -(len(m) + 1)]
                mode = m
                break

        result = evaluate(body, keyword, mode)
        results.append(result)
        print(format_report(result))

        eval_path = save_evaluation(result, OUTPUT_EVAL)
        print(f"  Saved: {eval_path}\n")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["overall"] == "PASS")
    print(f"\n{'='*50}")
    print(f"Summary: {passed}/{total} PASS")
    print(f"{'='*50}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Compass Runner — standalone writing mode CLI")
    parser.add_argument("--keyword", help="Keyword to process")
    parser.add_argument("--mode", choices=MODES + ["all"], default="versus",
                        help="Writing mode (default: versus)")
    parser.add_argument("--real-llm", action="store_true", help="Use real LLM (costs API credits)")
    parser.add_argument("--evaluate", metavar="DIR", help="Evaluate all drafts in directory")
    args = parser.parse_args()

    if args.evaluate:
        run_evaluate(args.evaluate)
        return

    if not args.keyword:
        print("ERROR: --keyword is required (or use --evaluate DIR)")
        sys.exit(1)

    if args.mode == "all":
        modes = MODES
    else:
        modes = [args.mode]

    results = []
    for mode in modes:
        result = run_single(args.keyword, mode, use_llm=args.real_llm)
        results.append(result)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["overall"] == "PASS")
    print(f"\n{'='*50}")
    print(f"[compass] Summary: {passed}/{total} PASS")
    for r in results:
        status = "PASS" if r["overall"] == "PASS" else "FAIL"
        print(f"  [{status}] {r['keyword']} / {r['mode']} (entropy={r['checks']['entropy']['value']}, chars={r['word_count']})")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
