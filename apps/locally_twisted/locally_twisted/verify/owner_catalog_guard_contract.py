"""Verify owner-like users cannot directly mutate protected catalog records."""
from __future__ import annotations

from typing import Any, Callable

import frappe

from locally_twisted.owner_catalog_guard import (
    OWNER_ACCESS_ROLE,
    catalog_guard_context,
)


OWNER_USER = "locallytwisted@gmail.com"
PROBE_ITEM_INSERT = "LT-OWNER-GUARD-INSERT"
PROBE_ITEM_EXISTING = "LT-OWNER-GUARD-EXISTING"
PROBE_ITEM_CONTEXT = "LT-OWNER-GUARD-CONTEXT"
PROBE_ATTRIBUTE = "LT Owner Guard Attribute"
PROBE_ITEM_GROUP = "LT Owner Guard Group"
PROBE_SLIDESHOW = "LT Owner Guard Slideshow Probe"


def run() -> dict[str, Any]:
    failures: list[str] = []
    probes: list[dict[str, Any]] = []

    if not frappe.db.exists("User", OWNER_USER):
        failures.append(f"missing owner user {OWNER_USER}")
        return _report(failures, probes)

    roles = set(frappe.get_roles(OWNER_USER))
    if OWNER_ACCESS_ROLE not in roles:
        failures.append(f"{OWNER_USER} missing {OWNER_ACCESS_ROLE}")

    _set_admin()
    _cleanup_probe_records()
    _ensure_probe_records()
    frappe.db.commit()
    probes.append(_expect_blocked("owner_item_insert", _owner_item_insert))
    probes.append(_expect_blocked("owner_item_save", _owner_item_save))
    probes.append(_expect_blocked("owner_item_delete", _owner_item_delete))
    probes.append(_expect_blocked("owner_item_rename", _owner_item_rename))
    probes.append(_expect_blocked("owner_website_item_insert", _owner_website_item_insert))
    probes.append(_expect_blocked("owner_website_item_save", _owner_website_item_save))
    probes.append(_expect_blocked("owner_website_item_delete", _owner_website_item_delete))
    probes.append(_expect_blocked("owner_website_item_rename", _owner_website_item_rename))
    probes.append(_expect_blocked("owner_item_price_insert", _owner_item_price_insert))
    probes.append(_expect_blocked("owner_item_attribute_insert", _owner_item_attribute_insert))
    probes.append(_expect_blocked("owner_item_attribute_value_insert", _owner_item_attribute_value_insert))
    probes.append(_expect_blocked("owner_item_variant_attribute_insert", _owner_item_variant_attribute_insert))
    probes.append(_expect_blocked("owner_item_group_insert", _owner_item_group_insert))
    probes.append(_expect_blocked("owner_item_group_save", _owner_item_group_save))
    probes.append(_expect_blocked("owner_item_group_rename", _owner_item_group_rename))
    probes.append(_expect_blocked("owner_website_slideshow_insert", _owner_website_slideshow_insert))
    probes.append(_expect_blocked("owner_website_slideshow_item_insert", _owner_website_slideshow_item_insert))
    probes.append(_expect_blocked("owner_webshop_settings_save", _owner_webshop_settings_save))
    probes.append(_expect_allowed_with_context("owner_blueprint_context_item_insert", _context_item_insert))

    failures.extend(row["detail"] for row in probes if not row["ok"])
    _cleanup_probe_records()
    return _report(failures, probes)


def execute() -> dict[str, Any]:
    report = run()
    print(report)
    return report


def _report(failures: list[str], probes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": not failures,
        "owner_user": OWNER_USER,
        "probes": probes,
        "failures": failures,
    }


def _expect_blocked(label: str, fn: Callable[[], None]) -> dict[str, Any]:
    try:
        _as_owner(fn)
    except Exception as exc:
        frappe.db.rollback()
        text = str(exc)
        if "Please use Product Setup" in text or "protected" in text.lower():
            return {"probe": label, "ok": True, "blocked": True, "detail": text}
        return {"probe": label, "ok": False, "blocked": True, "detail": f"wrong error: {text}"}
    finally:
        _set_admin()
    frappe.db.rollback()
    return {"probe": label, "ok": False, "blocked": False, "detail": "mutation was not blocked"}


def _expect_allowed_with_context(label: str, fn: Callable[[], None]) -> dict[str, Any]:
    try:
        _as_owner(fn)
        frappe.db.rollback()
        return {"probe": label, "ok": True, "blocked": False, "detail": "allowed inside guarded context"}
    except Exception as exc:
        frappe.db.rollback()
        return {"probe": label, "ok": False, "blocked": True, "detail": str(exc)}
    finally:
        _set_admin()


def _as_owner(fn: Callable[[], None]) -> None:
    frappe.set_user(OWNER_USER)
    fn()


def _set_admin() -> None:
    frappe.set_user("Administrator")


def _owner_item_insert() -> None:
    frappe.get_doc(_item_doc(PROBE_ITEM_INSERT)).insert()


def _owner_item_save() -> None:
    doc = frappe.get_doc("Item", PROBE_ITEM_EXISTING)
    doc.item_name = f"{doc.item_name} Owner Edit"
    doc.save()


def _owner_item_delete() -> None:
    frappe.delete_doc("Item", PROBE_ITEM_EXISTING)


def _owner_item_rename() -> None:
    frappe.rename_doc("Item", PROBE_ITEM_EXISTING, f"{PROBE_ITEM_EXISTING}-RENAMED")


def _owner_website_item_insert() -> None:
    frappe.get_doc(
        {
            "doctype": "Website Item",
            "item_code": "LT-OWNER-GUARD-MISSING-ITEM",
            "web_item_name": "Owner Guard Missing Item",
            "route": "shop-items/break-lab/owner-guard-missing-item",
            "published": 1,
            "item_group": "Bouquets",
        }
    ).insert()


def _owner_item_price_insert() -> None:
    frappe.get_doc(
        {
            "doctype": "Item Price",
            "item_code": PROBE_ITEM_EXISTING,
            "price_list": "Standard Selling",
            "price_list_rate": 12,
            "selling": 1,
        }
    ).insert()


def _owner_website_item_save() -> None:
    doc = frappe.get_doc("Website Item", _probe_website_item())
    doc.web_item_name = f"{doc.web_item_name} Owner Edit"
    doc.save()


def _owner_website_item_delete() -> None:
    frappe.delete_doc("Website Item", _probe_website_item())


def _owner_website_item_rename() -> None:
    frappe.rename_doc("Website Item", _probe_website_item(), f"{_probe_website_item()}-RENAMED")


def _owner_item_attribute_insert() -> None:
    frappe.get_doc(
        {
            "doctype": "Item Attribute",
            "attribute_name": "LT Owner Guard Attribute Insert",
            "item_attribute_values": [
                {
                    "attribute_value": "Owner Guard Value",
                    "abbr": "OGVI",
                }
            ],
        }
    ).insert()


def _owner_item_attribute_value_insert() -> None:
    frappe.get_doc(
        {
            "doctype": "Item Attribute Value",
            "parent": PROBE_ATTRIBUTE,
            "parenttype": "Item Attribute",
            "parentfield": "item_attribute_values",
            "attribute_value": "Owner Guard Child Value",
            "abbr": "OGCV",
        }
    ).insert()


def _owner_item_variant_attribute_insert() -> None:
    frappe.get_doc(
        {
            "doctype": "Item Variant Attribute",
            "parent": PROBE_ITEM_EXISTING,
            "parenttype": "Item",
            "parentfield": "attributes",
            "attribute": PROBE_ATTRIBUTE,
            "attribute_value": "Guard Value",
        }
    ).insert()


def _owner_item_group_insert() -> None:
    frappe.get_doc(
        {
            "doctype": "Item Group",
            "item_group_name": "LT Owner Guard Group Insert",
            "parent_item_group": _parent_item_group(),
            "is_group": 0,
        }
    ).insert()


def _owner_item_group_save() -> None:
    doc = frappe.get_doc("Item Group", PROBE_ITEM_GROUP)
    doc.route = "shop-items/owner-guard-group-owner-edit"
    doc.save()


def _owner_item_group_rename() -> None:
    frappe.rename_doc("Item Group", PROBE_ITEM_GROUP, f"{PROBE_ITEM_GROUP} Renamed")


def _owner_website_slideshow_insert() -> None:
    frappe.get_doc(
        {
            "doctype": "Website Slideshow",
            "slideshow_name": "LT Owner Guard Direct Slideshow",
        }
    ).insert()


def _owner_website_slideshow_item_insert() -> None:
    frappe.get_doc(
        {
            "doctype": "Website Slideshow Item",
            "parent": PROBE_SLIDESHOW,
            "parenttype": "Website Slideshow",
            "parentfield": "slideshow_items",
            "image": "/files/owner-guard-gallery-probe.png",
            "heading": "Owner guard gallery probe",
        }
    ).insert()


def _owner_webshop_settings_save() -> None:
    settings = frappe.get_single("Webshop Settings")
    settings.hide_price_for_guest = 0 if int(settings.hide_price_for_guest or 0) else 1
    settings.save()


def _context_item_insert() -> None:
    with catalog_guard_context("blueprint_local_apply"):
        frappe.get_doc(_item_doc(PROBE_ITEM_CONTEXT)).insert()


def _item_doc(item_code: str) -> dict[str, Any]:
    return {
        "doctype": "Item",
        "item_code": item_code,
        "item_name": item_code.replace("-", " ").title(),
        "item_group": "Bouquets",
        "stock_uom": "Nos",
        "is_stock_item": 0,
        "is_sales_item": 1,
        "is_purchase_item": 0,
        "include_item_in_manufacturing": 0,
    }


def _ensure_probe_records() -> None:
    if not frappe.db.exists("Item", PROBE_ITEM_EXISTING):
        frappe.get_doc(_item_doc(PROBE_ITEM_EXISTING)).insert(ignore_permissions=True)
    if not frappe.db.exists("Item Attribute", PROBE_ATTRIBUTE):
        frappe.get_doc(
            {
                "doctype": "Item Attribute",
                "attribute_name": PROBE_ATTRIBUTE,
                "item_attribute_values": [
                    {
                        "attribute_value": "Guard Value",
                        "abbr": "OGV",
                    }
                ],
            }
        ).insert(ignore_permissions=True)
    if not frappe.db.exists("Item Group", PROBE_ITEM_GROUP):
        frappe.get_doc(
            {
                "doctype": "Item Group",
                "item_group_name": PROBE_ITEM_GROUP,
                "parent_item_group": _parent_item_group(),
                "is_group": 0,
                "route": "shop-items/owner-guard-group",
            }
        ).insert(ignore_permissions=True)
    if not frappe.db.exists("Website Item", {"item_code": PROBE_ITEM_EXISTING}):
        from webshop.webshop.doctype.website_item.website_item import make_website_item

        website_item = make_website_item(frappe.get_doc("Item", PROBE_ITEM_EXISTING), save=False)
        website_item.web_item_name = "Owner Guard Existing Website Item"
        website_item.item_group = "Bouquets"
        website_item.route = "shop-items/break-lab/owner-guard-existing"
        website_item.published = 0
        website_item.insert(ignore_permissions=True)
    if frappe.db.exists("Website Slideshow", PROBE_SLIDESHOW):
        return
    frappe.get_doc(
        {
            "doctype": "Website Slideshow",
            "name": PROBE_SLIDESHOW,
            "slideshow_name": PROBE_SLIDESHOW,
        }
    ).insert(ignore_permissions=True)


def _probe_website_item() -> str:
    name = frappe.db.get_value("Website Item", {"item_code": PROBE_ITEM_EXISTING}, "name")
    if not name:
        raise AssertionError("Missing owner guard probe Website Item")
    return name


def _parent_item_group() -> str:
    return (
        frappe.db.get_value("Item Group", {"is_group": 1}, "name")
        or frappe.db.get_value("Item Group", {}, "name")
        or "All Item Groups"
    )


def _cleanup_probe_records() -> None:
    _set_admin()
    frappe.db.rollback()
    for doctype, filters in (
        ("Website Slideshow", {"name": ["like", "LT Owner Guard%"]}),
        ("Website Item", {"item_code": ["like", "LT-OWNER-GUARD%"]}),
        ("Item Price", {"item_code": ["like", "LT-OWNER-GUARD%"]}),
        ("Item", {"item_code": ["like", "LT-OWNER-GUARD%"]}),
        ("Item Attribute", {"name": ["like", "LT Owner Guard%"]}),
        ("Item Group", {"name": ["like", "LT Owner Guard%"]}),
    ):
        for name in frappe.get_all(doctype, filters=filters, pluck="name"):
            frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
    frappe.db.commit()
