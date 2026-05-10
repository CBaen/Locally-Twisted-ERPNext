#!/usr/bin/env python3
"""Render the internal product quote operator-review report."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.product_quote_operator_review.run"
ROOT = Path(__file__).resolve().parents[2]


class ReviewFail(Exception):
    pass


def bench_execute(limit: int) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            METHOD,
            "--kwargs",
            json.dumps({"limit": limit}),
        ],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise ReviewFail(f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    text = proc.stdout.strip()
    if not text:
        raise ReviewFail("product quote operator review returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ReviewFail(f"product quote operator review returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ReviewFail(f"product quote operator review returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20, help="Maximum product quote Quotations to review")
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute(limit=args.limit)
    except ReviewFail as exc:
        print(f"[PRODUCT QUOTE OPERATOR REVIEW] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[PRODUCT QUOTE OPERATOR REVIEW] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        print("[PRODUCT QUOTE OPERATOR REVIEW] " + ("PASS" if result.get("ok") else "FAIL"))
        print(f"  review_count: {result.get('review_count')}")
        print(f"  ready_count: {result.get('ready_count')}")
        print(f"  blocked_count: {result.get('blocked_count')}")
        for review in result.get("reviews") or []:
            print(
                "    - "
                f"{review.get('quotation')}: {review.get('status')} "
                f"({len(review.get('blockers') or [])} blocker(s))"
            )
        failures = result.get("failures") or []
        if failures:
            print("  failures:")
            for failure in failures:
                print(f"    - {failure}")

    return 0 if result.get("ok") else 1


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
