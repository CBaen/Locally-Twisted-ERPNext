#!/usr/bin/env python3
"""Offline CLI contract for the LT Frappe Cloud release controller.

This proves the controller itself, not only helper functions:

- active forensic-freeze lock blocks mutation actions;
- missing read receipt blocks read-only release forensics;
- a valid read receipt allows a read-only forensic action without provider
  mutation.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "release"))

from release_guard_common import REQUIRED_READ_DOCS  # noqa: E402


CONTROLLER = ROOT / "scripts" / "release" / "frappe_cloud_release_controller.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[RELEASE CONTROLLER CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        emergency_dir = tmp_path / "emergency"

        missing_payload = run_controller("--action", "frappe_cloud_deploy", "--json")
        if missing_payload.returncode == 0:
            failures.append("frappe_cloud_deploy passed without a sanitized payload artifact")
        if "payload" not in f"{missing_payload.stdout}\n{missing_payload.stderr}".lower():
            failures.append("missing deploy payload output did not mention payload")

        payload = tmp_path / "sanitized-payload.json"
        payload.write_text(
            json.dumps(
                {
                    "content_type": "application/json",
                    "body": {
                        "apps": [
                            {
                                "app": "locally_twisted",
                                "repository": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
                                "hash": "a" * 40,
                            }
                        ],
                        "sites": [{"name": "locallytwisted-staging.frappe.cloud"}],
                    },
                }
            ),
            encoding="utf-8",
        )

        blocked = run_controller(
            "--action",
            "frappe_cloud_deploy",
            "--payload-file",
            str(payload),
            "--emergency-handoff-dir",
            str(emergency_dir),
            "--json",
        )
        if blocked.returncode == 0:
            failures.append("frappe_cloud_deploy was not blocked by the active forensic-freeze lock")
        if "forensic-freeze" not in f"{blocked.stdout}\n{blocked.stderr}":
            failures.append("blocked deploy output did not mention forensic-freeze")
        handoffs = list(emergency_dir.glob("emergency-handoff-*.md"))
        if not handoffs:
            failures.append("blocked deploy did not write an emergency handoff artifact")
        elif "What Not To Touch" not in handoffs[0].read_text(encoding="utf-8"):
            failures.append("emergency handoff is missing What Not To Touch section")

        missing_receipt = run_controller("--action", "read_only_forensics", "--json")
        if missing_receipt.returncode == 0:
            failures.append("read_only_forensics passed without a required-doc read receipt")
        if "read receipt" not in f"{missing_receipt.stdout}\n{missing_receipt.stderr}".lower():
            failures.append("missing receipt output did not mention read receipt")

        receipt = tmp_path / "read-receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "agent": "release-controller-contract",
                    "created_at": "2026-05-23T00:00:00-06:00",
                    "read_documents": REQUIRED_READ_DOCS,
                }
            ),
            encoding="utf-8",
        )
        allowed = run_controller("--action", "read_only_forensics", "--read-receipt", str(receipt), "--json")
        if allowed.returncode != 0:
            failures.append("read_only_forensics with valid read receipt did not pass")
        if "provider_mutation_executed" not in allowed.stdout:
            failures.append("allowed read-only output did not report provider_mutation_executed=false")

    return failures


def run_controller(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CONTROLLER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
    )


if __name__ == "__main__":
    sys.exit(main())
