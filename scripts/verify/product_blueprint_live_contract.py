#!/usr/bin/env python3
"""Run the rollback-safe live ERPNext product blueprint contract.

Run:
  python scripts/verify/product_blueprint_live_contract.py
"""

from __future__ import annotations

import json
import subprocess
import sys

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.product_blueprint_contract.run"


def main() -> int:
    parse_noop_args(__doc__)
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        print("[PRODUCT BLUEPRINT LIVE CONTRACT] FAIL")
        print(proc.stdout)
        print(proc.stderr)
        return 1
    try:
        result = json.loads(proc.stdout.strip())
    except json.JSONDecodeError:
        print("[PRODUCT BLUEPRINT LIVE CONTRACT] FAIL")
        print(f"Non-JSON output: {proc.stdout}")
        print(proc.stderr)
        return 1
    if not result.get("ok"):
        print("[PRODUCT BLUEPRINT LIVE CONTRACT] FAIL")
        for failure in result.get("failures") or []:
            print(f"- {failure}")
        return 1
    print("[PRODUCT BLUEPRINT LIVE CONTRACT] PASS")
    print(f"  - blueprint: {result.get('blueprint')}")
    print(f"  - validation_status: {result.get('validation_status')}")
    print(f"  - rolled_back: {result.get('rolled_back')}")
    print(f"  - save_only_guard_counts_unchanged: {result.get('save_only_guard_counts_unchanged')}")
    print(f"  - rollback_guard_counts_unchanged: {result.get('rollback_guard_counts_unchanged')}")
    staff_setup = result.get("staff_setup") or {}
    if staff_setup:
        print(
            "  - staff_setup: "
            f"{staff_setup.get('configuration_choice_count')} configuration choices, "
            f"max={staff_setup.get('configuration_max')}, "
            f"variants={staff_setup.get('variant_combination_count')}, "
            f"media_rules={staff_setup.get('media_rules')}"
        )
    role_apply = result.get("role_apply") or {}
    if role_apply:
        roles = ", ".join(row.get("role") for row in role_apply.get("applied_roles") or [])
        print(f"  - role_apply: {roles}")
    owner_setup = result.get("owner_setup") or {}
    if owner_setup:
        print(
            "  - owner_setup: "
            f"user={owner_setup.get('user')}, "
            f"{owner_setup.get('variant_count')} variant(s), "
            f"{owner_setup.get('item_price_count')} price row(s), "
            f"published={owner_setup.get('published')}"
        )
    complex_media = result.get("complex_variant_media") or {}
    if complex_media:
        print(
            "  - complex_variant_media: "
            f"{complex_media.get('variant_count')} variant(s), "
            f"{complex_media.get('item_price_count')} price row(s), "
            f"selected_image={complex_media.get('selected_image')}"
        )
    local_apply = result.get("local_apply") or {}
    print(
        "  - local_apply: "
        f"{local_apply.get('variant_count')} variant(s), "
        f"{local_apply.get('item_price_count')} price row(s), "
        f"published={local_apply.get('published')}"
    )
    print(f"  - dynamic_add_on_checked: {local_apply.get('dynamic_add_on_checked')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
