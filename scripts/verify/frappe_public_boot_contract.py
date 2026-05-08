#!/usr/bin/env python3
"""Verify public Frappe script blocks include the LT boot asset map."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "templates"
BOOT_INCLUDE = 'templates/includes/frappe_public_boot.html'
BASE_SCRIPT_RE = re.compile(
    r"{%\s*block\s+base_scripts\s*%}(?P<body>.*?){%\s*endblock\s*%}",
    re.DOTALL,
)
FRAPPE_SCRIPT_MARKERS = (
    "frappe-web.bundle.js",
    "controls.bundle.js",
    "dialog.bundle.js",
    "web_form.bundle.js",
)


def main() -> int:
    parse_noop_args(__doc__)
    failures: list[str] = []
    include_path = TEMPLATES / "includes" / "frappe_public_boot.html"
    if not include_path.exists():
        failures.append(f"missing shared boot include: {include_path.relative_to(ROOT)}")
    else:
        include_text = include_path.read_text(encoding="utf-8")
        for marker in ("frappe.boot =", "frappe.boot.assets_json", "frappe.sys_defaults"):
            if marker not in include_text:
                failures.append(f"shared boot include missing {marker!r}")

    for path in sorted(TEMPLATES.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        for match in BASE_SCRIPT_RE.finditer(text):
            body = match.group("body")
            if any(marker in body for marker in FRAPPE_SCRIPT_MARKERS):
                if BOOT_INCLUDE not in body:
                    failures.append(
                        f"{path.relative_to(ROOT)} loads Frappe bundles without {BOOT_INCLUDE}"
                    )
                if "frappe.boot.assets_json" in body and BOOT_INCLUDE not in body:
                    failures.append(
                        f"{path.relative_to(ROOT)} duplicates the asset boot script instead of including it"
                    )

    if failures:
        print("[FRAPPE PUBLIC BOOT CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[FRAPPE PUBLIC BOOT CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
