"""Repair ERPNext variant Item Prices from catalog source option price modifiers.

The older repair path calls catalog source for full projected combinations. That works
for small families such as bouquets, but it stops on large color/customizer
families when catalog source rejects partial source rows. catalog source variant prices are built
from per-option price extras, so this repair resolves each non-color option's
price modifier once and applies the summed modifiers to every active ERPNext
variant.
"""

from __future__ import annotations

import json
import time
import urllib.request
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import frappe

from locally_twisted.catalog_contract.color_rules import is_balloon_color_axis
from locally_twisted.catalog_variant_rules import normalize_variant_value
from locally_twisted.commerce_rules import PRICE_LIST
from locally_twisted.seed.repair_variant_prices_from_catalog_source import (
    CSRF_RE,
    CATALOG_COMBINATION_ROUTE,
    USER_AGENT,
    _fetch_product_page,
    _find_resources,
    _opener,
)


class CatalogSourceVariantModifierRepairError(RuntimeError):
    pass


PRICE_AXIS_KEYWORDS = (
    "size",
    "height",
    "length",
    "topper",
    "add on",
    "add-on",
    "add bouquet",
    "led",
    "design",
)

NON_PRICE_AXIS_KEYWORDS = (
    "color",
    "palette",
    "theme",
)
REQUEST_ATTEMPTS = 3


def _money(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _load_inputs() -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    base = _find_resources()
    catalog = json.loads((base / "catalog.json").read_text(encoding="utf-8"))
    normalize_map = json.loads((base / "value_normalize_map.json").read_text(encoding="utf-8"))
    return catalog.get("products") or [], normalize_map


def _normalize_value(attr_name: str, raw_value: str, normalize_map: dict[str, dict[str, str]]) -> str:
    key = " ".join(str(raw_value or "").split()).lower()
    value = normalize_map.get(attr_name, {}).get(key, raw_value)
    return str(normalize_variant_value(attr_name, value) or "").strip()


def _is_price_modifier_axis(attribute: str) -> bool:
    lowered = attribute.lower()
    if is_balloon_color_axis(attribute):
        return False
    if any(keyword in lowered for keyword in NON_PRICE_AXIS_KEYWORDS):
        return False
    return any(keyword in lowered for keyword in PRICE_AXIS_KEYWORDS)


def _csrf_token(html: str) -> str:
    match = CSRF_RE.search(html)
    if not match:
        raise CatalogSourceVariantModifierRepairError("catalog source product page did not expose csrf_token")
    return match.group(1)


def _fetch_product_page_with_retry(opener: urllib.request.OpenerDirector, url: str) -> str:
    last_error: Exception | None = None
    for attempt in range(1, REQUEST_ATTEMPTS + 1):
        try:
            return _fetch_product_page(opener, url)
        except Exception as exc:
            last_error = exc
            if attempt < REQUEST_ATTEMPTS:
                time.sleep(attempt)
    raise CatalogSourceVariantModifierRepairError(f"catalog source product page request failed after retries: {last_error}")


def _post_price(
    opener: urllib.request.OpenerDirector,
    *,
    csrf_token: str,
    product_template_id: int,
    ptav_ids: list[int],
) -> dict[str, Any]:
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "product_template_id": product_template_id,
                "product_id": 0,
                "combination": ptav_ids,
                "add_qty": 1,
                "parent_combination": [],
            },
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        CATALOG_COMBINATION_ROUTE,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "X-CSRFToken": csrf_token,
        },
    )
    last_error: Exception | None = None
    for attempt in range(1, REQUEST_ATTEMPTS + 1):
        try:
            with opener.open(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8", errors="replace"))
            break
        except Exception as exc:
            last_error = exc
            if attempt < REQUEST_ATTEMPTS:
                time.sleep(attempt)
    else:
        raise CatalogSourceVariantModifierRepairError(f"catalog source option price request failed after retries: {last_error}")

    if data.get("error"):
        raise CatalogSourceVariantModifierRepairError(f"catalog source combination price error: {data['error']}")
    result = data.get("result") or {}
    if result.get("price") is None:
        raise CatalogSourceVariantModifierRepairError(f"catalog source returned no price for option ids: {ptav_ids}")
    return result


def _variant_rows(template_code: str) -> list[dict[str, Any]]:
    rows = frappe.db.sql(
        """
        SELECT
            item.name AS item_code,
            attr.attribute,
            attr.attribute_value,
            price.name AS price_doc,
            price.price_list_rate
        FROM `tabItem` item
        JOIN `tabItem Variant Attribute` attr
            ON attr.parent = item.name
        LEFT JOIN `tabItem Price` price
            ON price.item_code = item.name
           AND price.price_list = %s
           AND price.selling = 1
        WHERE item.variant_of = %s
          AND item.disabled = 0
        ORDER BY item.name, attr.idx
        """,
        (PRICE_LIST, template_code),
        as_dict=True,
    )
    by_item: dict[str, dict[str, Any]] = {}
    for row in rows:
        item = by_item.setdefault(
            row["item_code"],
            {
                "item_code": row["item_code"],
                "price_doc": row.get("price_doc"),
                "price_list_rate": row.get("price_list_rate"),
                "attributes": {},
            },
        )
        item["attributes"][str(row.get("attribute") or "")] = str(row.get("attribute_value") or "")
    return list(by_item.values())


def _upsert_item_price(item_code: str, price_doc: str | None, rate: Decimal, *, dry_run: bool) -> Decimal | None:
    if price_doc:
        old_rate = frappe.db.get_value("Item Price", price_doc, "price_list_rate")
        if not dry_run:
            frappe.db.set_value("Item Price", price_doc, "price_list_rate", float(rate))
        return _money(old_rate)

    if dry_run:
        return None

    frappe.get_doc(
        {
            "doctype": "Item Price",
            "item_code": item_code,
            "price_list": PRICE_LIST,
            "price_list_rate": float(rate),
            "currency": "USD",
            "selling": 1,
        }
    ).insert(ignore_permissions=True)
    return None


def _rebuild_variant_cache(template_code: str) -> None:
    try:
        from webshop.webshop.variant_selector.item_variants_cache import ItemVariantsCacheManager

        ItemVariantsCacheManager(template_code).build_cache()
        return
    except ImportError:
        pass

    from webshop.webshop.variant_selector.utils import ItemVariantsCacheManager

    ItemVariantsCacheManager(template_code).rebuild_cache()


def _option_modifiers(
    prod: dict[str, Any],
    normalize_map: dict[str, dict[str, str]],
) -> tuple[dict[tuple[str, str], Decimal], list[dict[str, Any]]]:
    slug = prod.get("slug")
    catalog_data_id = prod.get("catalog_data_id")
    url = prod.get("url")
    if not slug or not catalog_data_id or not url:
        raise CatalogSourceVariantModifierRepairError(f"Product is missing slug, catalog_data_id, or url: {prod}")

    base_price = _money(prod.get("base_price") or 0)
    opener = _opener()
    csrf = _csrf_token(_fetch_product_page_with_retry(opener, url))
    modifiers: dict[tuple[str, str], Decimal] = {}
    value_prices: list[dict[str, Any]] = []

    for attr_name, attr_data in (prod.get("attributes") or {}).items():
        attr_name = str(attr_name or "").strip()
        if not attr_name or not _is_price_modifier_axis(attr_name):
            continue
        for option in attr_data.get("values") or []:
            raw_value = str(option.get("name") or "").strip()
            ptav_id = int(option["ptav_id"])
            info = _post_price(
                opener,
                csrf_token=csrf,
                product_template_id=int(catalog_data_id),
                ptav_ids=[ptav_id],
            )
            option_price = _money(info["price"])
            delta = option_price - base_price
            normalized_value = _normalize_value(attr_name, raw_value, normalize_map)
            modifiers[(attr_name, normalized_value)] = delta
            if delta:
                value_prices.append(
                    {
                        "attribute": attr_name,
                        "value": normalized_value,
                        "catalog_source_option_price": str(option_price),
                        "delta": str(delta),
                        "is_combination_possible": bool(info.get("is_combination_possible")),
                        "catalog_source_product_id": info.get("product_id"),
                    }
                )

    return modifiers, value_prices


def _repair_product(
    prod: dict[str, Any],
    normalize_map: dict[str, dict[str, str]],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    template_code = str(prod.get("slug") or "").strip()
    base_price = _money(prod.get("base_price") or 0)
    variants = _variant_rows(template_code)
    if not variants:
        return {"template": template_code, "skipped": "no active variants"}

    modifiers, value_prices = _option_modifiers(prod, normalize_map)
    if not modifiers:
        return {
            "template": template_code,
            "base_price": str(base_price),
            "variants_checked": len(variants),
            "variants_that_would_change": 0,
            "skipped": "no price modifier axes",
        }

    changed = 0
    missing_price_docs = 0
    samples: list[dict[str, Any]] = []
    for variant in variants:
        new_rate = base_price
        for attr_name, attr_value in variant["attributes"].items():
            new_rate += modifiers.get((attr_name, attr_value), Decimal("0.00"))
        old_rate = _upsert_item_price(
            variant["item_code"],
            variant.get("price_doc"),
            new_rate,
            dry_run=dry_run,
        )
        if old_rate is None:
            missing_price_docs += 1
            would_change = True
        else:
            would_change = old_rate != new_rate
        if would_change:
            changed += 1
            if len(samples) < 20:
                samples.append(
                    {
                        "item_code": variant["item_code"],
                        "old_rate": str(old_rate) if old_rate is not None else None,
                        "new_rate": str(new_rate),
                        "attributes": variant["attributes"],
                    }
                )

    if changed and not dry_run:
        _rebuild_variant_cache(template_code)

    return {
        "template": template_code,
        "base_price": str(base_price),
        "variants_checked": len(variants),
        "variants_that_would_change": changed,
        "missing_price_docs": missing_price_docs,
        "price_modifier_values": value_prices,
        "change_samples": samples,
    }


def execute(
    slug_filter: str | None = None,
    max_products: int | None = None,
    dry_run: bool = False,
    strict: bool = True,
) -> str:
    frappe.flags.ignore_permissions = True
    products, normalize_map = _load_inputs()
    products = [prod for prod in products if prod.get("valid_variants")]
    if slug_filter:
        products = [prod for prod in products if prod.get("slug") == slug_filter]
    if max_products is not None:
        products = products[: int(max_products)]
    if slug_filter and not products:
        raise CatalogSourceVariantModifierRepairError(f"No variant product found for slug_filter={slug_filter!r}")

    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for prod in products:
        try:
            results.append(_repair_product(prod, normalize_map, dry_run=bool(dry_run)))
        except Exception as exc:
            error = {"template": prod.get("slug"), "error": str(exc)}
            errors.append(error)
            if strict:
                raise

    if not dry_run:
        frappe.db.commit()

    changed = sum(int(result.get("variants_that_would_change") or 0) for result in results)
    checked = sum(int(result.get("variants_checked") or 0) for result in results)
    return json.dumps(
        {
            "dry_run": bool(dry_run),
            "strict": bool(strict),
            "products_checked": len(results),
            "products_with_errors": len(errors),
            "variants_checked": checked,
            "variants_that_would_change": changed,
            "errors": errors,
            "results": results,
        },
        indent=2,
        sort_keys=True,
    )
