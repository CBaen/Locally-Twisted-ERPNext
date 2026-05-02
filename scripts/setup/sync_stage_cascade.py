#!/usr/bin/env python3
"""Sync Task fields required by LT CRM stage cascades."""
from __future__ import annotations

import subprocess
import sys


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.sync_stage_cascade.execute"


def main() -> int:
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
    if "ensured_custom_fields" not in proc.stdout:
        print("FATAL: stage cascade sync summary missing from output", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
