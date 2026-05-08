#!/usr/bin/env python3
"""Verify synthetic backend pipelines without live credentials or real customer data.

Run:
  python scripts/verify/synthetic_business_pipeline.py
  python scripts/verify/synthetic_business_pipeline.py --json
  python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
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
METHOD = "locally_twisted.verify.synthetic_business_pipeline.run"
ROOT = Path(__file__).resolve().parents[2]


class SyntheticPipelineFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise SyntheticPipelineFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise SyntheticPipelineFail("synthetic business pipeline returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SyntheticPipelineFail(f"synthetic business pipeline returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise SyntheticPipelineFail(
            f"synthetic business pipeline returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
        failures = _contract_failures(result)
    except SyntheticPipelineFail as exc:
        print(f"[SYNTHETIC BUSINESS PIPELINE] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[SYNTHETIC BUSINESS PIPELINE] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result, failures)

    return 0 if result.get("ok") and not failures else 1


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result.get("synthetic_only") is not True:
        failures.append("result is not marked synthetic_only")
    if result.get("live_inputs_required") is not False:
        failures.append("result requires live inputs")
    if result.get("uses_real_customer_data") is not False:
        failures.append("result uses real customer data")
    if result.get("read_only") is not True:
        failures.append("result is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("result allows sending")
    if result.get("mutation_allowed") is not False:
        failures.append("result allows accounting mutations")
    sections = result.get("sections")
    if not isinstance(sections, dict):
        failures.append("sections is not an object")
        return failures
    for key in (
        "synthetic_operating_readiness",
        "broken_piping",
        "inefficiencies",
        "cutover_deferred_not_blocking",
    ):
        if key not in sections:
            failures.append(f"sections missing {key}")
    if sections.get("broken_piping", {}).get("count"):
        failures.append("broken_piping section is not empty")
    if "live_payment_blockers" in sections:
        failures.append("live payment readiness is still labeled as a current blocker")
    required_contract_ids = {
        "stripe_amount_parity",
        "checkout_lead_conversion",
        "checkout_fulfillment",
        "payment_success_paid_order_cascade",
        "stripe_webhook_reconciliation",
        "customer_document_policy",
        "outbound_document_templates",
        "outbound_document_send_readiness",
        "quote_proposal_draft_packets",
        "unpaid_invoice_draft_packet_outliers",
        "customer_reminder_dry_run_outliers",
        "customer_reminder_review_report_outliers",
    }
    contract_ids = {
        item.get("id")
        for item in sections.get("synthetic_operating_readiness", {}).get("items", [])
        if isinstance(item, dict)
    }
    missing_contract_ids = sorted(required_contract_ids - contract_ids)
    if missing_contract_ids:
        failures.append("synthetic pipeline missing contracts: " + ", ".join(missing_contract_ids))
    return failures


def _print_summary(result: dict[str, Any], contract_failures: list[str]) -> None:
    print("[SYNTHETIC BUSINESS PIPELINE] " + ("PASS" if result.get("ok") and not contract_failures else "FAIL"))
    print(f"  generated_at: {result.get('generated_at')}")
    print(f"  synthetic_only: {result.get('synthetic_only')}")
    print(f"  live_inputs_required: {result.get('live_inputs_required')}")
    print(f"  uses_real_customer_data: {result.get('uses_real_customer_data')}")
    sections = result.get("sections") or {}
    for key in (
        "synthetic_operating_readiness",
        "broken_piping",
        "inefficiencies",
        "cutover_deferred_not_blocking",
    ):
        section = sections.get(key) or {}
        print(f"  {key}: {section.get('count')}")
    failures = list(result.get("failures") or []) + contract_failures
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
