#!/usr/bin/env python3
"""Verify customer forms/contact points, CRM targets, fail-loud UX, and business-copy routing."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.customer_contact_points_contract.run"


class CustomerContactPointsContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise CustomerContactPointsContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise CustomerContactPointsContractFail("customer contact-points contract returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CustomerContactPointsContractFail(
            f"customer contact-points contract returned non-JSON output: {text[:1000]}"
        ) from exc
    if not isinstance(parsed, dict):
        raise CustomerContactPointsContractFail(
            f"customer contact-points contract returned {type(parsed).__name__}, expected object"
        )
    return parsed


def write_markdown(result: dict[str, Any], path: Path) -> None:
    lines = [
        "# Customer Contact Points Contract",
        "",
        f"- Generated at: {result.get('generated_at')}",
        f"- Result: {'PASS' if result.get('ok') else 'FAIL'}",
        f"- Surfaces: {result.get('surface_count')}",
        "",
        "| Surface | Record Target | Customer Failure Visible | Business Copy Required | Status |",
        "|---|---|---:|---:|---|",
    ]
    for surface in result.get("surfaces") or []:
        lines.append(
            "| {id} | {target} | {visible} | {copy} | {status} |".format(
                id=surface.get("id"),
                target=surface.get("record_target"),
                visible="yes" if surface.get("customer_visible_failure") else "no",
                copy="yes" if surface.get("business_copy_required") else "no",
                status="PASS" if surface.get("passed") else "FAIL",
            )
        )

    lines.extend(["", "## Failures", ""])
    failures = result.get("failures") or []
    lines.extend(f"- {failure}" for failure in failures) if failures else lines.append("- None")

    lines.extend(["", "## Notes", ""])
    for surface in result.get("surfaces") or []:
        points = ", ".join(surface.get("contact_points") or [])
        lines.append(f"- `{surface.get('id')}`: {surface.get('notes')} Contact points: {points}.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        default="output/customer-contact-points-contract-20260510.json",
        help="JSON report output path.",
    )
    parser.add_argument(
        "--markdown",
        default="output/customer-contact-points-contract-20260510.md",
        help="Markdown report output path.",
    )
    args = parser.parse_args()

    try:
        result = bench_execute()
    except CustomerContactPointsContractFail as exc:
        print(f"[CUSTOMER CONTACT POINTS CONTRACT] FAIL\n  - {exc}")
        return 1

    report_path = ROOT / args.report
    markdown_path = ROOT / args.markdown
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    write_markdown(result, markdown_path)

    print("[CUSTOMER CONTACT POINTS CONTRACT] " + ("PASS" if result.get("ok") else "FAIL"))
    print(f"  surfaces: {result.get('surface_count')}")
    print(f"  report: {report_path}")
    print(f"  markdown: {markdown_path}")
    for surface in result.get("surfaces") or []:
        print(f"    - {surface.get('id')}: {'PASS' if surface.get('passed') else 'FAIL'}")
    if result.get("failures"):
        print("  failures:")
        for failure in result.get("failures") or []:
            print(f"    - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
