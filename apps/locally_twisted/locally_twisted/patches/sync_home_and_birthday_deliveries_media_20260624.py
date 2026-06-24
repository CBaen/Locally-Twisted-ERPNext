"""Repair live homepage routing and Birthday Deliveries public media."""
from __future__ import annotations

import frappe

from locally_twisted.seed import sync_site_branding


PRODUCT_ITEM_CODE = "birthday-deliveries"
PRODUCT_ROUTE = "shop-items/bouquets/birthday-deliveries"
OLD_IMAGE = "/files/birthday-deliveries.png"
NEW_IMAGE = "/files/birthday-deliveries--extra-12.webp"


def execute() -> dict[str, object]:
    """Keep `/` on the landing page and promote the approved birthday photo."""
    summary = {
        "site_branding": sync_site_branding.execute(),
        "birthday_deliveries_media": _sync_birthday_deliveries_media(),
    }
    frappe.clear_cache()
    frappe.db.commit()
    return summary


def _sync_birthday_deliveries_media() -> dict[str, object]:
    evidence: dict[str, object] = {
        "website_item": "",
        "item_code": PRODUCT_ITEM_CODE,
        "old_image": OLD_IMAGE,
        "new_image": NEW_IMAGE,
        "file_exists": bool(frappe.db.exists("File", {"file_url": NEW_IMAGE})),
        "changed": [],
        "missing": [],
    }

    website_item = (
        frappe.db.get_value("Website Item", {"route": PRODUCT_ROUTE}, ["name", "item_code", "slideshow"], as_dict=True)
        or frappe.db.get_value("Website Item", {"item_code": PRODUCT_ITEM_CODE}, ["name", "item_code", "slideshow"], as_dict=True)
    )
    if not website_item:
        evidence["missing"].append("Website Item")
        _log_media_repair_issue(evidence)
        return evidence

    website_item_name = str(website_item.get("name") or "")
    item_code = str(website_item.get("item_code") or PRODUCT_ITEM_CODE)
    evidence["website_item"] = website_item_name
    evidence["item_code"] = item_code

    _set_value_if_needed("Website Item", website_item_name, "website_image", NEW_IMAGE, evidence)

    if frappe.db.exists("Item", item_code):
        _set_value_if_needed("Item", item_code, "image", NEW_IMAGE, evidence)
    else:
        evidence["missing"].append(f"Item:{item_code}")

    blueprint_name = frappe.db.get_value("LT Product Blueprint", {"product_slug": PRODUCT_ITEM_CODE}, "name")
    if blueprint_name:
        _set_value_if_needed("LT Product Blueprint", blueprint_name, "primary_image", NEW_IMAGE, evidence)
        removed_blueprint_rows = frappe.db.delete(
            "LT Product Blueprint Gallery Image",
            {
                "parent": blueprint_name,
                "image": OLD_IMAGE,
            },
        )
        if removed_blueprint_rows:
            evidence["changed"].append(f"LT Product Blueprint Gallery Image:removed_old:{removed_blueprint_rows}")

    slideshow_name = str(website_item.get("slideshow") or "")
    if slideshow_name and frappe.db.exists("Website Slideshow", slideshow_name):
        removed_slideshow_rows = frappe.db.delete(
            "Website Slideshow Item",
            {
                "parent": slideshow_name,
                "image": OLD_IMAGE,
            },
        )
        if removed_slideshow_rows:
            evidence["changed"].append(f"Website Slideshow Item:removed_old:{removed_slideshow_rows}")

    if evidence["missing"] or not evidence["file_exists"]:
        _log_media_repair_issue(evidence)
    return evidence


def _set_value_if_needed(
    doctype: str,
    name: str,
    fieldname: str,
    value: str,
    evidence: dict[str, object],
) -> None:
    before = frappe.db.get_value(doctype, name, fieldname)
    if before == value:
        return
    frappe.db.set_value(doctype, name, fieldname, value, update_modified=True)
    evidence["changed"].append(f"{doctype}:{name}:{fieldname}:{before}->{value}")


def _log_media_repair_issue(evidence: dict[str, object]) -> None:
    frappe.log_error(
        title="LT Birthday Deliveries media repair warning",
        message=frappe.as_json(evidence, indent=2),
    )
