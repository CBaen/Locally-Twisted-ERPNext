"""Retire products removed from the public catalog on 2026-06-18."""
from __future__ import annotations

import frappe

from locally_twisted.shop_taxonomy import RETIRED_PRODUCT_CODES


def execute() -> None:
    missing: list[str] = []
    for item_code in RETIRED_PRODUCT_CODES:
        name = frappe.db.get_value("Website Item", {"item_code": item_code}, "name")
        if not name:
            missing.append(item_code)
            continue
        frappe.db.set_value(
            "Website Item",
            name,
            {
                "published": 0,
                "lt_product_page_type": "needs_review",
                "lt_commerce_lane": "needs_review",
            },
            update_modified=True,
        )

    if missing:
        frappe.log_error(
            title="LT retired product patch missing Website Items",
            message=", ".join(missing),
        )
    frappe.clear_cache()
