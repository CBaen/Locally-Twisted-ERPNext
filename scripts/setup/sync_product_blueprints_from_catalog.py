#!/usr/bin/env python3
"""Create owner-editable Product Setup records from current Website Items.

Dry run:
  python scripts/setup/sync_product_blueprints_from_catalog.py

Write local Product Setup records:
  python scripts/setup/sync_product_blueprints_from_catalog.py --write
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "_resources" / "catalog-source"
CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.sync_product_blueprints_from_catalog.execute"
STAGE = "/tmp/lt-product-gallery-source"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="Create/fill Product Setup records locally")
    parser.add_argument(
        "--apply-gallery",
        action="store_true",
        help="After --write, project approved Product Setup gallery rows into Website Slideshow",
    )
    args = parser.parse_args()

    if not shutil.which("docker"):
        print("[PRODUCT SETUP CATALOG SYNC] FAIL", file=sys.stderr)
        print("Docker CLI was not found on PATH.", file=sys.stderr)
        return 1
    if args.apply_gallery and not args.write:
        print("[PRODUCT SETUP CATALOG SYNC] FAIL", file=sys.stderr)
        print("--apply-gallery requires --write.", file=sys.stderr)
        return 1
    try:
        _stage_gallery_source()
    except RuntimeError as exc:
        print("[PRODUCT SETUP CATALOG SYNC] FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    kwargs = {"write": args.write, "apply_gallery": args.apply_gallery, "data_dir": STAGE}

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
            repr(kwargs),
        ],
        text=True,
        capture_output=True,
        timeout=600,
    )
    if proc.returncode != 0:
        print("[PRODUCT SETUP CATALOG SYNC] FAIL", file=sys.stderr)
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    text = proc.stdout.strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        print("[PRODUCT SETUP CATALOG SYNC] FAIL", file=sys.stderr)
        print(f"Non-JSON output: {text}", file=sys.stderr)
        return 1
    summary = result.get("summary") or {}
    mode = "WRITE" if args.write else "DRY RUN"
    print(f"[PRODUCT SETUP CATALOG SYNC] {mode} PASS")
    print(f"  website_items: {result.get('website_items')}")
    print(f"  would_create: {summary.get('would_create')}")
    print(f"  would_update: {summary.get('would_update')}")
    print(f"  created: {summary.get('created')}")
    print(f"  updated: {summary.get('updated')}")
    print(f"  projected: {summary.get('projected')}")
    return 0


def _run(cmd: list[str], *, timeout: int = 120) -> None:
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(cmd)
            + f"\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )


def _stage_gallery_source() -> None:
    if not (SOURCE / "catalog.json").exists():
        raise RuntimeError(f"Missing source catalog: {SOURCE / 'catalog.json'}")
    if not (SOURCE / "images").exists():
        raise RuntimeError(f"Missing source images directory: {SOURCE / 'images'}")
    _run(["docker", "exec", CONTAINER, "bash", "-lc", f"rm -rf {STAGE} && mkdir -p {STAGE}/images"])
    _run(["docker", "cp", str(SOURCE / "catalog.json"), f"{CONTAINER}:{STAGE}/catalog.json"])
    _run(["docker", "cp", str(SOURCE / "images") + "/.", f"{CONTAINER}:{STAGE}/images/"], timeout=300)


if __name__ == "__main__":
    sys.exit(main())
