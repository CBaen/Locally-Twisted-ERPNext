#!/usr/bin/env python3
"""Offline contract for release read receipt artifacts."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "release" / "read_receipt_artifact.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[RELEASE READ RECEIPT ARTIFACT CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        receipt = tmp_path / "read-receipt.json"

        preview = run_helper("--json")
        if preview.returncode == 0:
            failures.append("preview read receipt unexpectedly passed")
        if "preview" not in preview.stdout.lower():
            failures.append("preview read receipt did not explain preview mode")

        missing_agent = run_helper("--write", "--output", str(receipt), "--json")
        if missing_agent.returncode == 0:
            failures.append("read receipt write passed without --agent")

        write = run_helper(
            "--write",
            "--output",
            str(receipt),
            "--agent",
            "read-receipt-contract",
            "--evidence",
            "contract fixture with required docs",
            "--json",
        )
        if write.returncode != 0:
            failures.append("valid read receipt write did not pass")
        if not receipt.exists():
            failures.append("valid read receipt write did not create output")

        validate = run_helper("--validate-only", str(receipt), "--json")
        if validate.returncode != 0:
            failures.append("valid read receipt did not validate")

        missing_doc = tmp_path / "missing-doc-read-receipt.json"
        missing_data = json.loads(receipt.read_text(encoding="utf-8"))
        missing_data["read_documents"] = missing_data["read_documents"][:-1]
        missing_doc.write_text(json.dumps(missing_data), encoding="utf-8")
        missing_validate = run_helper("--validate-only", str(missing_doc), "--json")
        if missing_validate.returncode == 0:
            failures.append("read receipt with missing required doc validated")
        if "missing required docs" not in missing_validate.stdout:
            failures.append("missing-doc failure did not name required docs")

        empty = tmp_path / "empty-read-receipt.json"
        empty.write_text("{}", encoding="utf-8")
        empty_validate = run_helper("--validate-only", str(empty), "--json")
        if empty_validate.returncode == 0:
            failures.append("empty read receipt validated")
    return failures


def run_helper(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HELPER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )


if __name__ == "__main__":
    sys.exit(main())
