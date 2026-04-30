"""
enable_webshop_variants.py — Flip Webshop Settings to enable variants + attribute filters.

Run once on every site (idempotent). Not a fixture because Webshop Settings has
many other fields Jeff may edit (Stripe gateway account, checkout flags, etc.) —
fixturing the whole doc would risk overwriting his config.

Per migration-guard skill: this is a settings change, not schema. Loud-fail if
the setting doesn't apply.

Run:
  python scripts/setup/enable_webshop_variants.py
"""
from __future__ import annotations

import subprocess
import sys

CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"


def main() -> int:
    cmd = (
        "import frappe;"
        "frappe.db.set_value('Webshop Settings', 'Webshop Settings', "
        "{'enable_variants': 1, 'enable_attribute_filters': 1, 'show_attribute_dropdowns': 1});"
        "frappe.db.commit();"
        "v = frappe.db.get_value('Webshop Settings', 'Webshop Settings', "
        "['enable_variants','enable_attribute_filters','show_attribute_dropdowns'], as_dict=True);"
        "print('VERIFY:', v)"
    )
    p = subprocess.run(
        ["docker", "exec", "-i", CONTAINER,
         "bench", "--site", SITE, "console", "--no-banner"],
        input=cmd, text=True, capture_output=True, timeout=60
    )
    print(p.stdout)
    if p.returncode != 0:
        print(f"STDERR: {p.stderr}", file=sys.stderr)
        print(f"FATAL: bench console exit {p.returncode}", file=sys.stderr)
        return 1
    if "VERIFY:" not in p.stdout:
        print("FATAL: verification line not in output — settings may not have applied", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
