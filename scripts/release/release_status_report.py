#!/usr/bin/env python3
"""Report whether the LT staging release candidate may proceed to provider work.

This is a release-prevention gate. It is expected to block until Guiding Light's
deployment approval is recorded as a repo artifact.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


EXPECTED_BRANCH = "codex/lt-staging-release-candidate-freeze"
REQUIRED_FILES = [
    "workstreams/ecommerce-audit/staging-release-controller-packet-2026-05-29.md",
    "workstreams/ecommerce-audit/staging-release-candidate-freeze-2026-05-29.md",
    "workstreams/ecommerce-audit/staging-shop-audit-item-5-release-no-go-packet-2026-05-29.md",
    "workstreams/capability-graduation-support-packet-2026-05-29.md",
]
APPROVAL_FILE = "workstreams/ecommerce-audit/staging-deployment-approval-2026-05-29.md"


def git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], text=True, capture_output=True, check=False)


def value(args: list[str]) -> str:
    proc = git(args)
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def short_head(commit: str) -> str:
    return commit[:7] if commit else ""


def build_report(root: Path) -> dict[str, object]:
    blockers: list[str] = []
    warnings: list[str] = []

    branch = value(["rev-parse", "--abbrev-ref", "HEAD"])
    head = value(["rev-parse", "HEAD"])
    short = short_head(head)
    upstream = value(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    status_lines = [line for line in value(["status", "--porcelain"]).splitlines() if line.strip()]

    if branch != EXPECTED_BRANCH:
        blockers.append(f"expected branch {EXPECTED_BRANCH}, found {branch or 'unknown'}")

    if status_lines:
        blockers.append("working tree is not clean")

    if not upstream:
        blockers.append("source-freeze branch has no upstream remote")

    missing_files = [path for path in REQUIRED_FILES if not (root / path).is_file()]
    for path in missing_files:
        blockers.append(f"required release artifact missing: {path}")

    approval_path = root / APPROVAL_FILE
    approval_recorded = approval_path.is_file()
    if not approval_recorded:
        blockers.append(f"deployment approval artifact missing: {APPROVAL_FILE}")

    if status_lines:
        warnings.extend(status_lines)

    status = "READY" if not blockers else "BLOCKED"
    return {
        "ok": status == "READY",
        "status": status,
        "branch": branch,
        "head": short,
        "upstream": upstream,
        "approval_recorded": approval_recorded,
        "approval_file": APPROVAL_FILE,
        "required_files": REQUIRED_FILES,
        "blockers": blockers,
        "warnings": warnings,
        "non_approvals": [
            "staging deployment",
            "Frappe Cloud provider mutation",
            "app mirror update",
            "migrate/cache clear",
            "live checkout",
            "live Stripe",
            "DNS",
            "Search Console",
            "product data mutation",
            "ERPNext record mutation",
            "email sending",
        ],
    }


def print_plain(report: dict[str, object]) -> None:
    print(f"[LT RELEASE STATUS] {report['status']}")
    print(f"  branch: {report.get('branch')}")
    print(f"  head: {report.get('head')}")
    print(f"  upstream: {report.get('upstream') or 'missing'}")
    print(f"  deployment approval recorded: {report.get('approval_recorded')}")

    blockers = report.get("blockers") or []
    if blockers:
        print("  blockers:")
        for blocker in blockers:
            print(f"    - {blocker}")

    warnings = report.get("warnings") or []
    if warnings:
        print("  working tree notes:")
        for warning in warnings:
            print(f"    - {warning}")

    if report["status"] != "READY":
        print("  next safe step: record explicit staging deployment approval before provider work")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="return nonzero unless the release status is READY",
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[2]
    report = build_report(root)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_plain(report)

    if args.fail_on_blocked and report["status"] != "READY":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
