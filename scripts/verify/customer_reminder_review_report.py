#!/usr/bin/env python3
"""Render the no-live customer reminder review report.

Run:
  python scripts/verify/customer_reminder_review_report.py
  python scripts/verify/customer_reminder_review_report.py --json
  python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json
  python scripts/verify/customer_reminder_review_report.py --markdown output/customer-reminder-review-report.md
  python scripts/verify/customer_reminder_review_report.py --csv output/customer-reminder-review-report.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.paperwork.customer_reminder_review_report.run"
ROOT = Path(__file__).resolve().parents[2]


class CustomerReminderReviewReportFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise CustomerReminderReviewReportFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise CustomerReminderReviewReportFail("customer reminder review report returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CustomerReminderReviewReportFail(
            f"customer reminder review report returned non-JSON output: {text}"
        ) from exc
    if not isinstance(parsed, dict):
        raise CustomerReminderReviewReportFail(
            f"customer reminder review report returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    parser.add_argument("--markdown", help="Write human-readable markdown report")
    parser.add_argument("--csv", help="Write rows to CSV")
    args = parser.parse_args()

    try:
        result = bench_execute()
        failures = _contract_failures(result)
    except CustomerReminderReviewReportFail as exc:
        print(f"[CUSTOMER REMINDER REVIEW REPORT] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[CUSTOMER REMINDER REVIEW REPORT] wrote {report_path.relative_to(ROOT)}")

    if args.markdown:
        markdown_path = _rooted(args.markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(_markdown(result), encoding="utf-8")
        print(f"[CUSTOMER REMINDER REVIEW REPORT] wrote {markdown_path.relative_to(ROOT)}")

    if args.csv:
        csv_path = _rooted(args.csv)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        _write_csv(csv_path, result)
        print(f"[CUSTOMER REMINDER REVIEW REPORT] wrote {csv_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result, failures)

    return 0 if result.get("ok") and not failures else 1


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result.get("read_only") is not True:
        failures.append("report is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("report allows customer sending")
    if result.get("mutation_allowed") is not False:
        failures.append("report allows accounting mutations")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("report enables customer delivery")
    if result.get("automatic_delivery_enabled") is not False:
        failures.append("report enables automatic delivery")
    if result.get("report_type") != "customer_reminder_review_report":
        failures.append("report_type is not customer_reminder_review_report")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("mutation guard changed while rendering report")
    columns = {column.get("fieldname") for column in result.get("columns") or []}
    for fieldname in ("invoice", "customer_name", "recommended_cadence", "send_status", "blocked_customer_send_until"):
        if fieldname not in columns:
            failures.append(f"missing report column {fieldname}")
    for row in result.get("rows") or []:
        if row.get("delivery_mode") != "internal_review_only":
            failures.append(f"{row.get('invoice')} report row is not internal-review-only")
        if row.get("send_status") != "draft_only_not_sent":
            failures.append(f"{row.get('invoice')} report row is not draft-only")
        if row.get("customer_delivery_enabled") is not False:
            failures.append(f"{row.get('invoice')} report row enables customer delivery")
    return failures


def _print_summary(result: dict[str, Any], contract_failures: list[str]) -> None:
    print("[CUSTOMER REMINDER REVIEW REPORT] " + ("PASS" if result.get("ok") and not contract_failures else "FAIL"))
    print(f"  generated_at: {result.get('generated_at')}")
    print(f"  report_type: {result.get('report_type')}")
    print(f"  send_allowed: {result.get('send_allowed')}")
    print(f"  customer_delivery_enabled: {result.get('customer_delivery_enabled')}")
    summary = result.get("summary") or {}
    print(f"  row_count: {summary.get('row_count')}")
    print(f"  review_now_count: {summary.get('review_now_count')}")
    print(f"  hold_count: {summary.get('hold_count')}")
    for row in result.get("rows") or []:
        print(
            "    - "
            f"{row.get('invoice')}: {row.get('customer_name')} | "
            f"{row.get('recommended_cadence')} | {row.get('send_status')}"
        )
    failures = list(result.get("failures") or []) + contract_failures
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _markdown(result: dict[str, Any]) -> str:
    summary = result.get("summary") or {}
    lines = [
        "# Customer Reminder Review Report",
        "",
        f"- generated_at: {result.get('generated_at')}",
        f"- report_type: {result.get('report_type')}",
        f"- send_allowed: {result.get('send_allowed')}",
        f"- customer_delivery_enabled: {result.get('customer_delivery_enabled')}",
        f"- row_count: {summary.get('row_count')}",
        f"- review_now_count: {summary.get('review_now_count')}",
        f"- hold_count: {summary.get('hold_count')}",
        "",
        "| Invoice | Customer | Days Overdue | Balance | Cadence | Send Status | Blocked Until |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for row in result.get("rows") or []:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.get("invoice") or ""),
                    str(row.get("customer_name") or ""),
                    str(row.get("days_overdue") or 0),
                    str(row.get("balance_due") or ""),
                    str(row.get("recommended_cadence") or ""),
                    str(row.get("send_status") or ""),
                    str(row.get("blocked_customer_send_until") or ""),
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _write_csv(path: Path, result: dict[str, Any]) -> None:
    fieldnames = [column["fieldname"] for column in result.get("columns") or []]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in result.get("rows") or []:
            writer.writerow(row)


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
