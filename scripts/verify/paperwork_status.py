#!/usr/bin/env python3
"""Read-only paperwork/backend status report.

Run:
  python scripts/verify/paperwork_status.py
  python scripts/verify/paperwork_status.py --json
  python scripts/verify/paperwork_status.py --report output/paperwork-status.json
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
METHOD = "locally_twisted.verify.paperwork_status.run"
ROOT = Path(__file__).resolve().parents[2]


class PaperworkStatusFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise PaperworkStatusFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise PaperworkStatusFail("paperwork status returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PaperworkStatusFail(f"paperwork status returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise PaperworkStatusFail(f"paperwork status returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        report = bench_execute()
    except PaperworkStatusFail as exc:
        print(f"[PAPERWORK STATUS] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(report, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[PAPERWORK STATUS] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(report)
    return 0


def _print_summary(report: dict[str, Any]) -> None:
    counts = report.get("counts") or {}
    invoices = report.get("invoice_review") or {}
    payment_requests = report.get("payment_request_review") or {}
    email_queue = report.get("email_queue_review") or {}
    live = report.get("live_payment_readiness") or {}
    attention = report.get("attention_items") or []

    print("[PAPERWORK STATUS] OK")
    print(f"  generated_at: {report.get('generated_at')}")
    print(f"  sales_orders: {counts.get('Sales Order', 0)}")
    print(f"  sales_invoices: {counts.get('Sales Invoice', 0)}")
    print(f"  unpaid_invoices: {invoices.get('unpaid_count', 0)}")
    print(f"  overdue_invoices: {invoices.get('overdue_count', 0)}")
    print(f"  payment_requests_expected: {payment_requests.get('expected_count', 0)}")
    print(f"  payment_requests_paid: {payment_requests.get('paid_count', 0)}")
    print(f"  email_queue_status_counts: {email_queue.get('status_counts', {})}")
    print(f"  live_payment_ready: {live.get('ok')}")
    if attention:
        print("  attention_items:")
        for item in attention:
            print(f"    - {item}")


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
