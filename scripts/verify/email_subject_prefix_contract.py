#!/usr/bin/env python3
"""Verify site-local Email Queue subject prefixes stay opt-in."""
from __future__ import annotations

import argparse
import sys
import types
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_PATH = PROJECT_ROOT / "apps" / "locally_twisted"
if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))


class DummyConf(dict):
    def get(self, key, default=None):  # noqa: A003 - mirrors frappe.conf.get
        return super().get(key, default)


class DummyEmail:
    def __init__(self, subject: str):
        self.subject = subject


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    if "frappe" not in sys.modules:
        sys.modules["frappe"] = types.SimpleNamespace(conf=DummyConf())

    from locally_twisted import email_delivery_guard

    original_conf = email_delivery_guard.frappe.conf
    try:
        email_delivery_guard.frappe.conf = DummyConf()
        plain = DummyEmail("New paid order - SO-1")
        email_delivery_guard.apply_site_email_subject_prefix(plain)
        if plain.subject != "New paid order - SO-1":
            print("FAIL: subject changed without lt_email_subject_prefix")
            return 1

        email_delivery_guard.frappe.conf = DummyConf(
            lt_email_subject_prefix="SMOKESCREEN"
        )
        prefixed = DummyEmail("New paid order - SO-1")
        email_delivery_guard.apply_site_email_subject_prefix(prefixed)
        if prefixed.subject != "SMOKESCREEN New paid order - SO-1":
            print(f"FAIL: subject was not prefixed: {prefixed.subject!r}")
            return 1

        already = DummyEmail("SMOKESCREEN New paid order - SO-1")
        email_delivery_guard.apply_site_email_subject_prefix(already)
        if already.subject != "SMOKESCREEN New paid order - SO-1":
            print(f"FAIL: prefix duplicated: {already.subject!r}")
            return 1
    finally:
        email_delivery_guard.frappe.conf = original_conf

    print("[EMAIL SUBJECT PREFIX CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
