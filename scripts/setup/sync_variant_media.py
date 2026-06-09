#!/usr/bin/env python3
"""Stage catalog source catalog media in Docker and map it onto ERPNext variants.

Run:
  python scripts/setup/sync_variant_media.py
  python scripts/setup/sync_variant_media.py --slug classic-arch
  python scripts/setup/sync_variant_media.py --dry-run
  python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "_resources" / "catalog-source"
CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
STAGE = "/tmp/lt-variant-media"


class SyncFail(Exception):
    pass


def run(cmd: list[str], *, timeout: int = 120) -> str:
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise SyncFail(
            "Command failed:\n"
            + " ".join(cmd)
            + f"\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout


def stage_inputs() -> None:
    if not (SOURCE / "catalog.json").exists():
        raise SyncFail(f"Missing source catalog: {SOURCE / 'catalog.json'}")
    if not (SOURCE / "images").exists():
        raise SyncFail(f"Missing source images directory: {SOURCE / 'images'}")

    run(["docker", "exec", CONTAINER, "bash", "-lc", f"rm -rf {STAGE} && mkdir -p {STAGE}/images"])
    run(["docker", "cp", str(SOURCE / "catalog.json"), f"{CONTAINER}:{STAGE}/catalog.json"])

    # Copying the whole image directory is simpler and keeps this repeatable
    # even when a product has many extra photos.
    run(["docker", "cp", str(SOURCE / "images") + "/.", f"{CONTAINER}:{STAGE}/images/"], timeout=300)


def bench_execute(*, slug: str | None, dry_run: bool, include_details: bool) -> Any:
    kwargs = {"data_dir": STAGE, "dry_run": dry_run, "include_details": include_details}
    if slug:
        kwargs["slug_filter"] = slug
    out = run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            "locally_twisted.seed.sync_variant_media.execute",
            "--kwargs",
            repr(kwargs),
        ],
        timeout=600,
    )
    try:
        parsed = json.loads(out.strip())
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        return parsed
    except json.JSONDecodeError as exc:
        raise SyncFail(f"sync_variant_media returned non-JSON output:\n{out}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--slug", help="Limit sync to one product slug")
    parser.add_argument("--dry-run", action="store_true", help="Preview mappings without writing Item.image")
    parser.add_argument("--include-details", action="store_true", help="Include image-label review details")
    parser.add_argument("--report", help="Write the JSON summary to this path")
    args = parser.parse_args()

    try:
        if not shutil.which("docker"):
            raise SyncFail("Docker CLI was not found on PATH.")
        stage_inputs()
        summary = bench_execute(slug=args.slug, dry_run=args.dry_run, include_details=args.include_details)
    except SyncFail as exc:
        print(f"[variant-media] FAIL: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(summary, indent=2)
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[variant-media] wrote {report_path}")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
