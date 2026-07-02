"""Remove known local-only proof products from the ERPNext catalog.

This is intentionally narrow. It is for cleaning verifier-created products that
are not part of the catalog_data source catalog before catalog import/reimport proof.
"""
from __future__ import annotations

from typing import Any

import frappe


TARGET_TEMPLATE_CODES = (
    "owner-blueprint-smoke-20260517-101250",
    "release-proof-complex-product-1779036020",
)


def execute(dry_run: bool = True) -> dict[str, Any]:
    if getattr(frappe.local, "site", None) != "frontend":
        frappe.throw("Local proof product cleanup may run only on the local frontend site.")

    targets = _collect_targets()
    if dry_run:
        return {"ok": True, "dry_run": True, **targets}

    for doctype, names in (
        ("File", targets["files"]),
        ("Website Item", targets["website_items"]),
        ("Item Price", targets["item_prices"]),
        ("LT Product Blueprint", targets["blueprints"]),
        ("Item", targets["variant_items"]),
        ("Item", targets["template_items"]),
    ):
        if doctype == "LT Product Blueprint" and not frappe.db.exists("DocType", doctype):
            continue
        for name in names:
            if frappe.db.exists(doctype, name):
                frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)

    frappe.db.commit()
    after = _collect_targets()
    survivors = {key: value for key, value in after.items() if value}
    return {
        "ok": not survivors,
        "dry_run": False,
        "deleted": targets,
        "survivors": survivors,
    }


def _collect_targets() -> dict[str, list[str]]:
    templates = list(TARGET_TEMPLATE_CODES)
    variants = frappe.get_all(
        "Item",
        filters={"variant_of": ["in", templates]},
        pluck="name",
        order_by="name asc",
    )
    item_codes = sorted(set(templates) | set(variants))
    website_items = frappe.get_all(
        "Website Item",
        filters={"item_code": ["in", templates]},
        pluck="name",
        order_by="name asc",
    )
    item_prices = frappe.get_all(
        "Item Price",
        filters={"item_code": ["in", item_codes]},
        pluck="name",
        order_by="name asc",
    )
    files = frappe.get_all(
        "File",
        filters={
            "attached_to_name": ["in", item_codes + website_items],
            "attached_to_doctype": ["in", ["Item", "Website Item"]],
        },
        pluck="name",
        order_by="name asc",
    )
    blueprints: list[str] = []
    if frappe.db.exists("DocType", "LT Product Blueprint"):
        blueprints = frappe.get_all(
            "LT Product Blueprint",
            filters={"product_slug": ["in", templates]},
            pluck="name",
            order_by="name asc",
        )
    existing_templates = frappe.get_all(
        "Item",
        filters={"name": ["in", templates]},
        pluck="name",
        order_by="name asc",
    )
    return {
        "template_items": list(existing_templates),
        "variant_items": list(variants),
        "website_items": list(website_items),
        "item_prices": list(item_prices),
        "files": list(files),
        "blueprints": list(blueprints),
    }
