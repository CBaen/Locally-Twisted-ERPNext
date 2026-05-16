#!/usr/bin/env python3
"""Seed or clean fake owner-action records for the local backend tour."""
from __future__ import annotations

import argparse
import subprocess
import sys


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.owner_demo_data.execute"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cleanup", action="store_true", help="Remove the owner demo records instead of seeding them")
    parser.add_argument("--marker", default="LT-DEMO-OWNER-ACTIONS", help="Synthetic record marker")
    args = parser.parse_args()

    proc = subprocess.run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            METHOD,
            "--kwargs",
            repr({"cleanup": args.cleanup, "marker": args.marker}),
        ],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        return proc.returncode
    if '"synthetic_only": true' not in proc.stdout.lower() and not args.cleanup:
        print("FATAL: owner demo seed did not report synthetic_only=true", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
