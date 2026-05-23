#!/usr/bin/env python3
"""Offline contract for the local LT release status report command."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "scripts" / "release" / "release_status_report.py"
IDENTITY = ROOT / "scripts" / "release" / "release_identity_artifact.py"
APPROVAL = ROOT / "scripts" / "release" / "freeze_reopen_approval_artifact.py"

sys.path.insert(0, str(ROOT / "scripts" / "release"))
from release_guard_common import REQUIRED_READ_DOCS  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[RELEASE STATUS REPORT CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []

    no_args = run_status("--json")
    if no_args.returncode == 0:
        failures.append("release status unexpectedly passed without required artifacts")
    no_args_data = json.loads(no_args.stdout)
    if no_args_data.get("status") != "NO-GO":
        failures.append("release status without artifacts did not return NO-GO")
    if not any("identity proof" in blocker for blocker in no_args_data.get("blockers", [])):
        failures.append("release status without artifacts did not require identity proof")
    if no_args_data.get("provider_mutation_executed") is not False:
        failures.append("release status did not prove provider_mutation_executed=false")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        identity = tmp_path / "release-identity-proof.json"
        approval = tmp_path / "freeze-reopen-approval.json"
        receipt = tmp_path / "read-receipt.json"
        packet = tmp_path / "packet"

        write_identity(identity)
        write_approval(approval)
        receipt.write_text(
            json.dumps(
                {
                    "agent": "release-status-contract",
                    "created_at": "2026-05-23T00:00:00-06:00",
                    "read_documents": REQUIRED_READ_DOCS,
                }
            ),
            encoding="utf-8",
        )
        packet.mkdir()
        for name in ("controller.md", "provider-witness.md", "gate-fixer.md", "recorder.md"):
            (packet / name).write_text("Target: staging\nEvidence: contract fixture\nState: pass\n", encoding="utf-8")
        (packet / "failure-ledger.json").write_text("{}", encoding="utf-8")
        (packet / "read-receipt.json").write_text("{}", encoding="utf-8")
        (packet / "README.md").write_text("# Fresh Packet\n\nStatus: mutation-capable draft after approval.\n", encoding="utf-8")

        ready = run_status(
            "--identity-proof",
            str(identity),
            "--reopen-approval",
            str(approval),
            "--read-receipt",
            str(receipt),
            "--packet-dir",
            str(packet),
            "--json",
        )
        if ready.returncode != 0:
            failures.append("release status did not pass with fresh required artifacts")
        ready_data = json.loads(ready.stdout)
        if ready_data.get("status") != "READY_FOR_CONTROLLER":
            failures.append("release status with fresh artifacts did not return READY_FOR_CONTROLLER")

        (packet / "README.md").write_text("# Archived Packet\n\nStatus: NO-GO, read-only evidence only.\n", encoding="utf-8")
        no_go_packet = run_status(
            "--identity-proof",
            str(identity),
            "--reopen-approval",
            str(approval),
            "--read-receipt",
            str(receipt),
            "--packet-dir",
            str(packet),
            "--json",
        )
        if no_go_packet.returncode == 0:
            failures.append("release status passed with an explicitly no-go/read-only packet")
        if "no-go" not in no_go_packet.stdout.lower() and "read-only" not in no_go_packet.stdout.lower():
            failures.append("no-go packet status did not name no-go/read-only blocker")
    return failures


def write_identity(path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(IDENTITY),
            "--write",
            "--output",
            str(path),
            "--codex-account-label",
            "Built by Cameron work Codex account",
            "--github-account",
            "CBaen",
            "--frappe-cloud-team",
            "5b8acl3gba",
            "--operator",
            "release-status-contract",
            "--evidence",
            "contract fixture with no secrets",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)


def write_approval(path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(APPROVAL),
            "--write",
            "--output",
            str(path),
            "--approved-by",
            "release-status-contract",
            "--approval-evidence",
            "contract fixture only",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)


def run_status(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(STATUS), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )


if __name__ == "__main__":
    sys.exit(main())
