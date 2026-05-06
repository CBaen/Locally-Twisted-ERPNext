#!/usr/bin/env python3
"""Review unpaid/overdue invoices without sending reminders or mutating accounting.

Run:
  python scripts/verify/unpaid_invoice_review.py
  python scripts/verify/unpaid_invoice_review.py --json
  python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json
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
METHOD = "locally_twisted.paperwork.unpaid_invoice_review.run"
ROOT = Path(__file__).resolve().parents[2]


class UnpaidInvoiceReviewFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise UnpaidInvoiceReviewFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise UnpaidInvoiceReviewFail("unpaid invoice review returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UnpaidInvoiceReviewFail(f"unpaid invoice review returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise UnpaidInvoiceReviewFail(f"unpaid invoice review returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except UnpaidInvoiceReviewFail as exc:
        print(f"[UNPAID INVOICE REVIEW] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[UNPAID INVOICE REVIEW] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result)

    return 0 if result.get("ok") else 1


def _print_summary(result: dict[str, Any]) -> None:
    print("[UNPAID INVOICE REVIEW] " + ("PASS" if result.get("ok") else "FAIL"))
    print(f"  generated_at: {result.get('generated_at')}")
    print(f"  read_only: {result.get('read_only')}")
    print(f"  send_allowed: {result.get('send_allowed')}")
    print(f"  mutation_allowed: {result.get('mutation_allowed')}")
    print(f"  candidate_count: {len(result.get('review_candidates') or [])}")

    priority_counts = result.get("priority_counts") or {}
    if priority_counts:
        print(f"  priority_counts: {priority_counts}")

    for candidate in (result.get("review_candidates") or [])[:8]:
        print(
            "    - {invoice}: {customer} | {priority} | balance {balance} | docs {docs}".format(
                invoice=candidate.get("invoice"),
                customer=candidate.get("customer_name") or candidate.get("customer"),
                priority=candidate.get("priority"),
                balance=candidate.get("balance_due"),
                docs=", ".join(candidate.get("draft_document_ids") or []),
            )
        )

    failures = result.get("failures") or []
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
