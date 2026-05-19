#!/usr/bin/env python3
"""Verify school/seasonal color preset product behavior in local ERPNext."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.school_seasonal_color_preset_contract.run"
ROOT = Path(__file__).resolve().parents[2]


class SchoolSeasonalPresetContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    cmd = ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=180)
    if proc.returncode != 0:
        raise SchoolSeasonalPresetContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise SchoolSeasonalPresetContractFail("preset contract returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SchoolSeasonalPresetContractFail(f"preset contract returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise SchoolSeasonalPresetContractFail(
            f"preset contract returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the full JSON report")
    parser.add_argument("--report", help="Write the full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except SchoolSeasonalPresetContractFail as exc:
        print(f"[SCHOOL SEASONAL COLOR PRESET CONTRACT] FAIL\n  - {exc}")
        return 1

    rendered = json.dumps(result, indent=2, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[SCHOOL SEASONAL COLOR PRESET CONTRACT] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result)

    return 0 if result.get("ok") else 2


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate


def _print_summary(result: dict[str, Any]) -> None:
    status = "PASS" if result.get("ok") else "FAIL"
    print(f"[SCHOOL SEASONAL COLOR PRESET CONTRACT] {status}")
    print(f"  quote_request_products: {len(result.get('quote_request_products') or [])}")
    print(f"  graduation_checkout_products: {result.get('graduation_checkout_products')}")
    print(f"  raw_checkout_color_axes: {result.get('raw_checkout_color_axes')}")
    for row in result.get("graduation_variants") or []:
        print(
            "  graduation: "
            f"{row.get('template')} active={row.get('active_variant_count')} "
            f"expected={row.get('expected_variant_count')} "
            f"raw_color={row.get('raw_color_variant_count')}"
        )
    if result.get("failures"):
        for failure in result.get("failures") or []:
            print(f"  - {failure}")


if __name__ == "__main__":
    sys.exit(main())
