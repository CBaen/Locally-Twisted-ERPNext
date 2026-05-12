"""Sync Locally Twisted public/client-visible site branding.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_site_branding.execute
"""
from __future__ import annotations

import frappe


APP_NAME = "Locally Twisted"
LOGO_PATH = "/assets/locally_twisted/icons/lt-logo.png"
FAVICON_PATH = "/assets/locally_twisted/icons/lt-favicon.png?v=20260508-red-dog-1"
BRAND_HTML = f'<img src="{LOGO_PATH}?v=20260429-2" alt="{APP_NAME}" class="lt-logo">'

WEBSITE_FIELDS = {
    "app_name": APP_NAME,
    "brand_html": BRAND_HTML,
    "app_logo": LOGO_PATH,
    "splash_image": LOGO_PATH,
    "favicon": FAVICON_PATH,
    "home_page": "home",
    "head_html": "",
}

SYSTEM_FIELDS = {
    "app_name": APP_NAME,
}


def execute() -> dict[str, object]:
    """Apply the white-label website and system branding fields."""
    summary: dict[str, object] = {
        "website_settings": {},
        "system_settings": {},
        "committed": False,
    }

    website = frappe.get_single("Website Settings")
    website_changed = _apply_fields(website, WEBSITE_FIELDS, summary["website_settings"])
    if website_changed:
        website.save(ignore_permissions=True)

    system = frappe.get_single("System Settings")
    system_changed = _apply_fields(system, SYSTEM_FIELDS, summary["system_settings"])
    if system_changed:
        system.save(ignore_permissions=True)

    if website_changed or system_changed:
        frappe.clear_cache()
        frappe.db.commit()
        summary["committed"] = True
    else:
        frappe.clear_cache()

    return summary


def _apply_fields(doc, desired: dict[str, str], evidence: dict[str, object]) -> bool:
    changed = False
    for field, value in desired.items():
        before = doc.get(field)
        evidence[field] = {
            "before": before,
            "after": value,
            "changed": before != value,
        }
        if before != value:
            doc.set(field, value)
            changed = True
    return changed
