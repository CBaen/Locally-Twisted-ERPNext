#!/usr/bin/env python3
"""Generate the generic ProductPatternContract architecture report.

Run:
  python scripts/verify/product_pattern_contract_report.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
DEFAULT_OUTPUT = Path("output/product-pattern-contract-report.json")
SOURCE_CATALOG = Path("_resources/odoo-live/catalog.json")
CONTAINER_SOURCE_CATALOG = "/tmp/lt-odoo-live-catalog.json"


class ContractFail(Exception):
    pass


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None) -> Any:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=180)
    if proc.returncode != 0:
        raise ContractFail(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise ContractFail(f"{method} returned empty output")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"{method} returned non-JSON output: {text}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Host-side JSON report path.",
    )
    return parser.parse_args()


def copy_source_catalog_to_container() -> None:
    proc = subprocess.run(
        ["docker", "cp", str(SOURCE_CATALOG), f"{CONTAINER}:{CONTAINER_SOURCE_CATALOG}"],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise ContractFail(
            f"docker cp failed for source catalog\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )


def main() -> int:
    args = parse_args()
    try:
        if not SOURCE_CATALOG.exists():
            raise ContractFail(f"missing host source catalog: {SOURCE_CATALOG}")
        copy_source_catalog_to_container()
        result = bench_execute(
            "locally_twisted.verify.product_pattern_contract_report.run",
            kwargs={"source_catalog_path": CONTAINER_SOURCE_CATALOG},
        )
    except ContractFail as exc:
        print(f"[PRODUCT PATTERN CONTRACT REPORT] FAIL\n  - {exc}")
        return 1

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    summary = result.get("summary") or {}
    print("[PRODUCT PATTERN CONTRACT REPORT] " + ("PASS" if result.get("ok") else "FAIL"))
    print(f"  - report: {output}")
    print(f"  - priced Website Items: {result.get('priced_website_item_count')}")
    print(f"  - checkout statuses: {summary.get('checkout_status_counts')}")
    print(f"  - fail-loud states: {summary.get('fail_loud_state_counts')}")
    for failure in result.get("failures") or []:
        print(f"  - {failure}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
