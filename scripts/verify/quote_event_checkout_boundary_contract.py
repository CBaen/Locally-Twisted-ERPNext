#!/usr/bin/env python3
"""Run the LT Phase 4 quote/event checkout boundary contract inside ERPNext."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.quote_event_checkout_boundary_contract.run"
ROOT = Path(__file__).resolve().parents[2]


class ContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise ContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise ContractFail("quote/event checkout boundary contract returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"quote/event checkout boundary contract returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ContractFail(f"quote/event checkout boundary contract returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except ContractFail as exc:
        print(f"[QUOTE/EVENT CHECKOUT BOUNDARY CONTRACT] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, sort_keys=True, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[QUOTE/EVENT CHECKOUT BOUNDARY CONTRACT] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        print("[QUOTE/EVENT CHECKOUT BOUNDARY CONTRACT] " + ("PASS" if result.get("ok") else "FAIL"))
        print(f"  quote_first_count: {result.get('quote_first_count')}")
        print(f"  needs_review_count: {result.get('needs_review_count')}")
        print(f"  cart_api_blocked_count: {result.get('cart_api_blocked_count')}")
        print(f"  direct_checkout_url_blocked_count: {result.get('direct_checkout_url_blocked_count')}")
        print(f"  stale_localstorage_blocked_count: {result.get('stale_localstorage_blocked_count')}")
        print(f"  no_sellable_candidate_count: {result.get('no_sellable_candidate_count')}")
        if result.get("rolled_back"):
            print("  rollback: verifier rolled back and created no business records")
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
