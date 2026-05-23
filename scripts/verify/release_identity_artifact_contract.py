#!/usr/bin/env python3
"""Offline contract for release identity proof artifacts."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "release" / "release_identity_artifact.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[RELEASE IDENTITY ARTIFACT CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        identity = tmp_path / "release-identity-proof.json"

        preview = run_helper("--json")
        if preview.returncode == 0:
            failures.append("preview identity proof unexpectedly passed")
        if "preview" not in preview.stdout.lower():
            failures.append("preview identity proof did not explain preview mode")

        write = run_helper(
            "--write",
            "--output",
            str(identity),
            "--codex-account-label",
            "Built by Cameron work Codex account",
            "--github-account",
            "CBaen",
            "--frappe-cloud-team",
            "5b8acl3gba",
            "--operator",
            "release-identity-contract",
            "--evidence",
            "contract fixture with no secrets",
            "--json",
        )
        if write.returncode != 0:
            failures.append("valid identity proof write did not pass")
        if not identity.exists():
            failures.append("valid identity proof write did not create output")

        validate = run_helper("--validate-only", str(identity), "--json")
        if validate.returncode != 0:
            failures.append("valid identity proof did not validate")

        preview_file = tmp_path / "preview.json"
        preview_data = json.loads(preview.stdout)["preview"]
        preview_file.write_text(json.dumps(preview_data), encoding="utf-8")
        preview_validate = run_helper("--validate-only", str(preview_file), "--json")
        if preview_validate.returncode == 0:
            failures.append("preview identity proof validated as mutation-capable")

        stale = tmp_path / "stale-identity.json"
        stale_data = json.loads(identity.read_text(encoding="utf-8"))
        stale_data["source_commit"] = "d" * 40
        stale.write_text(json.dumps(stale_data), encoding="utf-8")
        stale_validate = run_helper("--validate-only", str(stale), "--json")
        if stale_validate.returncode == 0:
            failures.append("stale source_commit identity proof validated")
        if "source_commit" not in stale_validate.stdout:
            failures.append("stale source_commit failure did not name source_commit")

        secret = tmp_path / "secret-identity.json"
        secret_data = json.loads(identity.read_text(encoding="utf-8"))
        secret_data["api_token"] = "ghp_this_should_not_be_here"
        secret.write_text(json.dumps(secret_data), encoding="utf-8")
        secret_validate = run_helper("--validate-only", str(secret), "--json")
        if secret_validate.returncode == 0:
            failures.append("secret-bearing identity proof validated")
        if "secret" not in secret_validate.stdout.lower() and "token" not in secret_validate.stdout.lower():
            failures.append("secret-bearing failure did not name secret/token risk")

        wrong_site = tmp_path / "wrong-site-identity.json"
        wrong_site_data = json.loads(identity.read_text(encoding="utf-8"))
        for row in wrong_site_data["account_checks"]:
            if row["surface"] == "frappe_cloud_site":
                row["actual"] = "wrong-site.frappe.cloud"
        wrong_site.write_text(json.dumps(wrong_site_data), encoding="utf-8")
        wrong_site_validate = run_helper("--validate-only", str(wrong_site), "--json")
        if wrong_site_validate.returncode == 0:
            failures.append("wrong Frappe Cloud site identity proof validated")
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
