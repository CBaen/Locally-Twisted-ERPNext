"""Local browser-proof helpers for the multi-color purchasable tranche.

These helpers intentionally mutate the local ERPNext site only when called by
the CLI wrapper. They snapshot current Website Item contracts, apply the
temporary checkout contract needed for browser proof, and restore from the
snapshot afterward.
"""
from __future__ import annotations

import json
from typing import Any

import frappe

from locally_twisted.verify.multi_color_purchasable_rehearsal_contract import MULTI_COLOR_PRODUCTS


class ContractFail(Exception):
    pass


def apply_open_contracts() -> dict[str, Any]:
    snapshot = _snapshot()
    for row in snapshot["products"]:
        frappe.db.set_value(
            "Website Item",
            row["website_item_name"],
            {
                "lt_product_page_type": "simple_product",
                "lt_commerce_lane": "checkout",
            },
            update_modified=False,
        )
    frappe.clear_cache()
    frappe.db.commit()
    return {"ok": True, **snapshot}


def restore_contracts(snapshot_json: str | None = None, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    if snapshot is None:
        if not snapshot_json:
            raise ContractFail("restore_contracts requires snapshot_json or snapshot")
        snapshot = json.loads(snapshot_json)
    products = snapshot.get("products") or []
    if not products:
        raise ContractFail("restore_contracts received no products")
    restored: list[dict[str, Any]] = []
    for row in products:
        website_item_name = row.get("website_item_name")
        if not website_item_name:
            raise ContractFail(f"restore row missing website_item_name: {row}")
        frappe.db.set_value(
            "Website Item",
            website_item_name,
            {
                "lt_product_page_type": row.get("product_page_type"),
                "lt_commerce_lane": row.get("commerce_lane"),
            },
            update_modified=False,
        )
        restored.append(
            {
                "website_item_name": website_item_name,
                "item_code": row.get("item_code"),
                "product_page_type": row.get("product_page_type"),
                "commerce_lane": row.get("commerce_lane"),
            }
        )
    frappe.clear_cache()
    frappe.db.commit()
    return {"ok": True, "restored": restored}


def current_contracts() -> dict[str, Any]:
    return {"ok": True, **_snapshot()}


def _snapshot() -> dict[str, Any]:
    product_codes = sorted(MULTI_COLOR_PRODUCTS)
    rows = frappe.get_all(
        "Website Item",
        filters={"item_code": ["in", product_codes]},
        fields=[
            "name",
            "item_code",
            "web_item_name",
            "route",
            "item_group",
            "published",
            "lt_product_page_type",
            "lt_commerce_lane",
        ],
        order_by="item_code asc",
    )
    found = {row["item_code"] for row in rows}
    missing = sorted(set(product_codes) - found)
    if missing:
        raise ContractFail(f"missing Website Items for multi-color browser proof: {missing}")
    products: list[dict[str, Any]] = []
    for row in rows:
        if not int(row.get("published") or 0):
            raise ContractFail(f"{row['item_code']} Website Item is not published")
        route = str(row.get("route") or "").strip()
        if not route:
            raise ContractFail(f"{row['item_code']} Website Item has no route")
        products.append(
            {
                "website_item_name": row["name"],
                "item_code": row["item_code"],
                "web_item_name": row.get("web_item_name"),
                "route": "/" + route.lstrip("/"),
                "item_group": row.get("item_group"),
                "published": bool(row.get("published")),
                "product_page_type": row.get("lt_product_page_type"),
                "commerce_lane": row.get("lt_commerce_lane"),
                "color_axes": list(MULTI_COLOR_PRODUCTS[row["item_code"]]["color_axes"]),
            }
        )
    return {
        "product_count": len(products),
        "products": products,
    }
