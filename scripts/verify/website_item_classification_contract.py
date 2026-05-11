#!/usr/bin/env python3
"""Dry-run/apply explicit LT Website Item ecommerce classifications.

Examples:
  python scripts/verify/website_item_classification_contract.py
  python scripts/verify/website_item_classification_contract.py --apply
  python scripts/verify/website_item_classification_contract.py --json
  python scripts/verify/website_item_classification_contract.py --report output/website-item-classification-phase-2.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.website_item_classification_contract.run"
ROOT = Path(__file__).resolve().parents[2]


class ClassificationContractFail(Exception):
    pass


def bench_execute(*, apply: bool) -> dict[str, Any]:
    cmd = ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD]
    if apply:
        # Frappe's bench execute evals --kwargs as a Python literal, not JSON.
        cmd.extend(["--kwargs", "{'apply': True}"])
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=120)
    if proc.returncode != 0:
        raise ClassificationContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise ClassificationContractFail("classification contract returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ClassificationContractFail(f"classification contract returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ClassificationContractFail(
            f"classification contract returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="Apply the exact two-field Website Item classification changes")
    parser.add_argument("--json", action="store_true", help="Print the full JSON report")
    parser.add_argument("--report", help="Write the full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute(apply=args.apply)
    except ClassificationContractFail as exc:
        print(f"[WEBSITE ITEM CLASSIFICATION CONTRACT] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[WEBSITE ITEM CLASSIFICATION CONTRACT] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result)

    return 0 if result.get("ok") else 2


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate


def _print_summary(result: dict[str, Any]) -> None:
    status = "PASS" if result.get("ok") else "FAIL"
    action = result.get("action") or "unknown"
    print(f"[WEBSITE ITEM CLASSIFICATION CONTRACT] {status} ({action})")
    print(f"  expected_total: {result.get('expected_total')}")
    print(f"  matched_count: {result.get('matched_count')}")
    print(f"  desired_counts: {result.get('desired_counts')}")
    print(f"  planned_change_count: {result.get('planned_change_count')}")
    print(f"  applied_change_count: {result.get('applied_change_count')}")
    print(f"  only_mutated_doctype: {result.get('only_mutated_doctype')}")
    print(f"  only_mutated_fields: {result.get('only_mutated_fields')}")
    if result.get("stored_counts_for_targets"):
        print(f"  stored_counts_for_targets: {result.get('stored_counts_for_targets')}")
    if result.get("missing"):
        print(f"  missing: {result.get('missing')}")
    if result.get("ambiguous"):
        print(f"  ambiguous: {result.get('ambiguous')}")
    if result.get("failures"):
        for failure in result.get("failures") or []:
            print(f"  - {failure}")
    print(f"  reversal_note: {result.get('reversal_note')}")


if __name__ == "__main__":
    sys.exit(main())
