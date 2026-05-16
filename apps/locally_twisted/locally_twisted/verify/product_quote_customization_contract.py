"""Contract for quote-first customization payloads."""
from __future__ import annotations

import json
import time

import frappe

from locally_twisted.product_page_runtime import CONFIG_VERSION
from locally_twisted.product_quote_runtime import QUOTATION_FIELDNAMES
from locally_twisted.product_quote_request import normalize_public_product_quote_payload


class ContractFail(Exception):
    pass


def run() -> dict[str, object]:
    original_commit = frappe.db.commit

    def no_commit(*args, **kwargs):
        return None

    try:
        frappe.db.commit = no_commit
        result = _run_contract()
        result["rolled_back"] = True
        return result
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        frappe.db.rollback()


def _run_contract() -> dict[str, object]:
    payload = _normalized_payload()
    _assert_color_recipe(payload)
    quotation = _assert_draft_quotation_preserves_color_recipe(payload)
    _assert_bad_color_recipe_fails_loudly()
    return {
        "ok": True,
        "color_recipe_count": len(payload.get("color_recipes") or []),
        "quotation": quotation.name,
    }


def _normalized_payload() -> dict[str, object]:
    return normalize_public_product_quote_payload(
        item={
            "item_code": "classic-arch",
            "web_item_name": "Classic Arch",
            "item_group": "Arches",
            "route": "/shop-items/arches/classic-arch",
        },
        contract={
            "product_page_type": "complex_custom_product",
            "commerce_lane": "quote_first",
        },
        incoming={
            "schema_version": CONFIG_VERSION,
            "source": "product-page-quote-form",
            "website_item_code": "classic-arch",
            "product_page_type": "complex_custom_product",
            "commerce_lane": "quote_first",
            "selected_options": {
                "Arch Size": "20ft",
                "latex colors": "Reflex Champage, White, Navy",
            },
            "customizations": [
                {
                    "axis": "latex colors",
                    "values": ["Reflex Champage", "White", "Navy"],
                    "label": "Balloon color recipe",
                }
            ],
            "needs_operator_review": True,
        },
    )


def _assert_color_recipe(payload: dict[str, object]) -> None:
    recipes = payload.get("color_recipes")
    if not isinstance(recipes, list) or len(recipes) != 1:
        raise ContractFail(f"expected one structured color recipe, found {recipes!r}")
    recipe = recipes[0]
    if recipe.get("axis") != "latex colors":
        raise ContractFail(f"color recipe lost source axis: {recipe}")
    if recipe.get("values") != ["Reflex Champagne", "White", "Navy"]:
        raise ContractFail(f"color recipe lost selected values: {recipe}")
    groups = {group.get("group") for group in recipe.get("color_groups") or []}
    if "Reflex" not in groups or "Neutrals" not in groups:
        raise ContractFail(f"color recipe did not preserve grouped color metadata: {recipe}")
    summary = str(payload.get("summary") or "")
    if "Balloon color recipe: Reflex Champagne, White, Navy" not in summary:
        raise ContractFail(f"summary did not surface color recipe: {summary}")


def _assert_draft_quotation_preserves_color_recipe(payload: dict[str, object]):
    from locally_twisted.product_quote_runtime import create_product_page_draft_quotation_from_lead

    token = str(int(time.time() * 1000))
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": f"LT Color Recipe Contract {token}",
            "email_id": f"lt-color-recipe-{token}@example.invalid",
            "source": "Website",
            "status": "Open",
            "custom_lt_product_template_item": "classic-arch",
            "custom_lt_product_page_type": "complex_custom_product",
            "custom_lt_product_quote_summary": payload["summary"],
            "custom_lt_product_quote_payload": json.dumps(payload, sort_keys=True),
        }
    )
    lead.insert(ignore_permissions=True)
    quotation = create_product_page_draft_quotation_from_lead(lead.name)
    stored_payload = json.loads(quotation.get(QUOTATION_FIELDNAMES["json"]))
    if stored_payload.get("color_recipes") != payload.get("color_recipes"):
        raise ContractFail(f"draft Quotation lost color recipes: {stored_payload}")
    line_payload = json.loads(quotation.items[0].get("custom_lt_configuration_json"))
    if line_payload.get("color_recipes") != payload.get("color_recipes"):
        raise ContractFail(f"Quotation Item lost color recipes: {line_payload}")
    return quotation


def _assert_bad_color_recipe_fails_loudly() -> None:
    try:
        normalize_public_product_quote_payload(
            item={"item_code": "classic-arch", "web_item_name": "Classic Arch"},
            contract={"product_page_type": "complex_custom_product", "commerce_lane": "quote_first"},
            incoming={
                "schema_version": CONFIG_VERSION,
                "product_page_type": "complex_custom_product",
                "commerce_lane": "quote_first",
                "selected_options": {"latex colors": {"not": "allowed"}},
            },
        )
    except frappe.ValidationError as exc:
        if "product quote options" not in str(exc):
            raise ContractFail(f"bad color payload failed with unclear message: {exc}")
        return
    raise ContractFail("bad color payload should fail loudly")
