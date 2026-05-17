"""Local-only release smoke for a complex Product Setup item.

This intentionally creates local ERPNext records. Do not run on staging/live.
Use rollback-safe contracts for CI and this smoke only when GL approves a local
customer-journey proof.
"""
from __future__ import annotations

import time
from typing import Any

import frappe

from locally_twisted.locally_twisted.doctype.lt_product_blueprint.lt_product_blueprint import (
    apply_locally_from_desk,
)


EMPLOYEE_USER = "lt-product-release-proof@example.invalid"
EMPLOYEE_ROLE = "Item Manager"


def run(image_urls: dict[str, str] | None = None, slug: str | None = None) -> dict[str, Any]:
    if getattr(frappe.local, "site", None) != "frontend":
        frappe.throw("Product Blueprint release smoke is local-only and may run only on the frontend site.")
    image_urls = image_urls or {}
    missing_images = sorted(
        key for key in ("fallback", "small", "large_chrome") if not image_urls.get(key)
    )
    if missing_images:
        frappe.throw(f"Product Blueprint release smoke missing image URLs: {missing_images}")
    token = str(int(time.time()))
    slug = slug or f"release-proof-complex-product-{token}"
    employee_user = _ensure_employee_user()
    current_user = frappe.session.user
    previous_allow = frappe.conf.get("lt_allow_local_blueprint_apply")
    had_allow = "lt_allow_local_blueprint_apply" in frappe.conf

    try:
        frappe.set_user(employee_user)
        doc = _create_blueprint(slug, image_urls)
        frappe.conf.lt_allow_local_blueprint_apply = 1
        result = apply_locally_from_desk(doc.name)
    finally:
        frappe.set_user(current_user)
        if had_allow:
            frappe.conf.lt_allow_local_blueprint_apply = previous_allow
        else:
            frappe.conf.pop("lt_allow_local_blueprint_apply", None)

    website_item = frappe.get_doc("Website Item", result["website_item"])
    website_item.published = 1
    website_item.website_image = image_urls.get("fallback") or website_item.website_image
    website_item.save(ignore_permissions=True)
    frappe.db.commit()

    variant_item = f"{slug}-LARGE-CHROME-WEIGHT"
    configuration = {
        "schema_version": "lt-product-config-v1",
        "item_code": variant_item,
        "website_item_code": slug,
        "selected_options": {
            "Proof Size": "Large",
            "Proof Finish": "Chrome",
            "Proof Stand": "Weighted",
        },
        "configuration_groups": [
            {
                "key": "accent-pattern",
                "label": "Accent Pattern",
                "values": ["Confetti"],
            }
        ],
        "add_ons": [],
        "customizations": [],
    }

    return {
        "ok": True,
        "employee_user": employee_user,
        "blueprint": doc.name,
        "item_code": result["item_code"],
        "website_item": result["website_item"],
        "route": f"/{website_item.route}",
        "variant_item": variant_item,
        "variant_count": len(result.get("variants") or []),
        "item_price_count": len(result.get("item_prices") or []),
        "configuration": configuration,
        "images": image_urls,
        "published": int(website_item.published or 0),
    }


def _ensure_employee_user() -> str:
    if frappe.db.exists("User", EMPLOYEE_USER):
        user = frappe.get_doc("User", EMPLOYEE_USER)
        roles = {row.role for row in user.roles or []}
        if EMPLOYEE_ROLE not in roles:
            user.append("roles", {"role": EMPLOYEE_ROLE})
            user.save(ignore_permissions=True)
        return EMPLOYEE_USER

    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": EMPLOYEE_USER,
            "first_name": "Product",
            "last_name": "Release Proof",
            "enabled": 1,
            "send_welcome_email": 0,
            "roles": [{"role": EMPLOYEE_ROLE}],
        }
    )
    user.insert(ignore_permissions=True)
    return EMPLOYEE_USER


def _create_blueprint(slug: str, image_urls: dict[str, str]):
    return frappe.get_doc(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "Release Proof Complex Product",
            "product_slug": slug,
            "item_group": _first_leaf_item_group(),
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Local Preview Ready",
            "base_price": 75,
            "product_summary": "Local-only complex Product Setup proof for variants, pricing, and selected photos.",
            "option_rows": [
                _sku_axis("Proof Size", "Small\nMedium\nLarge\nGrand"),
                _sku_axis("Proof Finish", "Matte\nChrome\nSatin\nCrystal"),
                _sku_axis("Proof Stand", "Tabletop\nWeighted\nHanging"),
                {
                    "axis_name": "Accent Pattern",
                    "selection_behavior": "Configuration only",
                    "control_type": "Single select",
                    "required": 0,
                    "min_selections": 0,
                    "max_selections": 1,
                    "values": "Confetti\nCloud\nSwirl",
                },
            ],
            "media_rule_rows": [
                {
                    "rule_name": "Small size media",
                    "rule_type": "Selection group",
                    "selection_group": "Proof Size",
                    "selection_value": "Small",
                    "image": image_urls.get("small"),
                    "approved_for_customer": 1,
                },
                {
                    "rule_name": "Large chrome media",
                    "rule_type": "Selection combination",
                    "selection_conditions": "Proof Size=Large\nProof Finish=Chrome",
                    "image": image_urls.get("large_chrome"),
                    "approved_for_customer": 1,
                },
            ],
        }
    ).insert()


def _sku_axis(name: str, values: str) -> dict[str, Any]:
    return {
        "axis_name": name,
        "selection_behavior": "SKU-defining variant",
        "control_type": "Single select",
        "required": 1,
        "min_selections": 1,
        "max_selections": 1,
        "values": values,
    }


def _first_leaf_item_group() -> str:
    value = frappe.db.get_value("Item Group", {"is_group": 0}, "name") or frappe.db.get_value("Item Group", {}, "name")
    if not value:
        frappe.throw("No Item Group exists for product blueprint release smoke.")
    return value
