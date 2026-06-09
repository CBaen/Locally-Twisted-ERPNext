#!/usr/bin/env python3
"""Summarize whether the reusable product-page architecture is ready to import or reopen.

Run:
  python scripts/verify/product_page_architecture_readiness.py
  python scripts/verify/product_page_architecture_readiness.py --json
  python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.product_page_architecture_readiness.run"
ROOT = Path(__file__).resolve().parents[2]
SOURCE_CATALOG = ROOT / "_resources" / "catalog-source" / "catalog.json"
CONTAINER_SOURCE_CATALOG = "/tmp/lt-catalog-source-catalog.json"


class ArchitectureReadinessFail(Exception):
    pass


def bench_execute(*, kwargs: dict[str, Any] | None = None) -> dict[str, Any]:
    cmd = ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD]
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=180)
    if proc.returncode != 0:
        raise ArchitectureReadinessFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise ArchitectureReadinessFail("architecture readiness audit returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ArchitectureReadinessFail(f"architecture readiness audit returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ArchitectureReadinessFail(
            f"architecture readiness audit returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        copy_source_catalog_to_container()
        result = bench_execute(kwargs={"source_catalog_path": CONTAINER_SOURCE_CATALOG})
    except ArchitectureReadinessFail as exc:
        print(f"[PRODUCT PAGE ARCHITECTURE READINESS] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[PRODUCT PAGE ARCHITECTURE READINESS] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result)

    return 0 if result.get("ok") else 2


def _print_summary(result: dict[str, Any]) -> None:
    print("[PRODUCT PAGE ARCHITECTURE READINESS] " + ("PASS" if result.get("ok") else "BLOCKED"))
    print(f"  technical_architecture_ok: {result.get('technical_architecture_ok')}")
    print(f"  import_reopen_ok: {result.get('import_reopen_ok')}")
    print(f"  generated_at: {result.get('generated_at')}")
    summary = result.get("summary") or {}
    for key in ("pass", "blocked", "partial", "deferred", "info"):
        print(f"  {key}: {summary.get(key, 0)}")
    for row in result.get("criteria") or []:
        print(f"  - {row.get('status')}: {row.get('id')} - {row.get('summary')}")
        blocker = row.get("blocker")
        if blocker:
            print(f"    blocker: {blocker}")
    blockers = result.get("blockers") or []
    if blockers:
        print("  blockers:")
        for blocker in blockers:
            print(f"    - {blocker}")
    architecture_blockers = result.get("technical_architecture_blockers") or []
    if architecture_blockers:
        print("  technical_architecture_blockers:")
        for blocker in architecture_blockers:
            print(f"    - {blocker}")
    import_reopen_blockers = result.get("import_reopen_blockers") or []
    if import_reopen_blockers:
        print("  import_reopen_blockers:")
        for blocker in import_reopen_blockers:
            print(f"    - {blocker}")


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def copy_source_catalog_to_container() -> None:
    if not SOURCE_CATALOG.exists():
        raise ArchitectureReadinessFail(f"missing host source catalog: {SOURCE_CATALOG.relative_to(ROOT)}")
    proc = subprocess.run(
        ["docker", "cp", str(SOURCE_CATALOG), f"{CONTAINER}:{CONTAINER_SOURCE_CATALOG}"],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise ArchitectureReadinessFail(
            f"docker cp failed for source catalog\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )


if __name__ == "__main__":
    sys.exit(main())
