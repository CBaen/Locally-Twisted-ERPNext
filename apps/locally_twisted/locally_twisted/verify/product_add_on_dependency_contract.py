"""Verify checkout add-on dependency boundaries for product-page templates."""
from __future__ import annotations

import json

import frappe
from frappe.utils import flt

from locally_twisted.catalog_contract.addon_rules import CONFIRMED_ADD_ONS, REVIEW_ADD_ONS
from locally_twisted.product_page_runtime import (
    ADD_ON_ITEM_CONTRACTS,
    CONFIG_VERSION,
    LINE_FIELDNAMES,
    REVIEW_ONLY_SOURCE_ADD_ONS,
    _canonical_add_on_key,
    sales_order_add_on_lines,
    sales_order_line_configuration_fields,
)


PROOF_ITEM = "unicorn-bouquet-SMA"
PROOF_WEBSITE_ITEM = "unicorn-bouquet"
FOIL_NUMBER_ITEM = "ADDON-FOIL-NUMBER"


class ContractFail(Exception):
    pass


def run() -> dict[str, object]:
    try:
        _assert_source_review_axes_have_runtime_quote_boundaries()
        _assert_confirmed_foil_number_stays_priced_checkout()
        return {
            "ok": True,
            "confirmed_add_ons": sorted(CONFIRMED_ADD_ONS),
            "review_only_source_add_ons": sorted(REVIEW_ADD_ONS),
            "runtime_review_only_keys": sorted(REVIEW_ONLY_SOURCE_ADD_ONS),
        }
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}


def _assert_source_review_axes_have_runtime_quote_boundaries() -> None:
    source_keys = {_canonical_add_on_key(axis_name): axis_name for axis_name in REVIEW_ADD_ONS}
    missing_runtime_keys = sorted(set(source_keys) - set(REVIEW_ONLY_SOURCE_ADD_ONS))
    if missing_runtime_keys:
        raise ContractFail(f"review-only source add-ons missing runtime quote boundary: {missing_runtime_keys}")

    surprise_runtime_keys = sorted(set(REVIEW_ONLY_SOURCE_ADD_ONS) - set(source_keys))
    if surprise_runtime_keys:
        raise ContractFail(f"runtime review-only add-ons are not declared in source rules: {surprise_runtime_keys}")

    for key, source_attribute in source_keys.items():
        if key in ADD_ON_ITEM_CONTRACTS:
            raise ContractFail(f"review-only source add-on {source_attribute!r} is incorrectly checkout-priced")
        _assert_review_only_add_on_rejects_paid_checkout(key, source_attribute)


def _assert_review_only_add_on_rejects_paid_checkout(key: str, source_attribute: str) -> None:
    configuration = _configuration(
        add_ons=[
            {
                "key": key,
                "label": source_attribute,
                "source_attribute": source_attribute,
                "value": "Review this option",
                "quantity": 1,
            }
        ]
    )
    try:
        sales_order_line_configuration_fields(
            resolved_item=_resolved_item(),
            client_configuration=configuration,
        )
    except frappe.ValidationError as exc:
        if "needs a quote before checkout" not in str(exc):
            raise ContractFail(f"{source_attribute!r} failed with the wrong message: {exc}") from exc
        return
    raise ContractFail(f"{source_attribute!r} did not route to quote before paid checkout")


def _assert_confirmed_foil_number_stays_priced_checkout() -> None:
    if "Add Foil Number" not in CONFIRMED_ADD_ONS:
        raise ContractFail("source rules lost confirmed Add Foil Number decision")
    if "foil_number" not in ADD_ON_ITEM_CONTRACTS:
        raise ContractFail("runtime lost confirmed foil_number add-on contract")
    if "foil_number" in REVIEW_ONLY_SOURCE_ADD_ONS:
        raise ContractFail("confirmed foil_number add-on was accidentally marked review-only")

    configuration = _configuration(
        add_ons=[
            {
                "key": "foil_number",
                "label": "Foil number",
                "value": "111",
                "quantity": 3,
            }
        ]
    )
    line = sales_order_line_configuration_fields(
        resolved_item=_resolved_item(),
        client_configuration=configuration,
    )
    payload = json.loads(line.get(LINE_FIELDNAMES["json"]) or "{}")
    if payload.get("add_ons", [{}])[0].get("key") != "foil_number":
        raise ContractFail(f"base line did not preserve confirmed foil_number add-on: {payload}")

    add_on_lines = sales_order_add_on_lines(
        resolved_item=_resolved_item(),
        client_configuration=configuration,
        parent_qty=1,
    )
    if len(add_on_lines) != 1:
        raise ContractFail(f"confirmed foil_number should create one priced add-on line, found {len(add_on_lines)}")
    add_on_line = add_on_lines[0]
    if add_on_line.get("item_code") != FOIL_NUMBER_ITEM:
        raise ContractFail(f"confirmed foil_number line used wrong Item: {add_on_line.get('item_code')}")
    if int(add_on_line.get("qty") or 0) != 3:
        raise ContractFail(f"foil number '111' should create quantity 3, found {add_on_line.get('qty')}")
    if flt(add_on_line.get("rate")) != flt(ADD_ON_ITEM_CONTRACTS["foil_number"]["rate"]):
        raise ContractFail(f"foil_number add-on line used wrong rate: {add_on_line.get('rate')}")


def _resolved_item() -> dict[str, object]:
    return {
        "item_code": PROOF_ITEM,
        "website_item_code": PROOF_WEBSITE_ITEM,
        "variant_options": [{"attribute": "Bouquet Size", "attribute_value": "Small"}],
    }


def _configuration(*, add_ons: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": CONFIG_VERSION,
        "item_code": PROOF_ITEM,
        "website_item_code": PROOF_WEBSITE_ITEM,
        "selected_options": {"Bouquet Size": "Small"},
        "add_ons": add_ons,
        "customizations": [],
    }
