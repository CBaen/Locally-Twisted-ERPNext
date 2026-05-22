"""Create owner-editable Product Setup records from the current Website Items.

This sync does not mutate Item, Website Item, Item Price, route, or checkout
records. It only creates or fills LT Product Blueprint records so owners can
edit product business fields through the guarded Product Setup path.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

import frappe
from frappe.utils import flt, strip_html


PRICE_LIST = "Standard Selling"


def execute(write: bool = False) -> dict[str, Any]:
    rows = _website_items()
    existing = _existing_blueprints()
    planned: list[dict[str, Any]] = []
    created: list[str] = []
    updated: list[str] = []

    for row in rows:
        spec = _blueprint_spec(row)
        planned.append(_plan_row(spec, existing.get(spec["product_slug"])))
        if not write:
            continue
        result = _upsert_blueprint(spec, existing.get(spec["product_slug"]))
        if result["action"] == "created":
            created.append(result["name"])
        elif result["action"] == "updated":
            updated.append(result["name"])

    if write:
        frappe.db.commit()

    return {
        "ok": True,
        "dry_run": not write,
        "website_items": len(rows),
        "planned": planned,
        "created": created,
        "updated": updated,
        "summary": {
            "would_create": sum(1 for row in planned if row["action"] == "create"),
            "would_update": sum(1 for row in planned if row["action"] == "update"),
            "created": len(created),
            "updated": len(updated),
        },
    }


def _website_items() -> list[dict[str, Any]]:
    return frappe.get_all(
        "Website Item",
        filters={"item_code": ["!=", ""]},
        fields=[
            "name",
            "item_code",
            "web_item_name",
            "item_group",
            "published",
            "website_image",
            "slideshow",
            "short_description",
            "web_long_description",
            "lt_brand_description",
            "lt_product_details",
            "lt_product_page_type",
            "lt_commerce_lane",
        ],
        order_by="item_code asc",
    )


def _existing_blueprints() -> dict[str, str]:
    rows = frappe.get_all("LT Product Blueprint", fields=["name", "product_slug"])
    return {row["product_slug"]: row["name"] for row in rows if row.get("product_slug")}


def _blueprint_spec(row: dict[str, Any]) -> dict[str, Any]:
    item_code = row["item_code"]
    item = frappe.get_doc("Item", item_code)
    variants = _active_variants(item_code) if int(item.get("has_variants") or 0) else []
    option_rows = _option_rows(item, variants)
    price_rows = _price_rows(item_code, variants) if row.get("lt_commerce_lane") == "checkout" else []
    gallery_image_rows = _gallery_image_rows(row)
    media_rule_rows = _media_rule_rows(item_code, variants, row)
    base_price = min([price["price"] for price in price_rows], default=0)
    return {
        "product_name": row.get("web_item_name") or item.item_name or item_code,
        "product_slug": item_code,
        "item_group": row.get("item_group") or item.item_group,
        "page_template": _page_template(row.get("lt_product_page_type")),
        "buying_path": _buying_path(row.get("lt_commerce_lane")),
        "publish_status": "Draft",
        "shop_visibility": "Visible in shop" if int(row.get("published") or 0) else "Hidden from shop",
        "base_price": base_price,
        "product_summary": _summary(row),
        "product_story": row.get("lt_brand_description") or "",
        "product_details": row.get("lt_product_details") or "",
        "primary_image": row.get("website_image") or "",
        "target_item_code": item_code,
        "target_website_item": row.get("name"),
        "operator_notes": "Created from the current storefront catalog for guarded owner editing. Draft until reviewed.",
        "option_rows": option_rows,
        "price_rows": price_rows,
        "gallery_image_rows": gallery_image_rows,
        "media_rule_rows": media_rule_rows,
    }


def _plan_row(spec: dict[str, Any], existing_name: str | None) -> dict[str, Any]:
    missing_fields: list[str] = []
    if existing_name:
        missing_fields = _missing_update_fields(frappe.get_doc("LT Product Blueprint", existing_name), spec)
    return {
        "product_slug": spec["product_slug"],
        "product_name": spec["product_name"],
        "action": "update" if missing_fields else ("exists" if existing_name else "create"),
        "existing_blueprint": existing_name,
        "missing_fields": missing_fields,
        "price_rows": len(spec["price_rows"]),
        "option_rows": len(spec["option_rows"]),
        "gallery_image_rows": len(spec["gallery_image_rows"]),
        "media_rule_rows": len(spec["media_rule_rows"]),
        "shop_visibility": spec["shop_visibility"],
    }


def _upsert_blueprint(spec: dict[str, Any], existing_name: str | None) -> dict[str, str]:
    if existing_name:
        doc = frappe.get_doc("LT Product Blueprint", existing_name)
        action = "updated" if _fill_missing_fields(doc, spec) else "unchanged"
    else:
        doc = frappe.get_doc({"doctype": "LT Product Blueprint", **_base_fields(spec)})
        _replace_child_rows(doc, spec)
        doc.insert(ignore_permissions=True)
        return {"action": "created", "name": doc.name}

    if action == "updated":
        doc.save(ignore_permissions=True)
    return {"action": action, "name": doc.name}


def _fill_missing_fields(doc, spec: dict[str, Any]) -> bool:
    changed = False
    for fieldname, value in _base_fields(spec).items():
        current = getattr(doc, fieldname, None)
        if current in (None, "", 0) and value not in (None, ""):
            setattr(doc, fieldname, value)
            changed = True
    if not getattr(doc, "price_rows", None) and spec["price_rows"]:
        _replace_price_rows(doc, spec["price_rows"])
        changed = True
    if not getattr(doc, "option_rows", None) and spec["option_rows"]:
        _replace_option_rows(doc, spec["option_rows"])
        changed = True
    if not getattr(doc, "gallery_image_rows", None) and spec["gallery_image_rows"]:
        _replace_gallery_rows(doc, spec["gallery_image_rows"])
        changed = True
    if not getattr(doc, "media_rule_rows", None) and spec["media_rule_rows"]:
        _replace_media_rule_rows(doc, spec["media_rule_rows"])
        changed = True
    return changed


def _missing_update_fields(doc, spec: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for fieldname, value in _base_fields(spec).items():
        current = getattr(doc, fieldname, None)
        if current in (None, "", 0) and value not in (None, ""):
            missing.append(fieldname)
    if not getattr(doc, "price_rows", None) and spec["price_rows"]:
        missing.append("price_rows")
    if not getattr(doc, "option_rows", None) and spec["option_rows"]:
        missing.append("option_rows")
    if not getattr(doc, "gallery_image_rows", None) and spec["gallery_image_rows"]:
        missing.append("gallery_image_rows")
    if not getattr(doc, "media_rule_rows", None) and spec["media_rule_rows"]:
        missing.append("media_rule_rows")
    return missing


def _base_fields(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_name": spec["product_name"],
        "product_slug": spec["product_slug"],
        "item_group": spec["item_group"],
        "page_template": spec["page_template"],
        "buying_path": spec["buying_path"],
        "publish_status": spec["publish_status"],
        "shop_visibility": spec["shop_visibility"],
        "base_price": spec["base_price"],
        "product_summary": spec["product_summary"],
        "product_story": spec["product_story"],
        "product_details": spec["product_details"],
        "primary_image": spec["primary_image"],
        "target_item_code": spec["target_item_code"],
        "target_website_item": spec["target_website_item"],
        "operator_notes": spec["operator_notes"],
    }


def _replace_child_rows(
    doc,
    spec: dict[str, Any],
    *,
    include_prices: bool = True,
    include_gallery_media: bool = True,
) -> None:
    _replace_option_rows(doc, spec["option_rows"])
    if include_prices:
        _replace_price_rows(doc, spec["price_rows"])
    if include_gallery_media:
        _replace_gallery_rows(doc, spec["gallery_image_rows"])
        _replace_media_rule_rows(doc, spec["media_rule_rows"])


def _replace_option_rows(doc, rows: list[dict[str, Any]]) -> None:
    doc.option_rows = []
    for row in rows:
        doc.append("option_rows", row)


def _replace_price_rows(doc, rows: list[dict[str, Any]]) -> None:
    doc.price_rows = []
    for row in rows:
        doc.append("price_rows", row)


def _replace_gallery_rows(doc, rows: list[dict[str, Any]]) -> None:
    doc.gallery_image_rows = []
    for row in rows:
        doc.append("gallery_image_rows", row)


def _replace_media_rule_rows(doc, rows: list[dict[str, Any]]) -> None:
    doc.media_rule_rows = []
    for row in rows:
        doc.append("media_rule_rows", row)


def _active_variants(template_item: str) -> list[dict[str, Any]]:
    return frappe.get_all(
        "Item",
        filters={"variant_of": template_item, "disabled": 0},
        fields=["name", "item_name"],
        order_by="name asc",
    )


def _option_rows(item, variants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not variants:
        return []
    attrs = [row.attribute for row in item.get("attributes") or [] if row.attribute]
    if not attrs:
        attrs = sorted(_variant_attribute_values([row["name"] for row in variants]))
    value_map = _variant_attribute_values([row["name"] for row in variants])
    rows = []
    for attribute in attrs:
        values = sorted(value_map.get(attribute) or [])
        if not values:
            continue
        rows.append(
            {
                "axis_name": attribute,
                "role": "Sale unit option",
                "selection_behavior": "SKU-defining variant",
                "control_type": "Single select",
                "required": 1,
                "min_selections": 1,
                "max_selections": 1,
                "values": "\n".join(values),
                "pricing_behavior": "Server priced",
                "media_behavior": "No image change",
                "document_output": "Customer and operator",
            }
        )
    return rows


def _variant_attribute_values(variant_names: list[str]) -> dict[str, set[str]]:
    if not variant_names:
        return {}
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": ["in", variant_names]},
        fields=["parent", "attribute", "attribute_value"],
    )
    values: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row.get("attribute") and row.get("attribute_value"):
            values[row["attribute"]].add(row["attribute_value"])
    return values


def _price_rows(item_code: str, variants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets = [row["name"] for row in variants] or [item_code]
    prices = _price_map(targets)
    option_summary = _option_summary_map(targets)
    rows = []
    for target in targets:
        price = prices.get(target)
        if price is None:
            continue
        rows.append(
            {
                "item_code": target,
                "option_summary": option_summary.get(target) or target,
                "price": price,
                "enabled_for_checkout": 1,
            }
        )
    return rows


def _gallery_image_rows(website_item: dict[str, Any]) -> list[dict[str, Any]]:
    slideshow = website_item.get("slideshow")
    if not slideshow:
        return []
    rows = frappe.get_all(
        "Website Slideshow Item",
        filters={"parent": slideshow},
        fields=["image", "heading", "description"],
        order_by="idx asc",
    )
    return [
        {
            "image": row.get("image"),
            "heading": row.get("heading") or row.get("description") or "Product photo",
            "description": row.get("description") or "",
            "approved_for_customer": 1,
        }
        for row in rows
        if row.get("image")
    ]


def _media_rule_rows(
    item_code: str,
    variants: list[dict[str, Any]],
    website_item: dict[str, Any],
) -> list[dict[str, Any]]:
    if not variants:
        return []
    variant_codes = [row["name"] for row in variants]
    image_rows = frappe.get_all(
        "Item",
        filters={"name": ["in", variant_codes], "image": ["!=", ""]},
        fields=["name", "item_name", "image"],
        order_by="name asc",
    )
    fallback_image = website_item.get("website_image") or ""
    is_simple_checkout = (
        website_item.get("lt_product_page_type") == "simple_product"
        and website_item.get("lt_commerce_lane") == "checkout"
    )
    rules = []
    for row in image_rows:
        image = row.get("image")
        if not image or image == fallback_image:
            continue
        conditions = _variant_conditions(row["name"])
        rules.append(
            {
                "rule_name": f"{row['name']} selected photo",
                "rule_type": "Exact resolved variant",
                "selection_conditions": "\n".join(conditions),
                "variant_item": row["name"],
                "image": image,
                "approved_for_customer": 1 if is_simple_checkout else 0,
                "operator_note": (
                    "Backfilled from current simple checkout variant image."
                    if is_simple_checkout
                    else "Backfilled for review only; complex product variant images need Product Setup approval."
                ),
            }
        )
    return rules


def _variant_conditions(variant_item: str) -> list[str]:
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": variant_item},
        fields=["attribute", "attribute_value"],
        order_by="idx asc",
    )
    return [
        f"{row['attribute']}={row['attribute_value']}"
        for row in rows
        if row.get("attribute") and row.get("attribute_value")
    ]


def _price_map(item_codes: list[str]) -> dict[str, float]:
    rows = frappe.get_all(
        "Item Price",
        filters={"item_code": ["in", item_codes], "price_list": PRICE_LIST, "selling": 1},
        fields=["item_code", "price_list_rate"],
    )
    prices: dict[str, float] = {}
    for row in rows:
        price = flt(row.get("price_list_rate"))
        if price > 0 and row["item_code"] not in prices:
            prices[row["item_code"]] = price
    return prices


def _option_summary_map(item_codes: list[str]) -> dict[str, str]:
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": ["in", item_codes]},
        fields=["parent", "attribute", "attribute_value"],
        order_by="parent asc, idx asc",
    )
    by_parent: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_parent[row["parent"]].append(f"{row['attribute']}: {row['attribute_value']}")
    return {parent: "; ".join(values) for parent, values in by_parent.items()}


def _summary(row: dict[str, Any]) -> str:
    for fieldname in ("short_description", "web_long_description"):
        value = row.get(fieldname)
        if value:
            return strip_html(value).strip()
    return ""


def _page_template(value: str | None) -> str:
    return "Ready-to-order page" if value == "simple_product" else "Configurable product page"


def _buying_path(value: str | None) -> str:
    if value == "checkout":
        return "Direct checkout"
    if value == "quote_first":
        return "Quote first"
    return "Needs review"
