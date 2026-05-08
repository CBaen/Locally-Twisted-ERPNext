"""Repair variant templates where optional add-ons were imported as required axes.

Run in-process:
    bench --site frontend execute locally_twisted.seed.repair_optional_addon_variants.execute

This is idempotent. It creates required-choice variants, disables the older
optional-add-on variants, and rebuilds the Webshop variant cache.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from urllib.request import Request, urlopen

import frappe

from locally_twisted.catalog_variant_rules import (
    OPTIONAL_ADDON_ATTRIBUTES,
    is_required_variant_attribute,
    project_required_variant_combo,
)
from locally_twisted.commerce_rules import PRICE_LIST


SITE_FILES_DIR = Path("/home/frappe/frappe-bench/sites/frontend/public/files")

BOUQUET_SIZE_IMAGE_IDS = {
    "unicorn-bouquet": {"Small": 250, "Medium": 251, "Large": 252},
    "mickey-mouse-bouquet": {"Small": 253, "Medium": 254, "Large": 255},
    "minion-bouquet": {"Small": 369, "Medium": 370, "Large": 371},
    "encanto-bouquet": {"Small": 372, "Medium": 373, "Large": 374},
    "stitch-bouquet": {"Small": 408, "Medium": 409, "Large": 410},
    "flamingo-bouquet": {"Small": 414, "Medium": 415, "Large": 416},
    "football-bouquet": {"Small": 417, "Medium": 418, "Large": 419},
    "soccer-bouquet": {"Small": 420, "Medium": 421, "Large": 422},
    "over-the-hill-bouquet": {"Small": 423, "Medium": 424, "Large": 425},
    "space-bouquet": {"Small": 426, "Medium": 427, "Large": 428},
    "paw-patrol-bouquet": {"Small": 1083, "Medium": 1084, "Large": 1085},
    "elsa-bouquet": {"Small": 1086, "Medium": 1087, "Large": 1088},
    "holy-cow-bouquet": {"Small": 1089, "Medium": 1090, "Large": 1091},
}


def _variant_attrs(item_code: str) -> dict[str, str]:
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": item_code},
        fields=["attribute", "attribute_value"],
        order_by="idx asc",
    )
    return {
        row.attribute: row.attribute_value
        for row in rows
        if row.attribute and row.attribute_value
    }


def _template_required_attrs(template_code: str) -> list[str]:
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": template_code},
        fields=["attribute"],
        order_by="idx asc",
    )
    return [
        row.attribute
        for row in rows
        if row.attribute and is_required_variant_attribute(row.attribute)
    ]


def _set_template_required_attrs(template_code: str, required_attrs: list[str]) -> None:
    frappe.db.delete(
        "Item Variant Attribute",
        {
            "parent": template_code,
            "parenttype": "Item",
            "parentfield": "attributes",
        },
    )
    for idx, attr in enumerate(required_attrs, 1):
        frappe.get_doc(
            {
                "doctype": "Item Variant Attribute",
                "parent": template_code,
                "parenttype": "Item",
                "parentfield": "attributes",
                "idx": idx,
                "attribute": attr,
            }
        ).insert(ignore_permissions=True)
    frappe.db.set_value("Item", template_code, "has_variants", 1 if required_attrs else 0, update_modified=False)
    frappe.db.set_value(
        "Item",
        template_code,
        "variant_based_on",
        "Item Attribute" if required_attrs else None,
        update_modified=False,
    )


def _item_price(item_code: str) -> float | None:
    return frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": PRICE_LIST, "selling": 1},
        "price_list_rate",
    )


def _upsert_item_price(item_code: str, rate: float | None) -> None:
    if rate is None:
        return
    existing = frappe.db.exists(
        "Item Price",
        {"item_code": item_code, "price_list": PRICE_LIST, "selling": 1},
    )
    if existing:
        frappe.db.set_value("Item Price", existing, "price_list_rate", rate)
        return
    frappe.get_doc(
        {
            "doctype": "Item Price",
            "item_code": item_code,
            "price_list": PRICE_LIST,
            "price_list_rate": rate,
            "currency": "USD",
            "selling": 1,
        }
    ).insert(ignore_permissions=True)


def _ensure_public_file(source_url: str, file_name: str, attached_to_name: str) -> str:
    SITE_FILES_DIR.mkdir(parents=True, exist_ok=True)
    target = SITE_FILES_DIR / file_name
    if not target.exists() or target.stat().st_size == 0:
        request = Request(source_url, headers={"User-Agent": "LT variant media repair"})
        with urlopen(request, timeout=30) as response:
            with target.open("wb") as handle:
                shutil.copyfileobj(response, handle)

    file_url = f"/files/{file_name}"
    existing = frappe.db.exists(
        "File",
        {
            "file_url": file_url,
            "attached_to_doctype": "Item",
            "attached_to_name": attached_to_name,
        },
    )
    if not existing:
        frappe.get_doc(
            {
                "doctype": "File",
                "file_name": file_name,
                "file_url": file_url,
                "is_private": 0,
                "attached_to_doctype": "Item",
                "attached_to_name": attached_to_name,
            }
        ).insert(ignore_permissions=True)
    return file_url


def _explicit_variant_image(template_code: str, combo: dict[str, str], variant_code: str) -> str | None:
    image_ids = BOUQUET_SIZE_IMAGE_IDS.get(template_code)
    if not image_ids:
        return None
    size = combo.get("Bouquet Size") or ""
    for key, image_id in image_ids.items():
        if key.lower() in size.lower():
            source_url = f"http://5.78.136.133/web/image/product.product/{image_id}/image_1024"
            file_name = f"{template_code}-{key.lower()}.webp"
            return _ensure_public_file(source_url, file_name, variant_code)
    return None


def _find_or_create_required_variant(template_code: str, combo: dict[str, str]) -> str:
    from erpnext.controllers.item_variant import create_variant, get_variant

    existing = get_variant(template_code, args=combo)
    if existing:
        frappe.db.set_value("Item", existing, "disabled", 0)
        return existing

    variant = create_variant(template_code, args=combo)
    variant.insert(ignore_permissions=True)
    return variant.name


def _variant_templates_with_optional_axes() -> list[str]:
    rows = frappe.db.sql(
        """
        SELECT DISTINCT child.variant_of
        FROM `tabItem Variant Attribute` child
        WHERE child.attribute IN %(attributes)s
          AND child.variant_of IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM `tabItem Variant Attribute` template_attr
              WHERE template_attr.parent = child.variant_of
                AND template_attr.parenttype = 'Item'
                AND template_attr.parentfield = 'attributes'
                AND template_attr.attribute = 'Bouquet Size'
          )
        ORDER BY child.variant_of
        """,
        {"attributes": tuple(OPTIONAL_ADDON_ATTRIBUTES)},
        as_dict=True,
    )
    return [row.variant_of for row in rows if row.variant_of]


def _repair_template(template_code: str) -> dict[str, object]:
    required_attrs = _template_required_attrs(template_code)
    if not required_attrs:
        return {"template": template_code, "skipped": "no required attributes remain"}

    old_variants = frappe.get_all(
        "Item",
        filters={"variant_of": template_code},
        fields=["name", "image", "disabled"],
        limit_page_length=0,
        order_by="name asc",
    )

    groups: dict[tuple[tuple[str, str], ...], dict[str, object]] = {}
    old_optional_variants: list[str] = []
    for variant in old_variants:
        attrs = _variant_attrs(variant.name)
        has_optional_attr = any(attr in OPTIONAL_ADDON_ATTRIBUTES for attr in attrs)
        if has_optional_attr:
            old_optional_variants.append(variant.name)

        combo = project_required_variant_combo(attrs)
        if not combo:
            continue
        key = tuple(sorted(combo.items()))
        current = groups.get(key)
        if not current or (not current.get("image") and variant.get("image")):
            groups[key] = {
                "combo": combo,
                "image": variant.get("image"),
                "price": _item_price(variant.name),
            }

    _set_template_required_attrs(template_code, required_attrs)

    created_or_reused = []
    for data in groups.values():
        combo = data["combo"]
        variant_code = _find_or_create_required_variant(template_code, combo)
        _upsert_item_price(variant_code, data.get("price"))
        image = _explicit_variant_image(template_code, combo, variant_code) or data.get("image")
        if image:
            frappe.db.set_value("Item", variant_code, "image", image, update_modified=False)
        created_or_reused.append(variant_code)

    for old_code in old_optional_variants:
        if old_code not in created_or_reused:
            frappe.db.set_value("Item", old_code, "disabled", 1, update_modified=False)

    try:
        from webshop.webshop.variant_selector.item_variants_cache import ItemVariantsCacheManager

        ItemVariantsCacheManager(template_code).build_cache()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "LT optional add-on variant cache rebuild failed")

    return {
        "template": template_code,
        "required_attrs": required_attrs,
        "required_variants": len(created_or_reused),
        "disabled_optional_variants": len(old_optional_variants),
        "variants": created_or_reused,
    }


def execute() -> str:
    frappe.flags.ignore_permissions = True
    results = [_repair_template(template) for template in _variant_templates_with_optional_axes()]
    frappe.db.commit()
    return json.dumps(
        {
            "optional_attributes": sorted(OPTIONAL_ADDON_ATTRIBUTES),
            "templates_checked": len(results),
            "results": results,
        },
        indent=2,
    )
