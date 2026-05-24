"""Apply the approved shop taxonomy to ERPNext catalog records."""
from __future__ import annotations

from typing import Any

import frappe

from locally_twisted.owner_catalog_guard import catalog_guard_context
from locally_twisted.shop_taxonomy import (
    CategorySpec,
    LEGACY_CATEGORY_ROUTES,
    LEGACY_PRIMARY_GROUPS,
    OCCASION_ROOT,
    PRIMARY_CATEGORY_SPECS,
    PRODUCT_TAXONOMY,
    SECONDARY_CATEGORY_SPECS,
    SHOP_ROOT,
    category_slug,
    product_route,
)


def dry_run() -> dict[str, Any]:
    return execute(apply=False, commit=False)


def apply_approved(commit: bool = True) -> dict[str, Any]:
    return execute(apply=True, commit=commit)


def execute(apply: bool = False, commit: bool = False) -> dict[str, Any]:
    """Sync source-owned primary and secondary product categories."""
    report: dict[str, Any] = {
        "apply": apply,
        "groups_created": [],
        "groups_updated": [],
        "legacy_groups_hidden": [],
        "website_items_updated": [],
        "items_updated": 0,
        "variant_templates_checked": len(PRODUCT_TAXONOMY),
        "variant_items_updated": 0,
        "secondary_rows_written": 0,
        "failures": [],
    }

    if not frappe.db.exists("Item Group", SHOP_ROOT):
        report["failures"].append(f"missing root Item Group: {SHOP_ROOT}")
        return _finish(report, commit=False)

    with catalog_guard_context("shop_taxonomy_sync"):
        _ensure_group(
            CategorySpec(
                name=OCCASION_ROOT,
                parent="All Item Groups",
                route="shop-occasions",
                weightage=900,
                show_in_website=0,
                is_group=1,
            ),
            report,
            apply=apply,
        )
        for spec in PRIMARY_CATEGORY_SPECS:
            _ensure_group(spec, report, apply=apply)
        for spec in SECONDARY_CATEGORY_SPECS:
            _ensure_group(spec, report, apply=apply)
        _hide_legacy_groups(report, apply=apply)
        _sync_products(report, apply=apply)

    return _finish(report, commit=commit and apply)


def _finish(report: dict[str, Any], *, commit: bool) -> dict[str, Any]:
    report["ok"] = not report["failures"]
    if report["failures"]:
        frappe.db.rollback()
    elif commit:
        frappe.db.commit()
    return report


def _ensure_group(spec: CategorySpec, report: dict[str, Any], *, apply: bool) -> None:
    existing = frappe.db.exists("Item Group", spec.name)
    if not existing:
        report["groups_created"].append(spec.name)
        if not apply:
            return
        doc = frappe.get_doc(
            {
                "doctype": "Item Group",
                "name": spec.name,
                "item_group_name": spec.name,
                "parent_item_group": spec.parent,
                "is_group": spec.is_group,
                "show_in_website": spec.show_in_website,
                "weightage": spec.weightage,
            }
        )
        _set_route_if_available(doc, spec.route)
        doc.insert(ignore_permissions=True)
        return

    doc = frappe.get_doc("Item Group", existing)
    changes: dict[str, Any] = {}
    for field, value in (
        ("item_group_name", spec.name),
        ("parent_item_group", spec.parent),
        ("is_group", spec.is_group),
        ("show_in_website", spec.show_in_website),
        ("weightage", spec.weightage),
    ):
        if getattr(doc, field, None) != value:
            changes[field] = value
            setattr(doc, field, value)
    if _has_field(doc, "route") and getattr(doc, "route", None) != spec.route:
        changes["route"] = spec.route
        doc.route = spec.route
    if not changes:
        return
    report["groups_updated"].append({"name": spec.name, "changes": changes})
    if apply:
        doc.save(ignore_permissions=True)


def _hide_legacy_groups(report: dict[str, Any], *, apply: bool) -> None:
    for index, group in enumerate(LEGACY_PRIMARY_GROUPS, start=1):
        if not frappe.db.exists("Item Group", group):
            continue
        route = LEGACY_CATEGORY_ROUTES.get(group, f"shop-items/{category_slug(group)}")
        doc = frappe.get_doc("Item Group", group)
        changes: dict[str, Any] = {}
        if int(getattr(doc, "show_in_website", 0) or 0) != 0:
            changes["show_in_website"] = 0
            doc.show_in_website = 0
        target_weightage = 900 + index
        if int(getattr(doc, "weightage", 0) or 0) != target_weightage:
            changes["weightage"] = target_weightage
            doc.weightage = target_weightage
        if _has_field(doc, "route") and getattr(doc, "route", None) != route:
            changes["route"] = route
            doc.route = route
        if not changes:
            continue
        report["legacy_groups_hidden"].append({"name": group, "changes": changes})
        if apply:
            doc.save(ignore_permissions=True)


def _sync_products(report: dict[str, Any], *, apply: bool) -> None:
    for item_code, taxonomy in PRODUCT_TAXONOMY.items():
        primary = taxonomy["primary"]
        secondary = taxonomy["secondary"]
        expected_route = product_route(item_code)
        item_name = frappe.db.exists("Item", item_code)
        website_item_name = frappe.db.exists("Website Item", {"item_code": item_code})

        if not item_name:
            report["failures"].append(f"missing Item: {item_code}")
            continue
        if not website_item_name:
            report["failures"].append(f"missing Website Item for: {item_code}")
            continue

        template_changed = _item_group(item_code) != primary
        variant_count = frappe.db.count("Item", {"variant_of": item_code})
        bad_variant_count = frappe.db.count("Item", {"variant_of": item_code, "item_group": ["!=", primary]})
        if template_changed:
            report["items_updated"] += 1
        report["variant_items_updated"] += bad_variant_count

        wi = frappe.get_doc("Website Item", website_item_name)
        if not _has_field(wi, "website_item_groups"):
            report["failures"].append("Website Item is missing website_item_groups child table")
            continue

        current_secondary = [
            row.item_group
            for row in getattr(wi, "website_item_groups", [])
            if getattr(row, "item_group", None)
        ]
        website_changed = (
            wi.item_group != primary
            or wi.route != expected_route
            or current_secondary != [secondary]
        )
        if website_changed:
            report["website_items_updated"].append(
                {
                    "item_code": item_code,
                    "primary": primary,
                    "secondary": secondary,
                    "route": expected_route,
                }
            )
            report["secondary_rows_written"] += 1

        if not apply:
            continue

        if template_changed:
            frappe.db.set_value("Item", item_code, "item_group", primary, update_modified=False)
        if bad_variant_count:
            frappe.db.sql(
                """
                UPDATE `tabItem`
                   SET item_group = %s
                 WHERE variant_of = %s
                   AND item_group != %s
                """,
                (primary, item_code, primary),
            )
        elif variant_count:
            # Keep this branch explicit so the report distinguishes checked variants.
            pass

        if website_changed:
            wi.item_group = primary
            wi.route = expected_route
            wi.set("website_item_groups", [{"item_group": secondary}])
            wi.save(ignore_permissions=True)


def _item_group(item_code: str) -> str | None:
    return frappe.db.get_value("Item", item_code, "item_group")


def _set_route_if_available(doc: Any, route: str) -> None:
    if _has_field(doc, "route"):
        doc.route = route


def _has_field(doc: Any, fieldname: str) -> bool:
    return bool(doc.meta and doc.meta.has_field(fieldname))
