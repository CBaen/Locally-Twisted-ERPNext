#!/usr/bin/env python3
"""Render the no-live customer reminder dry-run queue.

Run:
  python scripts/verify/customer_reminder_dry_run.py
  python scripts/verify/customer_reminder_dry_run.py --json
  python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json
  python scripts/verify/customer_reminder_dry_run.py --markdown output/customer-reminder-dry-run.md
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
METHOD = "locally_twisted.paperwork.customer_reminder_dry_run.run"
ROOT = Path(__file__).resolve().parents[2]


class CustomerReminderDryRunFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise CustomerReminderDryRunFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise CustomerReminderDryRunFail("customer reminder dry run returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CustomerReminderDryRunFail(f"customer reminder dry run returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise CustomerReminderDryRunFail(
            f"customer reminder dry run returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    parser.add_argument("--markdown", help="Write human-readable markdown review queue")
    args = parser.parse_args()

    try:
        result = bench_execute()
        failures = _contract_failures(result)
    except CustomerReminderDryRunFail as exc:
        print(f"[CUSTOMER REMINDER DRY RUN] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[CUSTOMER REMINDER DRY RUN] wrote {report_path.relative_to(ROOT)}")

    if args.markdown:
        markdown_path = _rooted(args.markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(_markdown(result), encoding="utf-8")
        print(f"[CUSTOMER REMINDER DRY RUN] wrote {markdown_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result, failures)

    return 0 if result.get("ok") and not failures else 1


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result.get("read_only") is not True:
        failures.append("dry run is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("dry run allows customer sending")
    if result.get("mutation_allowed") is not False:
        failures.append("dry run allows accounting mutations")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("dry run enables customer delivery")
    if result.get("automatic_delivery_enabled") is not False:
        failures.append("dry run enables automatic delivery")
    if result.get("operating_mode") != "no_live_internal_review":
        failures.append("dry run operating mode is not no_live_internal_review")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("mutation guard changed while rendering dry run")
    for item in result.get("queue_items") or []:
        if item.get("delivery_mode") != "internal_review_only":
            failures.append(f"{item.get('invoice')} queue item is not internal-review-only")
        if item.get("send_status") != "draft_only_not_sent":
            failures.append(f"{item.get('invoice')} queue item is not draft-only")
        if item.get("customer_delivery_enabled") is not False:
            failures.append(f"{item.get('invoice')} queue item enables customer delivery")
    return failures


def _print_summary(result: dict[str, Any], contract_failures: list[str]) -> None:
    print("[CUSTOMER REMINDER DRY RUN] " + ("PASS" if result.get("ok") and not contract_failures else "FAIL"))
    print(f"  generated_at: {result.get('generated_at')}")
    print(f"  operating_mode: {result.get('operating_mode')}")
    print(f"  send_allowed: {result.get('send_allowed')}")
    print(f"  customer_delivery_enabled: {result.get('customer_delivery_enabled')}")
    print(f"  queue_item_count: {result.get('summary', {}).get('queue_item_count')}")
    for item in result.get("queue_items") or []:
        print(
            "    - "
            f"{item.get('invoice')}: {item.get('customer_name')} | "
            f"{item.get('recommended_cadence')} | {item.get('send_status')}"
        )
    failures = list(result.get("failures") or []) + contract_failures
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Customer Reminder Dry Run",
        "",
        f"- generated_at: {result.get('generated_at')}",
        f"- operating_mode: {result.get('operating_mode')}",
        f"- send_allowed: {result.get('send_allowed')}",
        f"- customer_delivery_enabled: {result.get('customer_delivery_enabled')}",
        f"- queue_item_count: {result.get('summary', {}).get('queue_item_count')}",
        "",
        "## Internal Review Queue",
        "",
    ]
    for item in result.get("queue_items") or []:
        lines.extend(
            [
                f"### {item.get('invoice')} - {item.get('customer_name')}",
                "",
                f"- cadence: {item.get('recommended_cadence')}",
                f"- delivery_mode: {item.get('delivery_mode')}",
                f"- send_status: {item.get('send_status')}",
                f"- blocked_customer_send_until: {', '.join(item.get('blocked_customer_send_until') or [])}",
                "",
            ]
        )
        for section in item.get("draft_sections") or []:
            lines.extend(
                [
                    f"#### {section.get('document_id')}",
                    "",
                    f"- subject: {section.get('subject')}",
                    f"- answer_first: {section.get('answer_first')}",
                    "",
                ]
            )
    if not result.get("queue_items"):
        lines.append("- None")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
