#!/usr/bin/env python3
"""Render draft-only quote/proposal packets without sending or mutating records.

Run:
  python scripts/verify/quote_proposal_draft_packet.py
  python scripts/verify/quote_proposal_draft_packet.py --json
  python scripts/verify/quote_proposal_draft_packet.py --report output/quote-proposal-draft-packet.json
  python scripts/verify/quote_proposal_draft_packet.py --markdown output/quote-proposal-draft-packet.md
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
METHOD = "locally_twisted.paperwork.quote_proposal_draft_packet.run"
ROOT = Path(__file__).resolve().parents[2]


class QuoteProposalDraftPacketFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise QuoteProposalDraftPacketFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise QuoteProposalDraftPacketFail("quote/proposal draft packet returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise QuoteProposalDraftPacketFail(f"quote/proposal draft packet returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise QuoteProposalDraftPacketFail(
            f"quote/proposal draft packet returned {type(parsed).__name__}, expected object"
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
    except QuoteProposalDraftPacketFail as exc:
        print(f"[QUOTE PROPOSAL DRAFT PACKET] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[QUOTE PROPOSAL DRAFT PACKET] wrote {report_path.relative_to(ROOT)}")

    if args.markdown:
        markdown_path = _rooted(args.markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(_markdown(result), encoding="utf-8")
        print(f"[QUOTE PROPOSAL DRAFT PACKET] wrote {markdown_path.relative_to(ROOT)}")

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
        failures.append("result allows mutations")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("result enables customer delivery")
    if result.get("packet_type") != "quote_proposal_draft_packet":
        failures.append("packet_type is not quote_proposal_draft_packet")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("mutation guard changed while rendering packets")

    packets = result.get("packets")
    if not isinstance(packets, list):
        failures.append("packets is not a list")
        return failures
    if result.get("packet_count") != len(packets):
        failures.append("packet_count does not match packets length")

    for packet in packets:
        label = packet.get("source_name") or "<missing source>"
        if packet.get("send_status") != "draft_only_not_sent":
            failures.append(f"{label} packet send_status is not draft_only_not_sent")
        if packet.get("human_approval_required") is not True:
            failures.append(f"{label} does not require human approval")
        section_ids = {section.get("document_id") for section in packet.get("sections") or []}
        if section_ids != {"quote_estimate", "event_proposal_packet"}:
            failures.append(f"{label} draft sections are wrong: {sorted(section_ids)}")
        for section in packet.get("sections") or []:
            if section.get("send_status") != "draft_only_not_sent":
                failures.append(f"{label} {section.get('document_id')} is not draft-only")
            readiness = section.get("send_readiness") or {}
            if readiness.get("send_ready") is True:
                failures.append(f"{label} {section.get('document_id')} is send-ready before human approval")
    return failures


def _print_summary(result: dict[str, Any], contract_failures: list[str]) -> None:
    print("[QUOTE PROPOSAL DRAFT PACKET] " + ("PASS" if result.get("ok") and not contract_failures else "FAIL"))
    print(f"  generated_at: {result.get('generated_at')}")
    print(f"  read_only: {result.get('read_only')}")
    print(f"  send_allowed: {result.get('send_allowed')}")
    print(f"  mutation_allowed: {result.get('mutation_allowed')}")
    print(f"  packet_count: {result.get('packet_count')}")
    for packet in (result.get("packets") or [])[:8]:
        print(
            "    - {source}: {customer} | sections {sections} | status {status}".format(
                source=packet.get("source_name"),
                customer=packet.get("customer_name"),
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
        "# Quote Proposal Draft Packet Preview",
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
                f"## {packet.get('source_name')} - {packet.get('customer_name')}",
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
