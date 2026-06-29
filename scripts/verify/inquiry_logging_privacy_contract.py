#!/usr/bin/env python3
"""Static guard that inquiry failure logs do not store raw form payload PII."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOOK_SOURCE = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "www" / "book.py"

REQUIRED_MARKERS = (
    "_safe_lead_creation_failure_context",
    "lt_safe_inquiry_failure_context_v1",
    "safe_context:",
    "required_field_present",
    "uploaded_file_count",
)

FORBIDDEN_MARKERS = (
    "{k: v for k, v in (frappe.form_dict or {}).items()",
    "payload: {payload}",
    "form_url:",
    "remote_ip:",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    source = BOOK_SOURCE.read_text(encoding="utf-8")
    failures = []
    for marker in REQUIRED_MARKERS:
        if marker not in source:
            failures.append(f"book.py missing safe logging marker: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in source:
            failures.append(f"book.py still contains raw/sensitive logging marker: {marker}")

    if failures:
        print("[INQUIRY LOGGING PRIVACY CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[INQUIRY LOGGING PRIVACY CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
