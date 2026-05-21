"""Verify owner-like users cannot directly mutate protected catalog records."""
from __future__ import annotations

from typing import Any, Callable

import frappe

from locally_twisted.owner_catalog_guard import (
    OWNER_ACCESS_ROLE,
    catalog_guard_context,
)


OWNER_USER = "locallytwisted@gmail.com"
PROBE_ITEM = "LT-OWNER-GUARD-PROBE"


def run() -> dict[str, Any]:
    failures: list[str] = []
    probes: list[dict[str, Any]] = []

    if not frappe.db.exists("User", OWNER_USER):
        failures.append(f"missing owner user {OWNER_USER}")
        return _report(failures, probes)

    roles = set(frappe.get_roles(OWNER_USER))
    if OWNER_ACCESS_ROLE not in roles:
        failures.append(f"{OWNER_USER} missing {OWNER_ACCESS_ROLE}")

    probes.append(_expect_blocked("owner_item_insert", _owner_item_insert))
    probes.append(_expect_blocked("owner_website_item_insert", _owner_website_item_insert))
    probes.append(_expect_blocked("owner_item_price_insert", _owner_item_price_insert))
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
    frappe.get_doc(_item_doc()).insert()


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
            "item_code": PROBE_ITEM,
            "price_list": "Standard Selling",
            "price_list_rate": 12,
            "selling": 1,
        }
    ).insert()


def _owner_webshop_settings_save() -> None:
    settings = frappe.get_single("Webshop Settings")
    settings.hide_price_for_guest = 0 if int(settings.hide_price_for_guest or 0) else 1
    settings.save()


def _context_item_insert() -> None:
    with catalog_guard_context("blueprint_local_apply"):
        frappe.get_doc(_item_doc()).insert()


def _item_doc() -> dict[str, Any]:
    return {
        "doctype": "Item",
        "item_code": PROBE_ITEM,
        "item_name": "Owner Guard Probe",
        "item_group": "Bouquets",
        "stock_uom": "Nos",
        "is_stock_item": 0,
        "is_sales_item": 1,
        "is_purchase_item": 0,
        "include_item_in_manufacturing": 0,
    }


def _cleanup_probe_records() -> None:
    _set_admin()
    frappe.db.rollback()
    for doctype, filters in (
        ("Website Item", {"item_code": ["like", "LT-OWNER-GUARD%"]}),
        ("Item Price", {"item_code": ["like", "LT-OWNER-GUARD%"]}),
        ("Item", {"item_code": ["like", "LT-OWNER-GUARD%"]}),
    ):
        for name in frappe.get_all(doctype, filters=filters, pluck="name"):
            frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
    frappe.db.commit()
