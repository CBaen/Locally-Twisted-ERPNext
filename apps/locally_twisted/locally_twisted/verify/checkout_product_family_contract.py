"""Verify Phase 3 ready-to-order checkout product-family preservation.

This is a rollback-only backend proof. It does not open public ecommerce, does
not touch Odoo, does not create live payment sessions, and does not send
customer messages. It proves the first direct-checkout product family at the
ERPNext/Frappe receiving layer: selected bouquet size + confirmed foil-number
add-on survive cart/checkout resolution, submitted Sales Order rows, and copied
Sales Invoice rows.
"""
from __future__ import annotations

import json
import time
from typing import Any

import frappe
from frappe.utils import add_days, flt, nowdate

from locally_twisted.product_page_runtime import (
    ADD_ON_ITEM_CONTRACTS,
    CONFIG_VERSION,
    LINE_FIELDNAMES,
    sales_order_line_configuration_fields,
)


PRICE_LIST = "Standard Selling"
FOIL_NUMBER_ADD_ON_KEY = "foil_number"
FOIL_NUMBER_ADD_ON_ITEM = "ADDON-FOIL-NUMBER"
FOIL_NUMBER_ADD_ON_RATE = 12.0

EXPECTED_FOIL_BOUQUET_WEBSITE_ITEMS = (
    "unicorn-bouquet",
    "mickey-mouse-bouquet",
    "minion-bouquet",
    "encanto-bouquet",
    "stitch-bouquet",
    "flamingo-bouquet",
    "football-bouquet",
    "soccer-bouquet",
    "space-bouquet",
    "over-the-hill-bouquet",
    "paw-patrol-bouquet",
    "elsa-bouquet",
    "holy-cow-bouquet",
)
MOTHERS_DAY_WEBSITE_ITEM = "mothers-day-bouquet"
EASTER_BALLOON_CUPS_WEBSITE_ITEM = "easter-balloon-cups"


class ContractFail(Exception):
    pass


def run() -> dict[str, Any]:
    token = str(int(time.time() * 1000))
    original_commit = frappe.db.commit
    intercepted_commits: list[bool] = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    try:
        frappe.db.commit = no_commit
        result = _run_contract(token)
        result["commit_calls_intercepted"] = len(intercepted_commits)
        frappe.db.rollback()
        result["rolled_back"] = True
        result["survivor_counts"] = _survivor_counts(token)
        survivors = {key: value for key, value in result["survivor_counts"].items() if value}
        if survivors:
            raise ContractFail(f"generated verifier records survived rollback: {survivors}")
        return {"ok": True, **result}
    except ContractFail as exc:
        frappe.db.rollback()
        return {"ok": False, "failures": [str(exc)], "survivor_counts": _survivor_counts(token)}
    except Exception:
        frappe.db.rollback()
        return {"ok": False, "failures": [frappe.get_traceback()], "survivor_counts": _survivor_counts(token)}
    finally:
        frappe.db.commit = original_commit
        frappe.db.rollback()


def _run_contract(token: str) -> dict[str, Any]:
    _assert_line_schema()
    _assert_foil_number_add_on_scope()
    _assert_unknown_client_selected_options_fail_loudly()

    sales_order_lines: list[dict[str, Any]] = []
    expected_base_line_count = 0
    expected_add_on_line_count = 0
    bouquet_results: list[dict[str, Any]] = []
    for website_item_code in EXPECTED_FOIL_BOUQUET_WEBSITE_ITEMS:
        bouquet_result, lines = _assert_bouquet_family_line(website_item_code)
        bouquet_results.append(bouquet_result)
        sales_order_lines.extend(lines)
        expected_base_line_count += int(bouquet_result["enabled_variant_count"])
        expected_add_on_line_count += int(bouquet_result["add_on_line_count"])

    mothers_day_result, mothers_day_lines = _assert_mothers_day_simple_line()
    sales_order_lines.extend(mothers_day_lines)
    expected_base_line_count += int(mothers_day_result["sale_sku_count"])

    easter_result, easter_lines = _assert_easter_balloon_cups_simple_line()
    sales_order_lines.extend(easter_lines)
    expected_base_line_count += int(easter_result["enabled_variant_count"])

    sales_order = _assert_sales_order_accepts_family_lines(
        token,
        sales_order_lines,
        expected_base_line_count=expected_base_line_count,
        expected_add_on_line_count=expected_add_on_line_count,
    )
    sales_invoice_name = _assert_invoice_preserves_family_lines(
        sales_order.name,
        expected_line_count=len(sales_order_lines),
        expected_base_line_count=expected_base_line_count,
        expected_add_on_line_count=expected_add_on_line_count,
    )

    return {
        "bouquet_family_count": len(bouquet_results),
        "bouquet_family": bouquet_results,
        "mothers_day": mothers_day_result,
        "easter_balloon_cups": easter_result,
        "sales_order": sales_order.name,
        "sales_invoice": sales_invoice_name,
        "sales_order_line_count": len(sales_order.items),
        "expected_sales_order_line_count": len(sales_order_lines),
        "enabled_sale_sku_count": expected_base_line_count,
        "add_on_line_count": expected_add_on_line_count,
        "line_fields": sorted(LINE_FIELDNAMES.values()),
        "schema_version": CONFIG_VERSION,
    }


def _assert_line_schema() -> None:
    for doctype in ("Sales Order Item", "Sales Invoice Item"):
        meta = frappe.get_meta(doctype)
        missing = sorted(field for field in LINE_FIELDNAMES.values() if not meta.has_field(field))
        if missing:
            raise ContractFail(f"{doctype} missing LT product-family checkout fields: {missing}")


def _assert_foil_number_add_on_scope() -> None:
    spec = ADD_ON_ITEM_CONTRACTS.get(FOIL_NUMBER_ADD_ON_KEY)
    if not spec:
        raise ContractFail("runtime lost confirmed foil_number add-on contract")
    eligible = tuple(spec.get("eligible_website_item_codes") or ())
    if eligible != EXPECTED_FOIL_BOUQUET_WEBSITE_ITEMS:
        raise ContractFail(
            "foil_number eligible product-family scope drifted; "
            f"expected {EXPECTED_FOIL_BOUQUET_WEBSITE_ITEMS}, found {eligible}"
        )
    if MOTHERS_DAY_WEBSITE_ITEM in eligible or "birthday-deliveries" in eligible:
        raise ContractFail("foil_number add-on leaked onto non-approved ready-to-order/review products")

    _assert_item_price(FOIL_NUMBER_ADD_ON_ITEM, FOIL_NUMBER_ADD_ON_RATE)


def _assert_bouquet_family_line(website_item_code: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from locally_twisted.product_options import get_checkout_add_on_options
    from locally_twisted.www.checkout import _resolve_sale_lines

    website_item = _assert_website_item_contract(website_item_code, page_type="simple_product", commerce_lane="checkout")
    variant_item_codes = _enabled_variants_for_template(website_item_code, required_attribute="Bouquet Size")

    add_on_options = get_checkout_add_on_options(website_item_code)
    foil_option = _only_foil_option(website_item_code, add_on_options)

    sale_lines: list[dict[str, Any]] = []
    verified_variants: list[dict[str, Any]] = []
    for variant_item_code in variant_item_codes:
        resolved = _resolve_cart_item(variant_item_code, website_item_code)
        selected_options = _variant_options_dict(resolved.get("variant_options") or [])
        if not selected_options.get("Bouquet Size"):
            raise ContractFail(f"{variant_item_code} did not preserve Bouquet Size selected option")
        configuration = _configuration_payload(
            item_code=variant_item_code,
            website_item_code=website_item_code,
            variant_options=resolved.get("variant_options") or [],
            add_ons=[
                {
                    "key": FOIL_NUMBER_ADD_ON_KEY,
                    "label": "Foil number",
                    "value": "7",
                    "quantity": 1,
                }
            ],
        )

        lines, resolved_items = _resolve_sale_lines(
            [{"item_code": variant_item_code, "qty": 1, "configuration": configuration}]
        )
        if len(lines) != 2:
            raise ContractFail(f"{variant_item_code} should create base + foil add-on lines, found {len(lines)}")
        if len(resolved_items) != 2:
            raise ContractFail(f"{variant_item_code} resolved display lines should include add-on, found {len(resolved_items)}")

        base_line, add_on_line = lines
        _assert_base_line_payload(
            label=variant_item_code,
            line=base_line,
            expected_item_code=variant_item_code,
            expected_website_item_code=website_item_code,
            expect_add_on=True,
            expected_selected_options=selected_options,
        )
        _assert_foil_add_on_line_payload(
            label=variant_item_code,
            line=add_on_line,
            expected_parent_item_code=variant_item_code,
            expected_website_item_code=website_item_code,
        )
        sale_lines.extend(lines)
        verified_variants.append(
            {
                "variant_item_code": variant_item_code,
                "selected_options": selected_options,
                "resolved_line_count": len(lines),
            }
        )

    return (
        {
            "website_item_code": website_item_code,
            "web_item_name": website_item.get("web_item_name"),
            "stored_contract": "simple_product|checkout",
            "foil_option_rate": flt(foil_option.get("unit_price")),
            "enabled_variant_count": len(variant_item_codes),
            "add_on_line_count": len(variant_item_codes),
            "resolved_line_count": len(sale_lines),
            "verified_variants": verified_variants,
        },
        sale_lines,
    )

def _assert_unknown_client_selected_options_fail_loudly() -> None:
    stale_configuration = _configuration_payload(
        item_code="unicorn-bouquet-SMA",
        website_item_code="unicorn-bouquet",
        variant_options=[
            {
                "attribute": "Bouquet Size",
                "attribute_value": "Small — 1 featured foil balloon, 2 coordinating foil balloons, 7 latex balloons",
            }
        ],
    )
    stale_configuration["selected_options"]["Retired Color Choice"] = "Blue"
    try:
        sales_order_line_configuration_fields(
            resolved_item={
                "item_code": "unicorn-bouquet-SMA",
                "website_item_code": "unicorn-bouquet",
                "variant_options": [
                    {
                        "attribute": "Bouquet Size",
                        "attribute_value": "Small — 1 featured foil balloon, 2 coordinating foil balloons, 7 latex balloons",
                    }
                ],
            },
            client_configuration=stale_configuration,
        )
    except frappe.ValidationError as exc:
        if "saved options no longer match" not in str(exc):
            raise ContractFail(f"unknown stale selected option failed with the wrong message: {exc}") from exc
        return
    raise ContractFail("unknown stale selected option should fail loudly instead of being silently dropped")


def _assert_mothers_day_simple_line() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    return _assert_single_sku_simple_line(
        website_item_code=MOTHERS_DAY_WEBSITE_ITEM,
        label="Mother's Day Bouquet",
        no_add_on_failure="Mother's Day Bouquet should not expose checkout add-ons",
    )


def _assert_easter_balloon_cups_simple_line() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    variant_item_codes = _enabled_variants_for_template(
        EASTER_BALLOON_CUPS_WEBSITE_ITEM,
        required_attribute="Easter Designs",
    )
    sale_lines: list[dict[str, Any]] = []
    verified_variants: list[dict[str, Any]] = []
    web_item_name = "Easter Balloon Cups"
    for variant_item_code in variant_item_codes:
        result, lines = _assert_variant_simple_line(
            website_item_code=EASTER_BALLOON_CUPS_WEBSITE_ITEM,
            variant_item_code=variant_item_code,
            label="Easter Balloon Cups",
            no_add_on_failure="Easter Balloon Cups should not expose checkout add-ons",
        )
        web_item_name = result.get("web_item_name") or web_item_name
        sale_lines.extend(lines)
        verified_variants.append(
            {
                "variant_item_code": variant_item_code,
                "selected_options": result.get("selected_options"),
                "resolved_line_count": result.get("resolved_line_count"),
            }
        )

    return (
        {
            "website_item_code": EASTER_BALLOON_CUPS_WEBSITE_ITEM,
            "web_item_name": web_item_name,
            "stored_contract": "simple_product|checkout",
            "enabled_variant_count": len(variant_item_codes),
            "add_on_options": 0,
            "resolved_line_count": len(sale_lines),
            "verified_variants": verified_variants,
            "seasonal_status": "architecture_verified_not_launch_approval",
            "note": (
                "Seasonal orderability/visibility is still a separate GL/business approval; "
                "this verifies the ERPNext receiving architecture only."
            ),
        },
        sale_lines,
    )

def _assert_variant_simple_line(
    *,
    website_item_code: str,
    variant_item_code: str,
    label: str,
    no_add_on_failure: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from locally_twisted.product_options import get_checkout_add_on_options
    from locally_twisted.www.checkout import _resolve_sale_lines

    website_item = _assert_website_item_contract(
        website_item_code,
        page_type="simple_product",
        commerce_lane="checkout",
    )
    if get_checkout_add_on_options(website_item_code):
        raise ContractFail(no_add_on_failure)

    item = frappe.db.get_value(
        "Item",
        {"item_code": variant_item_code, "variant_of": website_item_code},
        ["item_code", "disabled"],
        as_dict=True,
    )
    if not item or int(item.get("disabled") or 0):
        raise ContractFail(f"{label} variant {variant_item_code} is missing or disabled")

    resolved = _resolve_cart_item(variant_item_code, website_item_code)
    selected_options = _variant_options_dict(resolved.get("variant_options") or [])
    if not selected_options:
        raise ContractFail(f"{label} variant path did not resolve selected options: {resolved}")
    configuration = _configuration_payload(
        item_code=variant_item_code,
        website_item_code=website_item_code,
        variant_options=resolved.get("variant_options") or [],
    )

    lines, resolved_items = _resolve_sale_lines(
        [{"item_code": variant_item_code, "qty": 1, "configuration": configuration}]
    )
    if len(lines) != 1 or len(resolved_items) != 1:
        raise ContractFail(f"{label} variant path should create one line, found {len(lines)}")
    _assert_base_line_payload(
        label=website_item_code,
        line=lines[0],
        expected_item_code=variant_item_code,
        expected_website_item_code=website_item_code,
        expect_add_on=False,
        expected_selected_options=selected_options,
    )

    return (
        {
            "website_item_code": website_item_code,
            "web_item_name": website_item.get("web_item_name"),
            "variant_item_code": variant_item_code,
            "stored_contract": "simple_product|checkout",
            "selected_options": selected_options,
            "add_on_options": 0,
            "resolved_line_count": len(lines),
        },
        lines,
    )


def _assert_single_sku_simple_line(
    *,
    website_item_code: str,
    label: str,
    no_add_on_failure: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from locally_twisted.product_options import get_checkout_add_on_options
    from locally_twisted.www.checkout import _resolve_sale_lines

    website_item = _assert_website_item_contract(
        website_item_code,
        page_type="simple_product",
        commerce_lane="checkout",
    )
    if get_checkout_add_on_options(website_item_code):
        raise ContractFail(no_add_on_failure)

    item_code = _sellable_item_for_template(website_item_code)
    resolved = _resolve_cart_item(item_code, website_item_code)
    if resolved.get("variant_options"):
        raise ContractFail(f"{label} simple path unexpectedly resolved variant options: {resolved}")

    lines, resolved_items = _resolve_sale_lines([{"item_code": item_code, "qty": 1, "configuration": None}])
    if len(lines) != 1 or len(resolved_items) != 1:
        raise ContractFail(f"{label} simple path should create one line, found {len(lines)}")
    _assert_base_line_payload(
        label=website_item_code,
        line=lines[0],
        expected_item_code=item_code,
        expected_website_item_code=website_item_code,
        expect_add_on=False,
        expected_selected_options={},
    )

    return (
        {
            "website_item_code": website_item_code,
            "web_item_name": website_item.get("web_item_name"),
            "item_code": item_code,
            "stored_contract": "simple_product|checkout",
            "sale_sku_count": 1,
            "add_on_options": 0,
            "resolved_line_count": len(lines),
        },
        lines,
    )


def _assert_website_item_contract(website_item_code: str, *, page_type: str, commerce_lane: str) -> dict[str, Any]:
    row = frappe.db.get_value(
        "Website Item",
        {"item_code": website_item_code},
        ["name", "item_code", "web_item_name", "item_group", "published", "lt_product_page_type", "lt_commerce_lane"],
        as_dict=True,
    )
    if not row:
        raise ContractFail(f"missing Website Item for {website_item_code}")
    if not int(row.get("published") or 0):
        raise ContractFail(f"{website_item_code} Website Item is not published for server-side checkout resolution")
    actual = (row.get("lt_product_page_type"), row.get("lt_commerce_lane"))
    if actual != (page_type, commerce_lane):
        raise ContractFail(f"{website_item_code} stored contract should be {page_type}|{commerce_lane}, found {actual}")
    return row


def _enabled_variants_for_template(website_item_code: str, *, required_attribute: str) -> list[str]:
    rows = frappe.db.sql(
        """
        SELECT item.item_code
        FROM `tabItem` item
        INNER JOIN `tabItem Variant Attribute` attr
            ON attr.parent = item.name
        WHERE item.variant_of = %s
            AND item.disabled = 0
            AND attr.attribute = %s
            AND attr.attribute_value IS NOT NULL
            AND attr.attribute_value != ''
        ORDER BY item.item_code
        """,
        (website_item_code, required_attribute),
        as_dict=True,
    )
    item_codes = [row["item_code"] for row in rows]
    if not item_codes:
        raise ContractFail(f"{website_item_code} has no enabled variants for {required_attribute}")
    return item_codes


def _sellable_item_for_template(website_item_code: str) -> str:
    item = frappe.db.get_value(
        "Item",
        {"item_code": website_item_code},
        ["item_code", "disabled", "has_variants"],
        as_dict=True,
    )
    if not item:
        raise ContractFail(f"missing Item for {website_item_code}")
    if int(item.get("disabled") or 0):
        raise ContractFail(f"{website_item_code} Item is disabled")
    if int(item.get("has_variants") or 0):
        raise ContractFail(f"{website_item_code} was expected to be a simple single-SKU item, but has variants")
    return item["item_code"]


def _resolve_cart_item(item_code: str, expected_website_item_code: str) -> dict[str, Any]:
    from locally_twisted.api.cart import resolve_cart_item_for_sale

    resolved = resolve_cart_item_for_sale(item_code, raise_on_missing=True)
    if resolved.get("website_item_code") != expected_website_item_code:
        raise ContractFail(
            f"{item_code} resolved to Website Item {resolved.get('website_item_code')}, "
            f"expected {expected_website_item_code}"
        )
    if resolved.get("product_commerce_lane") != "checkout":
        raise ContractFail(f"{item_code} did not resolve into checkout lane: {resolved}")
    return resolved


def _only_foil_option(website_item_code: str, options: list[dict[str, Any]]) -> dict[str, Any]:
    if len(options) != 1:
        raise ContractFail(f"{website_item_code} should expose exactly one checkout add-on, found {options}")
    option = options[0]
    if option.get("key") != FOIL_NUMBER_ADD_ON_KEY:
        raise ContractFail(f"{website_item_code} exposed wrong add-on option: {option}")
    if option.get("item_code") != FOIL_NUMBER_ADD_ON_ITEM:
        raise ContractFail(f"{website_item_code} foil option used wrong Item: {option}")
    if flt(option.get("unit_price")) != FOIL_NUMBER_ADD_ON_RATE:
        raise ContractFail(f"{website_item_code} foil option should be ${FOIL_NUMBER_ADD_ON_RATE}, found {option}")
    return option


def _assert_item_price(item_code: str, expected_rate: float) -> None:
    rate = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": PRICE_LIST, "selling": 1},
        "price_list_rate",
    )
    if rate in (None, ""):
        raise ContractFail(f"{item_code} has no selling Item Price in {PRICE_LIST}")
    if flt(rate) != flt(expected_rate):
        raise ContractFail(f"{item_code} should be priced at {expected_rate}, found {rate}")


def _configuration_payload(
    *,
    item_code: str,
    website_item_code: str,
    variant_options: list[dict[str, Any]],
    add_ons: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": CONFIG_VERSION,
        "item_code": item_code,
        "website_item_code": website_item_code,
        "selected_options": _variant_options_dict(variant_options),
        "add_ons": add_ons or [],
        "customizations": [],
    }


def _variant_options_dict(rows: list[dict[str, Any]]) -> dict[str, str]:
    return {
        str(row.get("attribute")): str(row.get("attribute_value"))
        for row in rows
        if row.get("attribute") and row.get("attribute_value")
    }


def _assert_base_line_payload(
    *,
    label: str,
    line: dict[str, Any],
    expected_item_code: str,
    expected_website_item_code: str,
    expect_add_on: bool,
    expected_selected_options: dict[str, str],
) -> None:
    if line.get("item_code") != expected_item_code:
        raise ContractFail(f"{label} base line used wrong Item: {line.get('item_code')}")
    _assert_line_fields(label, line)
    payload = _payload(label, line)
    expected_pairs = {
        "schema_version": CONFIG_VERSION,
        "item_code": expected_item_code,
        "website_item_code": expected_website_item_code,
        "product_page_type": "simple_product",
        "commerce_lane": "checkout",
        "source": "lt_product_page_runtime",
    }
    for key, expected in expected_pairs.items():
        if payload.get(key) != expected:
            raise ContractFail(f"{label} base line payload {key} should be {expected!r}, found {payload.get(key)!r}")
    if payload.get("selected_options") != expected_selected_options:
        raise ContractFail(
            f"{label} base line dropped selected options; expected {expected_selected_options}, "
            f"found {payload.get('selected_options')}"
        )
    add_ons = payload.get("add_ons") or []
    if expect_add_on:
        if len(add_ons) != 1 or add_ons[0].get("key") != FOIL_NUMBER_ADD_ON_KEY:
            raise ContractFail(f"{label} base line did not preserve foil add-on selection: {payload}")
        if "unit_price" in add_ons[0] or "rate" in add_ons[0]:
            raise ContractFail(f"{label} base line add-on payload carried client price data: {payload}")
    elif add_ons:
        raise ContractFail(f"{label} simple line should not preserve add-ons: {payload}")


def _assert_foil_add_on_line_payload(
    *,
    label: str,
    line: dict[str, Any],
    expected_parent_item_code: str,
    expected_website_item_code: str,
) -> None:
    if line.get("item_code") != FOIL_NUMBER_ADD_ON_ITEM:
        raise ContractFail(f"{label} add-on line used wrong Item: {line.get('item_code')}")
    if int(line.get("qty") or 0) != 1:
        raise ContractFail(f"{label} add-on line should have qty 1 for one selected digit, found {line.get('qty')}")
    if flt(line.get("rate")) != FOIL_NUMBER_ADD_ON_RATE:
        raise ContractFail(f"{label} add-on line should be ${FOIL_NUMBER_ADD_ON_RATE}, found {line.get('rate')}")
    _assert_line_fields(label, line)
    payload = _payload(label, line)
    expected_pairs = {
        "schema_version": CONFIG_VERSION,
        "item_code": FOIL_NUMBER_ADD_ON_ITEM,
        "parent_item_code": expected_parent_item_code,
        "website_item_code": expected_website_item_code,
        "product_page_type": "simple_product",
        "commerce_lane": "checkout",
        "add_on_key": FOIL_NUMBER_ADD_ON_KEY,
        "add_on_label": "Foil number",
        "selected_value": "7",
        "quantity_per_parent": 1,
        "parent_qty": 1,
        "source": "lt_product_page_add_on",
    }
    for key, expected in expected_pairs.items():
        if payload.get(key) != expected:
            raise ContractFail(f"{label} add-on payload {key} should be {expected!r}, found {payload.get(key)!r}")


def _assert_line_fields(label: str, line: Any) -> None:
    for fieldname in LINE_FIELDNAMES.values():
        value = line.get(fieldname) if hasattr(line, "get") else getattr(line, fieldname, None)
        if not value:
            raise ContractFail(f"{label} line missing {fieldname}")


def _payload(label: str, line: Any) -> dict[str, Any]:
    raw = line.get(LINE_FIELDNAMES["json"]) if hasattr(line, "get") else getattr(line, LINE_FIELDNAMES["json"], None)
    try:
        return json.loads(raw or "{}")
    except (TypeError, ValueError) as exc:
        raise ContractFail(f"{label} line payload is not valid JSON: {raw!r}") from exc


def _assert_sales_order_accepts_family_lines(
    token: str,
    lines: list[dict[str, Any]],
    *,
    expected_base_line_count: int,
    expected_add_on_line_count: int,
):
    customer = _create_customer(token)
    sales_order = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "customer": customer.name,
            "order_type": "Shopping Cart",
            "transaction_date": nowdate(),
            "delivery_date": add_days(nowdate(), 7),
            "currency": "USD",
            "selling_price_list": PRICE_LIST,
            "items": lines,
        }
    )
    sales_order.flags.ignore_permissions = True
    sales_order.flags.mute_email = True
    sales_order.insert(ignore_permissions=True)
    sales_order.submit()
    if len(sales_order.items) != len(lines):
        raise ContractFail(f"Sales Order stored {len(sales_order.items)} lines, expected {len(lines)}")
    _assert_stored_rows_preserve_line_fields(
        "Sales Order",
        sales_order.items,
        expected_base_line_count=expected_base_line_count,
        expected_add_on_line_count=expected_add_on_line_count,
    )
    return sales_order


def _assert_invoice_preserves_family_lines(
    sales_order_name: str,
    *,
    expected_line_count: int,
    expected_base_line_count: int,
    expected_add_on_line_count: int,
) -> str:
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    from locally_twisted.product_page_runtime import copy_sales_order_line_configuration_to_invoice

    invoice = make_sales_invoice(sales_order_name, ignore_permissions=True)
    invoice.flags.ignore_permissions = True
    invoice.flags.mute_email = True
    invoice.set_missing_values()
    copy_sales_order_line_configuration_to_invoice(invoice, sales_order_name)
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    if len(invoice.items) != expected_line_count:
        raise ContractFail(f"Sales Invoice stored {len(invoice.items)} lines, expected {expected_line_count}")
    _assert_stored_rows_preserve_line_fields(
        "Sales Invoice",
        invoice.items,
        expected_base_line_count=expected_base_line_count,
        expected_add_on_line_count=expected_add_on_line_count,
    )
    return invoice.name


def _assert_stored_rows_preserve_line_fields(
    label: str,
    rows: list[Any],
    *,
    expected_base_line_count: int,
    expected_add_on_line_count: int,
) -> None:
    base_count = 0
    add_on_count = 0
    for row in rows:
        _assert_line_fields(label, row)
        payload = _payload(label, row)
        if payload.get("schema_version") != CONFIG_VERSION:
            raise ContractFail(f"{label} row lost configuration version: {payload}")
        if payload.get("source") == "lt_product_page_add_on":
            add_on_count += 1
            if payload.get("item_code") != FOIL_NUMBER_ADD_ON_ITEM:
                raise ContractFail(f"{label} add-on row stored wrong item payload: {payload}")
        elif payload.get("source") == "lt_product_page_runtime":
            base_count += 1
            if payload.get("commerce_lane") != "checkout":
                raise ContractFail(f"{label} base row did not preserve checkout lane: {payload}")
        else:
            raise ContractFail(f"{label} row has unknown LT product-page payload source: {payload}")
    if base_count != expected_base_line_count:
        raise ContractFail(f"{label} should store {expected_base_line_count} checkout base SKU lines, found {base_count}")
    if add_on_count != expected_add_on_line_count:
        raise ContractFail(f"{label} should store {expected_add_on_line_count} foil add-on lines, found {add_on_count}")


def _create_customer(token: str):
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"LT Checkout Product Family Contract {token}",
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "All Territories",
        }
    )
    customer.insert(ignore_permissions=True)
    return customer


def _easter_balloon_cups_seasonal_status() -> dict[str, Any]:
    row = frappe.db.get_value(
        "Website Item",
        {"item_code": EASTER_BALLOON_CUPS_WEBSITE_ITEM},
        ["item_code", "web_item_name", "published", "lt_product_page_type", "lt_commerce_lane"],
        as_dict=True,
    )
    if not row:
        return {
            "website_item_code": EASTER_BALLOON_CUPS_WEBSITE_ITEM,
            "status": "deferred_pending_seasonal_approval",
            "found": False,
        }
    return {
        "website_item_code": EASTER_BALLOON_CUPS_WEBSITE_ITEM,
        "web_item_name": row.get("web_item_name"),
        "published": bool(row.get("published")),
        "stored_contract": f"{row.get('lt_product_page_type')}|{row.get('lt_commerce_lane')}",
        "status": "deferred_pending_seasonal_approval",
        "note": "Seasonal orderability/visibility is a separate GL/business approval; this verifier did not claim Easter launch readiness.",
    }


def _survivor_counts(token: str) -> dict[str, int]:
    customer_names = frappe.get_all(
        "Customer",
        filters={"customer_name": ["like", f"%{token}%"]},
        pluck="name",
    )
    return {
        "customer": len(customer_names),
        "sales_order": frappe.db.count("Sales Order", {"customer": ["in", customer_names]}) if customer_names else 0,
        "sales_invoice": frappe.db.count("Sales Invoice", {"customer": ["in", customer_names]}) if customer_names else 0,
    }
