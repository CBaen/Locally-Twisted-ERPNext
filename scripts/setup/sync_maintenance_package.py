#!/usr/bin/env python3
"""Sync LT sanitized Maintenance Admin role, report, and workspace."""
from __future__ import annotations

import argparse
import subprocess
import sys


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.sync_maintenance_package.execute"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        return proc.returncode
    if "boundary_ok" not in proc.stdout:
        print("FATAL: maintenance package sync summary missing from output", file=sys.stderr)
        return 1
    if '"boundary_ok": false' in proc.stdout.lower():
        print("FATAL: maintenance package boundary did not pass", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
