#!/usr/bin/env python3
"""Verify maintained Python verifier scripts expose safe, fast --help output.

This contract prevents the regression where a verifier treats ``--help`` as a
normal run and accidentally launches browser checks or backend probes.

Run:
  python scripts/verify/verifier_cli_contract.py
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFY_DIR = ROOT / "scripts" / "verify"
HELP_TIMEOUT_SECONDS = 5


def maintained_scripts() -> list[Path]:
    scripts = []
    proc = subprocess.run(
        ["git", "ls-files", "scripts/verify/*.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")

    for rel_path in sorted(line.strip() for line in proc.stdout.splitlines() if line.strip()):
        path = ROOT / rel_path
        if not path.exists():
            continue
        if path.name.startswith("_"):
            continue
        if path.name == Path(__file__).name:
            continue
        scripts.append(path)
    return scripts


def check_help(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    try:
        proc = subprocess.run(
            [sys.executable, str(path), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=HELP_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return [f"{rel} --help timed out after {HELP_TIMEOUT_SECONDS}s"]

    output = f"{proc.stdout}\n{proc.stderr}".lower()
    failures = []
    if proc.returncode != 0:
        failures.append(f"{rel} --help exited {proc.returncode}")
    if "usage:" not in output:
        failures.append(f"{rel} --help did not print usage text")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    failures = []
    for path in maintained_scripts():
        failures.extend(check_help(path))

    if failures:
        print("[VERIFIER CLI CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"[VERIFIER CLI CONTRACT] PASS ({len(maintained_scripts())} scripts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
