#!/usr/bin/env python3
"""Verify no-snapshot readiness gate command-packet path handling.

Run:
  python scripts/verify/product_import_readiness_gate_contract.py
"""
from __future__ import annotations

import sys

from _cli import parse_noop_args
from product_import_readiness_gate import _snapshot_display_path

EXPECTED_PLACEHOLDER = "<fresh current-state-snapshot-* required>"


def main() -> int:
    parse_noop_args(__doc__)

    failures: list[str] = []
    try:
        display_path = _snapshot_display_path([])
    except ValueError as exc:
        failures.append(f"empty snapshot list raised ValueError: {exc}")
    else:
        if display_path != EXPECTED_PLACEHOLDER:
            failures.append(f"empty snapshot list returned {display_path!r}, expected {EXPECTED_PLACEHOLDER!r}")

    if failures:
        print("[PRODUCT IMPORT READINESS GATE CONTRACT] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[PRODUCT IMPORT READINESS GATE CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
