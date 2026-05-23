#!/usr/bin/env python3
"""Fail if release docs collapse provider success into owner-review readiness.

This is a small local docs gate. It scans the current release/failure handoff
surface for risky readiness phrases and requires nearby blocking/gate language.
It also requires the new executable lock/gate references to appear in the docs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DEFAULT_TARGETS = [
    "CODING-HANDOFF.md",
    "ECOMMERCE-SHOP-HANDOFF.md",
    "LT-LAUNCH-RUNBOOK.md",
    "locally-twisted-queue.md",
    "locally-twisted-decisions.md",
    "lessons-learned.md",
    "scripts/README.md",
    "workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md",
    "workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md",
    "workstreams/frappe-cloud-staging-owner-review-2026-05-22.md",
    "capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md",
    "capabilities/failures/release-controller-churn-after-stop.md",
]

RISKY_PHRASES = [
    "owner-review ready",
    "owner review ready",
    "staging ready",
    "live ready",
    "launch authority",
    "release authority",
]

SAFE_CONTEXT_TERMS = [
    "not ",
    "blocked",
    "gate",
    "must fail",
    "before",
    "unverified",
    "cannot",
    "must not",
    "do not",
    "frozen",
    "superseded",
]

REQUIRED_REFERENCES = [
    "release_locks/locally-twisted-staging-forensic-freeze.json",
    "scripts/release/frappe_cloud_release_controller.py",
    "scripts/verify/release_controller_contract.py",
    "scripts/verify/frappe_cloud_payload_contract.py",
    "scripts/verify/release_lock_contract.py",
    "scripts/verify/release_claim_language_contract.py",
    "npm run test:release-prevention",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", nargs="*", help="Optional repo-relative files to scan.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    targets = args.paths or DEFAULT_TARGETS
    failures = check_targets(targets)
    result = {"ok": not failures, "failures": failures, "targets": targets}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[RELEASE CLAIM LANGUAGE CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def check_targets(targets: list[str]) -> list[str]:
    failures: list[str] = []
    combined = []

    for rel_path in targets:
        path = ROOT.joinpath(*rel_path.replace("\\", "/").split("/"))
        if not path.exists():
            failures.append(f"scan target missing: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        combined.append(text.replace("\\", "/"))
        failures.extend(check_file_language(rel_path, text))

    combined_text = "\n".join(combined)
    for reference in REQUIRED_REFERENCES:
        if reference not in combined_text:
            failures.append(f"required release-prevention reference is missing from docs: {reference}")
    return failures


def check_file_language(rel_path: str, text: str) -> list[str]:
    failures: list[str] = []
    lines = text.splitlines()
    lowered_lines = [line.lower() for line in lines]
    for index, line in enumerate(lowered_lines):
        for phrase in RISKY_PHRASES:
            if phrase not in line:
                continue
            start = max(0, index - 2)
            end = min(len(lowered_lines), index + 3)
            context = "\n".join(lowered_lines[start:end])
            normalized_context = " ".join(context.replace("*", "").split())
            if not any(term in normalized_context for term in SAFE_CONTEXT_TERMS):
                failures.append(
                    f"{rel_path}:{index + 1} uses {phrase!r} without nearby blocking/gate language"
                )
    return failures


if __name__ == "__main__":
    sys.exit(main())
