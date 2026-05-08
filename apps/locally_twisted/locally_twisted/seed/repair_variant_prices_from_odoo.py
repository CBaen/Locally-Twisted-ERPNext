"""Repair ERPNext variant Item Prices from Odoo's dynamic combination prices.

Run in-process:
    bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_odoo.execute --kwargs '{"slug_filter":"unicorn-bouquet"}'
    bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_odoo.execute --kwargs '{"dry_run": true}'

This exists because Odoo's product page base price is not enough. Price-affecting
attributes live behind /website_sale/get_combination_info.
"""
from __future__ import annotations

import json
import re
import urllib.request
from decimal import Decimal, ROUND_HALF_UP
from http.cookiejar import CookieJar
from typing import Any

import frappe

from locally_twisted.catalog_variant_rules import (
    is_required_variant_attribute,
    project_required_variant_combo,
)
from locally_twisted.commerce_rules import PRICE_LIST
from locally_twisted.seed.seed_catalog import _find_resources


ODOO_COMBINATION_ROUTE = "http://5.78.136.133/website_sale/get_combination_info"
USER_AGENT = "LT Odoo variant price repair"
CSRF_RE = re.compile(r'csrf_token:\s*"([^"]+)"')


class OdooVariantPriceRepairError(RuntimeError):
    pass


def _money(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _load_inputs() -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    base = _find_resources()
    catalog = json.loads((base / "catalog.json").read_text(encoding="utf-8"))
    normalize_map = json.loads((base / "value_normalize_map.json").read_text(encoding="utf-8"))
    return catalog.get("products") or [], normalize_map


def _normalize_value(attr_name: str, raw_value: str, normalize_map: dict[str, dict[str, str]]) -> str:
    key = " ".join(str(raw_value or "").split()).lower()
    return normalize_map.get(attr_name, {}).get(key, raw_value)


def _opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))


def _fetch_product_page(opener: urllib.request.OpenerDirector, url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def _csrf_token(html: str) -> str:
    match = CSRF_RE.search(html)
    if not match:
        raise OdooVariantPriceRepairError("Odoo product page did not expose csrf_token")
    return match.group(1)


def _post_combination_info(
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
        ODOO_COMBINATION_ROUTE,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "X-CSRFToken": csrf_token,
        },
    )
    with opener.open(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
    data = json.loads(body)
    if data.get("error"):
        raise OdooVariantPriceRepairError(f"Odoo combination price error: {data['error']}")
    result = data.get("result") or {}
    if not result.get("is_combination_possible"):
        raise OdooVariantPriceRepairError(f"Odoo says combination is not possible: {ptav_ids}")
    if result.get("price") is None:
        raise OdooVariantPriceRepairError(f"Odoo returned no price for combination: {ptav_ids}")
    return result


def _ptav_attribute_lookup(prod: dict[str, Any]) -> dict[int, str]:
    lookup: dict[int, str] = {}
    for attr_name, attr_data in (prod.get("attributes") or {}).items():
        for value in attr_data.get("values") or []:
            lookup[int(value["ptav_id"])] = attr_name
    return lookup


def _required_ptav_ids(row: dict[str, Any], prod: dict[str, Any]) -> list[int]:
    lookup = _ptav_attribute_lookup(prod)
    full_ptav_ids = [int(value) for value in row.get("ptav_ids") or []]
    combo = row.get("combo") or {}
    projected_combo = project_required_variant_combo(combo)
    if len(projected_combo) == len(combo):
        return full_ptav_ids

    required_names = set(projected_combo)
    required_ids = [
        ptav_id
        for ptav_id in full_ptav_ids
        if lookup.get(ptav_id) in required_names and is_required_variant_attribute(lookup.get(ptav_id))
    ]
    if not required_ids:
        raise OdooVariantPriceRepairError(
            f"Could not project required ptav ids for {prod.get('slug')} row {row.get('combo')}"
        )
    return required_ids


def _find_erpnext_variant(
    template_code: str,
    combo: dict[str, str],
    normalize_map: dict[str, dict[str, str]],
) -> str | None:
    from erpnext.controllers.item_variant import get_variant

    args = {
        attr_name: _normalize_value(attr_name, raw, normalize_map)
        for attr_name, raw in project_required_variant_combo(combo).items()
    }
    return get_variant(template_code, args=args)


def _upsert_item_price(item_code: str, rate: Decimal, *, dry_run: bool) -> Decimal | None:
    existing = frappe.db.exists(
        "Item Price",
        {"item_code": item_code, "price_list": PRICE_LIST, "selling": 1},
    )
    if existing:
        old_rate = frappe.db.get_value("Item Price", existing, "price_list_rate")
        if not dry_run:
            frappe.db.set_value("Item Price", existing, "price_list_rate", float(rate))
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


def _repair_product(
    prod: dict[str, Any],
    normalize_map: dict[str, dict[str, str]],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    slug = prod.get("slug")
    odoo_id = prod.get("odoo_id")
    url = prod.get("url")
    if not slug or not odoo_id or not url:
        raise OdooVariantPriceRepairError(f"Product is missing slug, odoo_id, or url: {prod}")

    rows = prod.get("valid_variants") or []
    if not rows:
        return {"template": slug, "skipped": "no variants"}

    opener = _opener()
    csrf = _csrf_token(_fetch_product_page(opener, url))

    # Keep one Odoo call per current ERPNext variant, not per dropped add-on row.
    projected_rows: dict[tuple[tuple[str, str], ...], dict[str, Any]] = {}
    for row in rows:
        combo = project_required_variant_combo(row.get("combo") or {})
        if not combo:
            continue
        projected_rows.setdefault(tuple(sorted(combo.items())), row)

    repaired = []
    for row in projected_rows.values():
        variant_code = _find_erpnext_variant(slug, row.get("combo") or {}, normalize_map)
        if not variant_code:
            raise OdooVariantPriceRepairError(f"ERPNext variant not found for {slug}: {row.get('combo')}")
        ptav_ids = _required_ptav_ids(row, prod)
        info = _post_combination_info(
            opener,
            csrf_token=csrf,
            product_template_id=int(odoo_id),
            ptav_ids=ptav_ids,
        )
        new_rate = _money(info["price"])
        old_rate = _upsert_item_price(variant_code, new_rate, dry_run=dry_run)
        repaired.append(
            {
                "item_code": variant_code,
                "old_rate": str(old_rate) if old_rate is not None else None,
                "new_rate": str(new_rate),
                "would_change": old_rate != new_rate,
                "odoo_product_id": info.get("product_id"),
                "ptav_ids": ptav_ids,
            }
        )

    if not dry_run:
        _rebuild_variant_cache(slug)
    return {"template": slug, "dry_run": dry_run, "variants_checked": len(repaired), "variants": repaired}


def execute(
    slug_filter: str | None = None,
    max_products: int | None = None,
    dry_run: bool = False,
) -> str:
    frappe.flags.ignore_permissions = True
    products, normalize_map = _load_inputs()
    if slug_filter:
        products = [prod for prod in products if prod.get("slug") == slug_filter]
    products = [prod for prod in products if prod.get("valid_variants")]
    if max_products is not None:
        products = products[: int(max_products)]
    if slug_filter and not products:
        raise OdooVariantPriceRepairError(f"No variant product found for slug_filter={slug_filter!r}")

    results = [_repair_product(prod, normalize_map, dry_run=bool(dry_run)) for prod in products]
    if not dry_run:
        frappe.db.commit()
    changed = sum(1 for result in results for row in result["variants"] if row.get("would_change"))
    return json.dumps(
        {
            "dry_run": bool(dry_run),
            "products_checked": len(results),
            "variants_that_would_change": changed,
            "results": results,
        },
        indent=2,
    )
