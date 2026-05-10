#!/usr/bin/env python3
"""Render a read-only internal paperwork review digest.

Run:
  python scripts/verify/paperwork_review_digest.py
  python scripts/verify/paperwork_review_digest.py --json
  python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json
  python scripts/verify/paperwork_review_digest.py --markdown output/paperwork-review-digest.md
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
METHOD = "locally_twisted.paperwork.paperwork_review_digest.run"
ROOT = Path(__file__).resolve().parents[2]


class PaperworkReviewDigestFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise PaperworkReviewDigestFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise PaperworkReviewDigestFail("paperwork review digest returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PaperworkReviewDigestFail(f"paperwork review digest returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise PaperworkReviewDigestFail(
            f"paperwork review digest returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    parser.add_argument("--markdown", help="Write human-readable markdown digest")
    args = parser.parse_args()

    try:
        result = bench_execute()
        failures = _contract_failures(result)
    except PaperworkReviewDigestFail as exc:
        print(f"[PAPERWORK REVIEW DIGEST] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[PAPERWORK REVIEW DIGEST] wrote {report_path.relative_to(ROOT)}")

    if args.markdown:
        markdown_path = _rooted(args.markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(_markdown(result), encoding="utf-8")
        print(f"[PAPERWORK REVIEW DIGEST] wrote {markdown_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result, failures)

    return 0 if result.get("ok") and not failures else 1


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result.get("read_only") is not True:
        failures.append("digest is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("digest allows customer sending")
    if result.get("mutation_allowed") is not False:
        failures.append("digest allows accounting mutations")
    if result.get("digest_type") != "paperwork_review_digest":
        failures.append("digest_type is not paperwork_review_digest")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("mutation guard changed while rendering digest")

    expected_sources = {
        "paperwork_status",
        "business_automation_index",
        "unpaid_invoice_review",
        "unpaid_invoice_draft_packet",
    }
    missing_sources = sorted(expected_sources - set(result.get("source_surfaces") or []))
    if missing_sources:
        failures.append("missing source surfaces: " + ", ".join(missing_sources))
    automation_summary = (result.get("source_summaries") or {}).get("business_automation_index") or {}
    if automation_summary.get("runtime_contracts_executed") is not False:
        failures.append("paperwork digest must not execute fake-data runtime contracts through the automation index")

    sections = result.get("sections")
    if not isinstance(sections, dict):
        failures.append("sections is not an object")
        return failures
    for key in (
        "unpaid_invoice_packets",
        "cutover_deferred_not_blocking",
        "setup_gaps",
        "partial_connections",
        "operations_readiness",
        "next_safe_actions",
    ):
        if key not in sections:
            failures.append(f"sections missing {key}")
    if "live_payment_blockers" in sections:
        failures.append("live payment readiness is still labeled as a current blocker")

    for packet in sections.get("unpaid_invoice_packets", {}).get("items", []):
        if packet.get("send_status") != "draft_only_not_sent":
            failures.append(f"{packet.get('invoice')} packet is not draft-only")
        if packet.get("human_approval_required") is not True:
            failures.append(f"{packet.get('invoice')} packet does not require human approval")

    operations_items = sections.get("operations_readiness", {}).get("items") or []
    operations_ids = {item.get("id") for item in operations_items if isinstance(item, dict)}
    for required_id in ("company_operations", "vendor_contractor", "accountant_finance", "customer_user"):
        if required_id not in operations_ids:
            failures.append(f"operations_readiness missing {required_id}")
    for item in operations_items:
        if not isinstance(item, dict):
            failures.append("operations_readiness item is not an object")
            continue
        if not item.get("audience"):
            failures.append(f"{item.get('id')} missing audience")
        if not item.get("next_safe_action"):
            failures.append(f"{item.get('id')} missing next_safe_action")
        if item.get("customer_delivery_enabled") is not False:
            failures.append(f"{item.get('id')} does not block customer delivery")
        if item.get("accounting_mutation_enabled") is not False:
            failures.append(f"{item.get('id')} does not block accounting mutation")
    return failures


def _print_summary(result: dict[str, Any], contract_failures: list[str]) -> None:
    print("[PAPERWORK REVIEW DIGEST] " + ("PASS" if result.get("ok") and not contract_failures else "FAIL"))
    print(f"  generated_at: {result.get('generated_at')}")
    print(f"  read_only: {result.get('read_only')}")
    print(f"  send_allowed: {result.get('send_allowed')}")
    print(f"  mutation_allowed: {result.get('mutation_allowed')}")
    sections = result.get("sections") or {}
    for key in (
        "unpaid_invoice_packets",
        "cutover_deferred_not_blocking",
        "setup_gaps",
        "partial_connections",
        "operations_readiness",
    ):
        section = sections.get(key) or {}
        print(f"  {key}: {section.get('count')}")
    failures = list(result.get("failures") or []) + contract_failures
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _markdown(result: dict[str, Any]) -> str:
    sections = result.get("sections") or {}
    lines = [
        "# Paperwork Review Digest",
        "",
        f"- generated_at: {result.get('generated_at')}",
        f"- read_only: {result.get('read_only')}",
        f"- send_allowed: {result.get('send_allowed')}",
        f"- mutation_allowed: {result.get('mutation_allowed')}",
        "",
    ]
    for key, title in (
        ("unpaid_invoice_packets", "Unpaid Invoice Packets"),
        ("cutover_deferred_not_blocking", "Cutover Deferred, Not Blocking"),
        ("setup_gaps", "Setup Gaps"),
        ("partial_connections", "Partial Connections"),
        ("operations_readiness", "Operations Readiness"),
        ("next_safe_actions", "Next Safe Actions"),
    ):
        section = sections.get(key) or {}
        lines.extend([f"## {title}", "", f"Count: {section.get('count')}", ""])
        for item in section.get("items") or []:
            lines.append(f"- {_item_label(item)}")
        if not section.get("items"):
            lines.append("- None")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _item_label(item: Any) -> str:
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return str(item)
    return (
        item.get("label")
        or item.get("summary")
        or item.get("invoice")
        or item.get("id")
        or json.dumps(item, default=str)
    )


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
