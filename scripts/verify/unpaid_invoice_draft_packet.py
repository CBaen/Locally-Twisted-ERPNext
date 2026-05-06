#!/usr/bin/env python3
"""Render draft-only unpaid invoice packets without sending or mutating records.

Run:
  python scripts/verify/unpaid_invoice_draft_packet.py
  python scripts/verify/unpaid_invoice_draft_packet.py --json
  python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json
  python scripts/verify/unpaid_invoice_draft_packet.py --markdown output/unpaid-invoice-draft-packet.md
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
METHOD = "locally_twisted.paperwork.unpaid_invoice_draft_packet.run"
ROOT = Path(__file__).resolve().parents[2]


class UnpaidInvoiceDraftPacketFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise UnpaidInvoiceDraftPacketFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise UnpaidInvoiceDraftPacketFail("unpaid invoice draft packet returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UnpaidInvoiceDraftPacketFail(f"unpaid invoice draft packet returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise UnpaidInvoiceDraftPacketFail(
            f"unpaid invoice draft packet returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    parser.add_argument("--markdown", help="Write human-review markdown packet preview")
    args = parser.parse_args()

    try:
        result = bench_execute()
        failures = _contract_failures(result)
    except UnpaidInvoiceDraftPacketFail as exc:
        print(f"[UNPAID INVOICE DRAFT PACKET] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[UNPAID INVOICE DRAFT PACKET] wrote {report_path.relative_to(ROOT)}")

    if args.markdown:
        markdown_path = _rooted(args.markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(_markdown(result), encoding="utf-8")
        print(f"[UNPAID INVOICE DRAFT PACKET] wrote {markdown_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result, failures)

    return 0 if result.get("ok") and not failures else 1


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result.get("read_only") is not True:
        failures.append("result is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("result allows sending")
    if result.get("mutation_allowed") is not False:
        failures.append("result allows accounting mutations")
    if result.get("packet_type") != "unpaid_invoice_draft_packet":
        failures.append("packet_type is not unpaid_invoice_draft_packet")
    if result.get("source_review_surface") != "unpaid_invoice_review":
        failures.append("source_review_surface is not unpaid_invoice_review")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("mutation guard changed while rendering packets")

    packets = result.get("packets")
    if not isinstance(packets, list):
        failures.append("packets is not a list")
        return failures
    if result.get("packet_count") != len(packets):
        failures.append("packet_count does not match packets length")

    for packet in packets:
        invoice = packet.get("invoice") or "<missing invoice>"
        if packet.get("send_status") != "draft_only_not_sent":
            failures.append(f"{invoice} packet send_status is not draft_only_not_sent")
        if packet.get("human_approval_required") is not True:
            failures.append(f"{invoice} does not require human approval")
        sections = packet.get("sections")
        if not isinstance(sections, list) or len(sections) != 2:
            failures.append(f"{invoice} does not have exactly two draft sections")
            continue
        section_ids = {section.get("document_id") for section in sections}
        if section_ids != {"payment_reminder_draft", "statement_of_account"}:
            failures.append(f"{invoice} draft sections are wrong: {sorted(section_ids)}")
        for section in sections:
            section_id = section.get("document_id") or "<missing section>"
            if section.get("send_status") != "draft_only_not_sent":
                failures.append(f"{invoice} {section_id} is not draft-only")
            if "human_approval" not in str(section.get("do_not_send_without") or ""):
                failures.append(f"{invoice} {section_id} lacks human_approval gate")
            for key in ("subject", "answer_first", "body_preview", "key_fields_to_review"):
                if not section.get(key):
                    failures.append(f"{invoice} {section_id} missing {key}")
    return failures


def _print_summary(result: dict[str, Any], contract_failures: list[str]) -> None:
    print("[UNPAID INVOICE DRAFT PACKET] " + ("PASS" if result.get("ok") and not contract_failures else "FAIL"))
    print(f"  generated_at: {result.get('generated_at')}")
    print(f"  read_only: {result.get('read_only')}")
    print(f"  send_allowed: {result.get('send_allowed')}")
    print(f"  mutation_allowed: {result.get('mutation_allowed')}")
    print(f"  packet_count: {result.get('packet_count')}")
    print(f"  source_review_surface: {result.get('source_review_surface')}")
    for packet in (result.get("packets") or [])[:8]:
        print(
            "    - {invoice}: {customer} | sections {sections} | status {status}".format(
                invoice=packet.get("invoice"),
                customer=packet.get("customer_name") or packet.get("customer"),
                sections=", ".join(section.get("document_id", "") for section in packet.get("sections") or []),
                status=packet.get("send_status"),
            )
        )

    failures = list(result.get("failures") or []) + contract_failures
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Unpaid Invoice Draft Packet Preview",
        "",
        f"- generated_at: {result.get('generated_at')}",
        f"- read_only: {result.get('read_only')}",
        f"- send_allowed: {result.get('send_allowed')}",
        f"- mutation_allowed: {result.get('mutation_allowed')}",
        "",
    ]
    for packet in result.get("packets") or []:
        lines.extend(
            [
                f"## {packet.get('invoice')} - {packet.get('customer_name') or packet.get('customer')}",
                "",
                f"- send_status: {packet.get('send_status')}",
                f"- human_approval_required: {packet.get('human_approval_required')}",
                "",
            ]
        )
        for section in packet.get("sections") or []:
            lines.extend(
                [
                    f"### {section.get('title')}",
                    "",
                    f"Subject: {section.get('subject')}",
                    "",
                    str(section.get("answer_first") or ""),
                    "",
                    str(section.get("body_preview") or ""),
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
