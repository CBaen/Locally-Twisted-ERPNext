"""
clear_website_cache.py — Clear Frappe's website + asset caches on the LT site.

Run after editing any of:
  - Jinja templates in apps/locally_twisted/locally_twisted/templates/
  - SCSS or CSS in apps/locally_twisted/locally_twisted/public/
  - Web Page records via the API
  - hooks.py (also requires service restart — see install_webshop.py)

Why this script exists:
  Frappe caches rendered Web Pages, asset bundle paths, and template lookups
  aggressively. Editing a Jinja partial on host disk will not affect the
  served page until the cache is cleared. The cache is a per-site Redis-backed
  cache; clearing it forces Frappe to re-resolve templates and re-render pages
  on the next request.

What this script does:
  1. bench --site frontend clear-cache       (clears site cache)
  2. bench --site frontend clear-website-cache  (clears Web Page + Web Form cache)
  3. Optional: --restart  also restart backend so any hooks.py change is picked up

Idempotent: safe to re-run.

Usage:
  python scripts/dev/clear_website_cache.py
  python scripts/dev/clear_website_cache.py --restart
"""

from __future__ import annotations

import argparse
import subprocess
import sys

CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, text=True, check=check)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--restart", action="store_true",
                        help="Also restart backend (needed after hooks.py changes).")
    args = parser.parse_args()

    print("\n=== Clearing site cache ===")
    run(["docker", "exec", CONTAINER, "bash", "-lc",
         f"cd /home/frappe/frappe-bench && bench --site {SITE} clear-cache"])

    print("\n=== Clearing website cache ===")
    run(["docker", "exec", CONTAINER, "bash", "-lc",
         f"cd /home/frappe/frappe-bench && bench --site {SITE} clear-website-cache"])

    if args.restart:
        print("\n=== Restarting backend (for hooks.py changes) ===")
        run(["docker", "restart", CONTAINER])

    print("\nDone. Next page request will re-resolve templates and re-render.")


if __name__ == "__main__":
    main()
