#!/usr/bin/env python3
"""Sync LT public/client-visible white-label site branding."""
from __future__ import annotations

import subprocess
import sys


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.sync_site_branding.execute"


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
    if "website_settings" not in proc.stdout or "system_settings" not in proc.stdout:
        print("FATAL: site branding sync summary missing from output", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
