"""Runtime product-page contract helpers for LT Webshop flows.

This module owns ERPNext-side preservation for the reusable product page
types. Catalog/source audit code can describe products, but checkout and
quote flows must use this runtime layer before creating business records.
"""
from __future__ import annotations

import json
import re
from typing import Any

import frappe
from frappe import _

from locally_twisted.catalog_contract.color_rules import (
    canonical_color_name,
    grouped_colors,
    is_balloon_color_axis,
)
from locally_twisted.catalog_variant_rules import required_variant_attribute_names
from locally_twisted.checkout_fulfillment import LINE_FULFILLMENT_FIELDNAMES
from locally_twisted.product_page_labels import COMMERCE_LANE_OPTIONS, PRODUCT_PAGE_TYPE_OPTIONS
from locally_twisted.product_setup_runtime import (
    product_setup_schema_for_website_item,
    resolve_product_setup_media,
    resolve_product_setup_configuration,
)
from locally_twisted.product_variant_media import approved_variant_item_media_for_codes


CONFIG_VERSION = "lt-product-config-v1"
PRICE_LIST = "Standard Selling"

WEBSITE_ITEM_PAGE_TYPE_FIELD = "lt_product_page_type"
WEBSITE_ITEM_COMMERCE_LANE_FIELD = "lt_commerce_lane"

LINE_FIELDNAMES = {
    "template_item": "custom_lt_product_template_item",
    "page_type": "custom_lt_product_page_type",
    "version": "custom_lt_configuration_version",
    "summary": "custom_lt_configuration_summary",
    "json": "custom_lt_configuration_json",
}

MAX_CONFIGURATION_BYTES = 12000
MAX_ADD_ON_QUANTITY = 10
MAX_FOIL_NUMBER_DIGITS = 3
MAX_COLOR_RECIPE_VALUES = 24

FOIL_NUMBER_ELIGIBLE_WEBSITE_ITEMS = (
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

ADD_ON_ITEM_CONTRACTS = {
    "foil_number": {
        "item_code": "ADDON-FOIL-NUMBER",
        "item_name": "Foil Number Add-On",
        "label": "Foil number",
        "item_group": "Bouquets",
        "description": "Add number foils to make it a birthday bouquet.",
        "rate": 12.0,
        "eligible_website_item_codes": FOIL_NUMBER_ELIGIBLE_WEBSITE_ITEMS,
        "input_type": "digit_text",
        "quantity_min": 1,
        "quantity_max": MAX_FOIL_NUMBER_DIGITS,
        "value_label": "Numbers",
        "maxlength": MAX_FOIL_NUMBER_DIGITS,
        "pattern": "[0-9]{1,3}",
        "help": "Choose up to 3 number foils. Repeated digits are okay.",
    },
}

ADD_ON_KEY_ALIASES = {
    "add_foil_number": "foil_number",
}


def checkout_add_on_contracts_for_item(website_item_code: str | None) -> dict[str, dict[str, Any]]:
    """Return static and blueprint-authored checkout add-ons for a product page."""
    contracts = {key: dict(value) for key, value in ADD_ON_ITEM_CONTRACTS.items()}
    contracts.update(_blueprint_add_on_contracts_for_item(website_item_code))
    return contracts


def _blueprint_add_on_contracts_for_item(website_item_code: str | None) -> dict[str, dict[str, Any]]:
    website_item_code = str(website_item_code or "").strip()
    if not website_item_code:
        return {}
    if not frappe.db.exists("DocType", "LT Product Blueprint"):
        return {}
    blueprint_names = frappe.get_all(
        "LT Product Blueprint",
        filters={"target_item_code": website_item_code},
        pluck="name",
    )
    if not blueprint_names:
        return {}
    rows = frappe.get_all(
        "LT Product Blueprint Add On",
        filters={
            "parent": ["in", blueprint_names],
            "parenttype": "LT Product Blueprint",
            "checkout_approved": 1,
            "price_source": "Fixed Item Price",
        },
        fields=["add_on_name", "add_on_item", "requires_value", "quantity_min", "quantity_max"],
        order_by="idx asc",
    )
    contracts: dict[str, dict[str, Any]] = {}
    for row in rows:
        item_code = str(row.get("add_on_item") or "").strip()
        if not item_code:
            continue
        item = frappe.db.get_value(
            "Item",
            {"item_code": item_code, "disabled": 0},
            ["item_code", "item_name", "item_group", "description"],
            as_dict=True,
        )
        if not item:
            continue
        label = str(row.get("add_on_name") or item.get("item_name") or item_code).strip()
        key = f"blueprint_{_canonical_add_on_key(label or item_code)}"
        contracts[key] = {
            "item_code": item_code,
            "item_name": item.get("item_name") or label,
            "label": label,
            "item_group": item.get("item_group") or "",
            "description": item.get("description") or f"Blueprint add-on for {website_item_code}.",
            "eligible_website_item_codes": (website_item_code,),
            "input_type": "number_text" if row.get("requires_value") else "quantity",
            "quantity_min": int(row.get("quantity_min") or 0),
            "quantity_max": int(row.get("quantity_max") or MAX_ADD_ON_QUANTITY),
            "source": "lt_product_blueprint",
        }
    return contracts


# Retired catalog add-on-looking axes that are known, but not approved for
# paid checkout. They must fail as quote-required instead of looking like
# broken setup or silently becoming free options.
REVIEW_ONLY_SOURCE_ADD_ONS = {
    "add_ons": {
        "label": "Add ons",
        "source_attribute": "Add ons",
        "review_reason": "Potential optional add-ons need product-family mapping before checkout.",
    },
    "plush_add_ons": {
        "label": "Plush add ons",
        "source_attribute": "Plush add ons",
        "review_reason": "Plush upgrades need product-family mapping before checkout.",
    },
    "orbz_toppers": {
        "label": "Orbz toppers",
        "source_attribute": "Orbz toppers",
        "review_reason": "Topper upgrades need product-family mapping before checkout.",
    },
    "add_bouquet": {
        "label": "Add Bouquet",
        "source_attribute": "Add Bouquet",
        "review_reason": "Companion bouquets need GL/product-family confirmation before checkout.",
    },
}

CUSTOMER_SAFE_SETUP_FALLBACK = (
    "Tiny snag: this checkout setup needs a quick team review. "
    "Please request a quote while we fix it."
)

_CUSTOMER_UNSAFE_MARKERS = (
    "Missing Item",
    "Missing Item Price",
    "Missing Sales",
    "Missing Quotation",
    "Missing ",
    "Unknown add-on",
    "Add-on:",
    "ADDON-",
    "custom_lt_",
)

_CHECKOUT_GROUP_HINTS = (
    "bouquet",
    "bouquets",
    "deliveries",
    "delivery",
    "get well",
    "get-well",
    "seasonal",
    "grab",
)


def customer_safe_checkout_error(message: Any) -> str:
    """Strip setup/debug evidence from a customer-facing checkout message."""
    text = " ".join(str(message or "").split())
    if not text:
        return CUSTOMER_SAFE_SETUP_FALLBACK

    safe = text
    for marker in _CUSTOMER_UNSAFE_MARKERS:
        if marker in safe:
            safe = safe.split(marker, 1)[0].strip()
    if safe and safe.lower().startswith("tiny snag") and not _contains_internal_marker(safe):
        return safe
    return CUSTOMER_SAFE_SETUP_FALLBACK


def normalize_client_configuration(raw: Any) -> dict[str, Any] | None:
    """Validate optional cart-line configuration from the browser.

    Old carts may only contain item_code/qty. Once a page starts sending
    executable configuration, the payload must declare the current schema
    version or it fails loudly instead of dropping choices on the floor.
    """
    if raw in (None, "", {}):
        return None

    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            frappe.throw(
                _("Tiny snag: this item option data did not come through cleanly. Please choose the options again."),
                frappe.ValidationError,
            )

    if not isinstance(raw, dict):
        frappe.throw(
            _("Tiny snag: this item option data did not come through cleanly. Please choose the options again."),
            frappe.ValidationError,
        )

    version = raw.get("schema_version") or raw.get("version")
    if version != CONFIG_VERSION:
        frappe.throw(
            _(
                "Tiny snag: this cart item was saved with an older option format. "
                "Please remove it, choose the options again, and we will keep the details safe."
            ),
            frappe.ValidationError,
        )

    try:
        encoded = json.dumps(raw, sort_keys=True, default=str)
    except (TypeError, ValueError):
        frappe.throw(
            _("Tiny snag: this item option data has a value we cannot save yet. Please choose the options again."),
            frappe.ValidationError,
        )
    if len(encoded.encode("utf-8")) > MAX_CONFIGURATION_BYTES:
        frappe.throw(
            _("Tiny snag: this item has too many option details for checkout. Please request a quote and we will help."),
            frappe.ValidationError,
        )

    normalized = json.loads(encoded)
    normalized["color_recipes"] = _normalized_color_recipes(normalized)
    encoded = json.dumps(normalized, sort_keys=True, default=str)
    if len(encoded.encode("utf-8")) > MAX_CONFIGURATION_BYTES:
        frappe.throw(
            _("Tiny snag: this item has too many option details for checkout. Please request a quote and we will help."),
            frappe.ValidationError,
        )

    return normalized


def cart_line_key(item_code: str, client_configuration: dict[str, Any] | None = None) -> str:
    """Stable browser/server identity for one configured cart line."""
    item_code = str(item_code or "").strip()
    configuration = normalize_client_configuration(client_configuration)
    configuration_key = ""
    if configuration:
        configuration_key = json.dumps(
            configuration,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
            ensure_ascii=False,
        )
    return f"{item_code}::{configuration_key}"


def product_page_contract_for_website_item(website_item_code: str | None) -> dict[str, str]:
    """Return page-type fields for a Website Item, with safe defaults."""
    website_item_code = (website_item_code or "").strip()
    if not website_item_code:
        return {"product_page_type": "needs_review", "commerce_lane": "needs_review"}

    meta = frappe.get_meta("Website Item")
    fields = ["item_code", "web_item_name", "item_group"]
    if meta.has_field(WEBSITE_ITEM_PAGE_TYPE_FIELD):
        fields.append(WEBSITE_ITEM_PAGE_TYPE_FIELD)
    if meta.has_field(WEBSITE_ITEM_COMMERCE_LANE_FIELD):
        fields.append(WEBSITE_ITEM_COMMERCE_LANE_FIELD)

    row = frappe.db.get_value(
        "Website Item",
        {"item_code": website_item_code},
        fields,
        as_dict=True,
    ) or {}

    inferred = _inferred_product_page_contract(website_item_code, row)
    explicit_page_type = _known_or_empty(row.get(WEBSITE_ITEM_PAGE_TYPE_FIELD), PRODUCT_PAGE_TYPE_OPTIONS)
    explicit_commerce_lane = _known_or_empty(row.get(WEBSITE_ITEM_COMMERCE_LANE_FIELD), COMMERCE_LANE_OPTIONS)
    resolved = resolved_product_page_contract_values(
        explicit_page_type=explicit_page_type,
        explicit_commerce_lane=explicit_commerce_lane,
        inferred=inferred,
    )
    return {
        "product_page_type": resolved["product_page_type"],
        "commerce_lane": resolved["commerce_lane"],
        "web_item_name": row.get("web_item_name") or website_item_code,
        "item_group": row.get("item_group") or "",
    }


def resolved_product_page_contract_values(
    *,
    explicit_page_type: str,
    explicit_commerce_lane: str,
    inferred: dict[str, str],
) -> dict[str, str]:
    """Resolve stored Website Item fields with fail-closed checkout precedence.

    Paid checkout is allowed only when the Website Item explicitly says
    `checkout` and a known product page type. Inference can preserve review
    behavior for unclassified products, but it must never infer paid checkout
    from item-group hints or partially-filled fields.
    """
    inferred_page_type = inferred.get("product_page_type") or "needs_review"
    inferred_commerce_lane = inferred.get("commerce_lane") or "needs_review"

    if explicit_commerce_lane == "checkout" and explicit_page_type in {"simple_product", "complex_custom_product"}:
        return {"product_page_type": explicit_page_type, "commerce_lane": "checkout"}

    if explicit_page_type == "complex_custom_product" and explicit_commerce_lane == "quote_first":
        return {"product_page_type": "complex_custom_product", "commerce_lane": "quote_first"}

    if explicit_page_type == "needs_review" or explicit_commerce_lane == "needs_review":
        return {"product_page_type": "needs_review", "commerce_lane": "needs_review"}

    if explicit_commerce_lane == "checkout":
        return {"product_page_type": "needs_review", "commerce_lane": "needs_review"}

    if explicit_commerce_lane == "quote_first":
        page_type = explicit_page_type or inferred_page_type
        if page_type == "needs_review":
            page_type = "complex_custom_product"
        return {"product_page_type": page_type, "commerce_lane": "quote_first"}

    if inferred_commerce_lane == "checkout":
        return {"product_page_type": "needs_review", "commerce_lane": "needs_review"}

    if inferred_page_type == "needs_review" or inferred_commerce_lane == "needs_review":
        return {"product_page_type": "needs_review", "commerce_lane": "needs_review"}

    return {"product_page_type": inferred_page_type, "commerce_lane": inferred_commerce_lane}


def _inferred_product_page_contract(website_item_code: str, website_item: dict[str, Any]) -> dict[str, str]:
    """Conservative fallback when ERPNext page-template fields are unset.

    Imported Website Items can exist before their template/lane fields are
    synced. In that state, paid checkout must not be the default. We infer from
    live variant axes and item group so complex work routes to quote-first.
    """
    attributes = _live_variant_attribute_names(website_item_code)
    required_attributes = required_variant_attribute_names(attributes)
    if any(is_balloon_color_axis(attribute) for attribute in attributes):
        return {"product_page_type": "complex_custom_product", "commerce_lane": "quote_first"}
    if len(required_attributes) > 1:
        return {"product_page_type": "complex_custom_product", "commerce_lane": "quote_first"}
    if _group_suggests_checkout(website_item.get("item_group")):
        return {"product_page_type": "simple_product", "commerce_lane": "checkout"}
    if required_attributes:
        return {"product_page_type": "complex_custom_product", "commerce_lane": "quote_first"}
    return {"product_page_type": "needs_review", "commerce_lane": "needs_review"}


def _live_variant_attribute_names(website_item_code: str) -> list[str]:
    rows = frappe.db.sql(
        """
        SELECT DISTINCT attr.attribute
        FROM `tabItem Variant Attribute` attr
        JOIN `tabItem` item
          ON item.name = attr.parent
        WHERE item.disabled = 0
          AND (item.item_code = %(item_code)s OR item.variant_of = %(item_code)s)
        ORDER BY attr.idx ASC, attr.attribute ASC
        """,
        {"item_code": website_item_code},
        as_dict=True,
    )
    return [str(row.get("attribute") or "").strip() for row in rows if row.get("attribute")]


def _group_suggests_checkout(item_group: Any) -> bool:
    text = str(item_group or "").lower()
    return any(hint in text for hint in _CHECKOUT_GROUP_HINTS)


def sales_order_line_configuration_fields(
    *,
    resolved_item: dict[str, Any],
    client_configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build custom Sales Order Item fields for a resolved cart line."""
    _assert_line_storage("Sales Order Item")

    website_item_code = resolved_item.get("website_item_code") or resolved_item.get("item_code")
    contract = product_page_contract_for_website_item(website_item_code)
    if contract["commerce_lane"] != "checkout":
        frappe.throw(
            _(
                "Tiny snag: this design needs a quote before checkout. "
                "Please send it through the inquiry form so we keep the details together."
            ),
            frappe.ValidationError,
        )

    variant_options = _variant_options_dict(resolved_item.get("variant_options") or [])
    client_configuration = normalize_client_configuration(client_configuration)
    setup_resolution = _product_setup_resolution_for_checkout(
        website_item_code=website_item_code,
        client_configuration=client_configuration,
        variant_options=variant_options,
    )
    selected_media = _selected_media_for_checkout(
        website_item_code=website_item_code,
        resolved_item=resolved_item,
        client_configuration=client_configuration,
        setup_resolution=setup_resolution,
    )
    selected_content = (setup_resolution or {}).get("selected_content") or {}
    color_recipes = _validated_checkout_color_recipes(client_configuration, variant_options=variant_options)
    _assert_checkout_configuration_is_priced(
        client_configuration,
        website_item_code=website_item_code,
        variant_options=variant_options,
        allow_configuration_groups=bool(setup_resolution),
    )
    sale_unit_options = {
        attribute: value for attribute, value in variant_options.items() if not is_balloon_color_axis(attribute)
    }
    _assert_client_options_match_variant(
        client_configuration=client_configuration,
        variant_options=sale_unit_options,
        resolved_item=resolved_item,
        setup_resolution=setup_resolution,
    )

    payload = {
        "schema_version": CONFIG_VERSION,
        "item_code": resolved_item.get("item_code"),
        "website_item_code": website_item_code,
        "product_page_type": contract["product_page_type"],
        "commerce_lane": contract["commerce_lane"],
        "selected_options": sale_unit_options,
        "color_recipes": color_recipes,
        "add_ons": _validated_checkout_add_ons(client_configuration, website_item_code=website_item_code),
        "configuration_groups": _configuration_groups_from_resolution(setup_resolution, client_configuration),
        "customizations": _non_color_customizations(client_configuration),
        "validation_hash": (setup_resolution or {}).get("validation_hash"),
        "source": "lt_product_page_runtime",
    }
    if selected_media:
        payload["selected_media"] = selected_media
    if selected_content:
        payload["selected_content"] = selected_content
    summary = _configuration_summary(payload)

    return {
        LINE_FIELDNAMES["template_item"]: website_item_code,
        LINE_FIELDNAMES["page_type"]: contract["product_page_type"],
        LINE_FIELDNAMES["version"]: CONFIG_VERSION,
        LINE_FIELDNAMES["summary"]: summary,
        LINE_FIELDNAMES["json"]: json.dumps(payload, sort_keys=True, default=str),
    }


def sales_order_add_on_lines(
    *,
    resolved_item: dict[str, Any],
    client_configuration: dict[str, Any] | None = None,
    parent_qty: int = 1,
) -> list[dict[str, Any]]:
    """Build extra Sales Order Item rows for priced product-page add-ons."""
    _assert_line_storage("Sales Order Item")

    client_configuration = normalize_client_configuration(client_configuration)
    website_item_code = resolved_item.get("website_item_code") or resolved_item.get("item_code")
    add_ons = _validated_checkout_add_ons(client_configuration, website_item_code=website_item_code)
    if not add_ons:
        return []

    contract = product_page_contract_for_website_item(website_item_code)
    if contract["commerce_lane"] != "checkout":
        frappe.throw(
            _(
                "Tiny snag: this design needs a quote before checkout. "
                "Please send it through the inquiry form so we keep the details together."
            ),
            frappe.ValidationError,
        )

    lines = []
    add_on_contracts = checkout_add_on_contracts_for_item(website_item_code)
    for add_on in add_ons:
        spec = add_on_contracts[add_on["key"]]
        item = frappe.db.get_value(
            "Item",
            {"item_code": spec["item_code"], "disabled": 0},
            ["item_code", "item_name", "item_group"],
            as_dict=True,
        )
        if not item:
            frappe.log_error(
                f"Missing Item: {spec['item_code']}",
                "LT product add-on checkout setup missing",
            )
            frappe.throw(
                _(
                    "Tiny snag: this add-on is not set up for checkout yet. "
                    "Please request a quote so we do not lose the upgrade."
                ),
                frappe.ValidationError,
            )
        rate = frappe.db.get_value(
            "Item Price",
            {"item_code": spec["item_code"], "price_list": PRICE_LIST, "selling": 1},
            "price_list_rate",
        )
        if rate in (None, ""):
            frappe.log_error(
                f"Missing Item Price: {spec['item_code']} / {PRICE_LIST}",
                "LT product add-on checkout price missing",
            )
            frappe.throw(
                _(
                    "Tiny snag: this add-on is missing its checkout price. "
                    "Please request a quote so we do not sell an upgrade as free."
                ),
                frappe.ValidationError,
            )

        parent_qty_value = max(1, int(parent_qty or 1))
        line_qty = parent_qty_value * add_on["quantity"]
        payload = {
            "schema_version": CONFIG_VERSION,
            "item_code": spec["item_code"],
            "parent_item_code": resolved_item.get("item_code"),
            "website_item_code": website_item_code,
            "product_page_type": contract["product_page_type"],
            "commerce_lane": contract["commerce_lane"],
            "add_on_key": add_on["key"],
            "add_on_label": add_on["label"],
            "selected_value": add_on.get("value"),
            "quantity_per_parent": add_on["quantity"],
            "parent_qty": parent_qty_value,
            "source": "lt_product_page_add_on",
        }
        lines.append(
            {
                "item_code": spec["item_code"],
                "item_name": item.get("item_name") or spec["item_name"],
                "item_group": item.get("item_group") or spec["item_group"],
                "qty": line_qty,
                "rate": float(rate),
                LINE_FIELDNAMES["template_item"]: website_item_code,
                LINE_FIELDNAMES["page_type"]: contract["product_page_type"],
                LINE_FIELDNAMES["version"]: CONFIG_VERSION,
                LINE_FIELDNAMES["summary"]: _add_on_summary(payload),
                LINE_FIELDNAMES["json"]: json.dumps(payload, sort_keys=True, default=str),
            }
        )
    return lines


def copy_sales_order_line_configuration_to_invoice(invoice_doc, sales_order_name: str) -> None:
    """Copy LT line configuration from Sales Order Item to Sales Invoice Item."""
    _assert_line_storage("Sales Invoice Item")

    sales_order = frappe.get_doc("Sales Order", sales_order_name)
    so_items = {row.name: row for row in sales_order.items}
    fallback_by_code: dict[str, list[Any]] = {}
    for row in sales_order.items:
        fallback_by_code.setdefault(row.item_code, []).append(row)

    for invoice_row in invoice_doc.items:
        source_row = so_items.get(invoice_row.get("so_detail"))
        if not source_row:
            candidates = fallback_by_code.get(invoice_row.item_code) or []
            source_row = candidates[0] if len(candidates) == 1 else None
        if not source_row:
            continue
        for fieldname in [*LINE_FIELDNAMES.values(), *LINE_FULFILLMENT_FIELDNAMES.values()]:
            value = source_row.get(fieldname)
            if value not in (None, ""):
                invoice_row.set(fieldname, value)


def _assert_line_storage(doctype: str) -> None:
    meta = frappe.get_meta(doctype)
    missing = [field for field in LINE_FIELDNAMES.values() if not meta.has_field(field)]
    if missing:
        frappe.log_error(
            f"Missing {doctype} fields: {', '.join(missing)}",
            "LT product-page runtime fields missing",
        )
        frappe.throw(
            _(
                "Tiny snag: the checkout option storage is not installed yet. "
                "Please request a quote while we finish this page type."
            ),
            frappe.ValidationError,
        )


def _assert_checkout_configuration_is_priced(
    client_configuration: dict[str, Any] | None,
    *,
    website_item_code: str | None,
    variant_options: dict[str, str] | None = None,
    allow_configuration_groups: bool = False,
) -> None:
    if not client_configuration:
        if any(is_balloon_color_axis(axis) for axis in (variant_options or {})):
            frappe.throw(
                _(
                    "Tiny snag: this product needs color choices saved as a color recipe before checkout. "
                    "Please choose the colors again so we keep the details together."
                ),
                frappe.ValidationError,
            )
        return
    _validated_checkout_add_ons(client_configuration, website_item_code=website_item_code)
    _validated_checkout_color_recipes(client_configuration, variant_options=variant_options or {})
    if _configuration_groups(client_configuration) and not allow_configuration_groups:
        frappe.throw(
            _(
                "Tiny snag: these product choices are not connected to checkout yet. "
                "Please request a quote so the details stay with the request."
            ),
            frappe.ValidationError,
        )
    if _non_color_customizations(client_configuration):
        frappe.throw(
            _(
                "Tiny snag: custom option details are not connected to paid checkout yet. "
                "Please request a quote so the design notes stay with the inquiry."
            ),
            frappe.ValidationError,
        )


def _product_setup_resolution_for_checkout(
    *,
    website_item_code: str | None,
    client_configuration: dict[str, Any] | None,
    variant_options: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    schema = product_setup_schema_for_website_item(website_item_code)
    if not schema:
        return None
    resolution = resolve_product_setup_configuration(
        schema,
        client_configuration or {},
        trusted_variant_attributes=variant_options or {},
    )
    if not resolution.get("ok") or resolution.get("commerce_outcome") != "checkout":
        frappe.throw(
            _(
                "Tiny snag: this product setup needs review before checkout. "
                "Please adjust the selections or ask the team for help."
            ),
            frappe.ValidationError,
        )
    return resolution


def _selected_media_for_checkout(
    *,
    website_item_code: str | None,
    resolved_item: dict[str, Any],
    client_configuration: dict[str, Any] | None,
    setup_resolution: dict[str, Any] | None,
) -> dict[str, Any]:
    if setup_resolution and setup_resolution.get("selected_media"):
        return setup_resolution["selected_media"]
    schema = product_setup_schema_for_website_item(website_item_code)
    setup_media = resolve_product_setup_media(
        schema,
        variant_item_code=resolved_item.get("item_code"),
        configuration=client_configuration,
    )
    if setup_media:
        return setup_media
    return approved_variant_item_media_for_codes(
        variant_item_code=resolved_item.get("item_code"),
        website_item_code=website_item_code,
    )


def _assert_client_options_match_variant(
    *,
    client_configuration: dict[str, Any] | None,
    variant_options: dict[str, str],
    resolved_item: dict[str, Any],
    setup_resolution: dict[str, Any] | None = None,
) -> None:
    if not client_configuration:
        return
    expected_item = client_configuration.get("item_code")
    if expected_item and expected_item != resolved_item.get("item_code"):
        frappe.throw(
            _("Tiny snag: this cart item's saved options point to a different item. Please choose the options again."),
            frappe.ValidationError,
        )
    if setup_resolution:
        resolved_attributes = setup_resolution.get("resolved_variant_attributes") or {}
        for attribute, value in resolved_attributes.items():
            if attribute not in variant_options or str(value) != str(variant_options.get(attribute)):
                frappe.throw(
                    _(
                        "Tiny snag: this cart item's saved setup no longer matches the selected item. "
                        "Please choose the options again."
                    ),
                    frappe.ValidationError,
                )
        return
    selected = client_configuration.get("selected_options") or {}
    if not isinstance(selected, dict):
        frappe.throw(
            _("Tiny snag: this cart item's selected options are not readable. Please choose the options again."),
            frappe.ValidationError,
        )
    color_axes = sorted(attribute for attribute in selected if is_balloon_color_axis(attribute))
    if color_axes:
        frappe.throw(
            _(
                "Tiny snag: color choices must be saved as a color recipe before checkout. "
                "Please choose the colors again so we keep the details together."
            ),
            frappe.ValidationError,
        )
    for attribute, value in selected.items():
        if attribute not in variant_options:
            frappe.throw(
                _(
                    "Tiny snag: this cart item's saved options no longer match this item. "
                    "Please choose the options again."
                ),
                frappe.ValidationError,
            )
        if str(value) != str(variant_options[attribute]):
            frappe.throw(
                _("Tiny snag: this cart item's saved options do not match the selected item. Please choose the options again."),
                frappe.ValidationError,
            )


def _validated_checkout_add_ons(
    client_configuration: dict[str, Any] | None,
    *,
    website_item_code: str | None,
) -> list[dict[str, Any]]:
    if not client_configuration:
        return []
    add_ons = client_configuration.get("add_ons") or []
    if not add_ons:
        return []
    if not isinstance(add_ons, list):
        frappe.throw(
            _("Tiny snag: this item's add-on details are not readable. Please choose the options again."),
            frappe.ValidationError,
        )

    normalized = []
    add_on_contracts = checkout_add_on_contracts_for_item(website_item_code)
    for raw in add_ons:
        if not isinstance(raw, dict):
            frappe.throw(
                _("Tiny snag: this item's add-on details are not readable. Please choose the options again."),
                frappe.ValidationError,
            )
        key = _add_on_key(raw)
        spec = add_on_contracts.get(key)
        if not spec and key in REVIEW_ONLY_SOURCE_ADD_ONS:
            frappe.throw(
                _(
                    "Tiny snag: this add-on needs a quote before checkout. "
                    "Please send it through the inquiry form so we price the upgrade correctly."
                ),
                frappe.ValidationError,
            )
        if not spec:
            frappe.log_error(
                f"Unknown add-on: {key or '(blank)'}",
                "LT product add-on checkout contract missing",
            )
            frappe.throw(
                _(
                    "Tiny snag: this add-on is not connected to checkout yet. "
                    "Please request a quote so we do not sell an upgrade incorrectly."
                ),
                frappe.ValidationError,
            )
        _assert_add_on_is_eligible(key, spec, website_item_code)
        value = _validated_add_on_value(spec, raw.get("value"))
        quantity = _add_on_quantity(raw.get("quantity"), value=value)
        quantity_min = int(spec.get("quantity_min") or 0)
        quantity_max = int(spec.get("quantity_max") or MAX_ADD_ON_QUANTITY)
        if quantity_min and quantity < quantity_min:
            frappe.throw(
                _(
                    "Tiny snag: this add-on needs a higher quantity before checkout. "
                    "Please choose the product options again."
                ),
                frappe.ValidationError,
            )
        if quantity > quantity_max:
            frappe.throw(
                _(
                    "Tiny snag: this add-on quantity is higher than this product allows. "
                    "Please choose the product options again."
                ),
                frappe.ValidationError,
            )
        normalized.append(
            {
                "key": key,
                "label": str(raw.get("label") or spec["label"]).strip() or spec["label"],
                "value": value,
                "quantity": quantity,
                "item_code": spec["item_code"],
            }
        )
    return normalized


def _validated_add_on_value(spec: dict[str, Any], value: Any) -> Any:
    if spec.get("input_type") != "digit_text":
        return value

    text = str(value or "").strip()
    quantity_max = int(spec.get("quantity_max") or MAX_ADD_ON_QUANTITY)
    if not re.fullmatch(rf"[0-9]{{1,{quantity_max}}}", text):
        frappe.throw(
            _(
                "Tiny snag: number foils need up to 3 digits, using only 0-9. "
                "Please choose the numbers again."
            ),
            frappe.ValidationError,
        )
    return text


def _validated_checkout_color_recipes(
    client_configuration: dict[str, Any] | None,
    *,
    variant_options: dict[str, str],
) -> list[dict[str, Any]]:
    recipes = _normalized_color_recipes(client_configuration or {})
    by_axis = {recipe["axis"]: recipe for recipe in recipes}
    required_axes = sorted(axis for axis in variant_options if is_balloon_color_axis(axis))
    missing = [axis for axis in required_axes if axis not in by_axis]
    if missing:
        frappe.throw(
            _(
                "Tiny snag: this product needs color choices saved as a color recipe before checkout. "
                "Please choose the colors again so we keep the details together."
            ),
            frappe.ValidationError,
        )
    mismatched = []
    for axis in required_axes:
        required_value = canonical_color_name(variant_options.get(axis))
        if required_value and required_value not in set(by_axis[axis].get("values") or []):
            mismatched.append(axis)
    if mismatched:
        frappe.throw(
            _(
                "Tiny snag: this cart item's saved color recipe no longer matches this item. "
                "Please choose the colors again so we keep the details together."
            ),
            frappe.ValidationError,
        )
    return recipes


def _normalized_color_recipes(configuration: dict[str, Any]) -> list[dict[str, Any]]:
    selected = configuration.get("selected_options") or {}
    if isinstance(selected, dict):
        selected_color_axes = sorted(axis for axis in selected if is_balloon_color_axis(axis))
        if selected_color_axes:
            frappe.throw(
                _(
                    "Tiny snag: color choices must be saved as a color recipe before checkout. "
                    "Please choose the colors again so we keep the details together."
                ),
                frappe.ValidationError,
            )
    elif selected not in (None, ""):
        frappe.throw(
            _("Tiny snag: this cart item's selected options are not readable. Please choose the options again."),
            frappe.ValidationError,
        )

    raw_recipes = configuration.get("color_recipes") or []
    if raw_recipes and not isinstance(raw_recipes, list):
        frappe.throw(
            _("Tiny snag: this item's color recipe is not readable. Please choose the colors again."),
            frappe.ValidationError,
        )

    recipe_rows = list(raw_recipes)
    customizations = configuration.get("customizations") or []
    if isinstance(customizations, dict):
        recipe_rows.extend(customizations.get("color_recipes") or [])
        customizations = customizations.get("items") or []
    if not isinstance(customizations, list):
        frappe.throw(
            _("Tiny snag: this item's custom option details are not readable. Please choose the options again."),
            frappe.ValidationError,
        )
    for row in customizations:
        if not isinstance(row, dict):
            continue
        axis = _clean_text(row.get("axis") or row.get("key") or row.get("source_axis"))
        if is_balloon_color_axis(axis):
            recipe_rows.append(row)

    normalized: dict[str, dict[str, Any]] = {}
    for row in recipe_rows:
        if not isinstance(row, dict):
            frappe.throw(
                _("Tiny snag: this item's color recipe is not readable. Please choose the colors again."),
                frappe.ValidationError,
            )
        axis = _clean_text(row.get("axis") or row.get("key") or row.get("source_axis"))
        if not is_balloon_color_axis(axis):
            frappe.throw(
                _("Tiny snag: this item's color recipe used an unknown color option. Please choose the colors again."),
                frappe.ValidationError,
            )
        values = _color_recipe_values(row)
        if not values:
            frappe.throw(
                _("Tiny snag: this item's color recipe needs at least one color. Please choose the colors again."),
                frappe.ValidationError,
            )
        if len(values) > MAX_COLOR_RECIPE_VALUES:
            frappe.throw(
                _("Tiny snag: this item's color recipe has too many colors for checkout. Please request a quote and we will help."),
                frappe.ValidationError,
            )
        normalized[axis] = {
            "axis": axis,
            "label": _clean_text(row.get("label")) or "Balloon color recipe",
            "values": values,
            "color_groups": grouped_colors(values),
            "status": "validated_for_checkout",
            "source": "lt_product_page_runtime",
        }
    return [normalized[axis] for axis in sorted(normalized)]


def _color_recipe_values(row: dict[str, Any]) -> list[str]:
    if "values" not in row:
        value = row.get("value")
        if isinstance(value, list):
            raw_values = value
        elif value in (None, ""):
            raw_values = []
        else:
            frappe.throw(
                _("Tiny snag: this item's color recipe must allow multiple colors. Please choose the colors again."),
                frappe.ValidationError,
            )
    else:
        raw_values = row.get("values")
    if not isinstance(raw_values, list):
        frappe.throw(
            _("Tiny snag: this item's color recipe must allow multiple colors. Please choose the colors again."),
            frappe.ValidationError,
        )
    values = [canonical_color_name(_clean_text(value)) for value in raw_values]
    return [value for value in values if value]


def _non_color_customizations(client_configuration: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not client_configuration:
        return []
    customizations = client_configuration.get("customizations") or []
    if isinstance(customizations, dict):
        customizations = customizations.get("items") or []
    if not isinstance(customizations, list):
        return [{"status": "invalid_customization_payload"}]
    result = []
    for row in customizations:
        if not isinstance(row, dict):
            result.append({"status": "invalid_customization_row"})
            continue
        axis = _clean_text(row.get("axis") or row.get("key") or row.get("source_axis"))
        if is_balloon_color_axis(axis):
            continue
        result.append(row)
    return result


def _configuration_groups_from_resolution(
    setup_resolution: dict[str, Any] | None,
    client_configuration: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if setup_resolution:
        groups = setup_resolution.get("configuration_groups") or []
        return [row for row in groups if isinstance(row, dict)]
    return _configuration_groups(client_configuration)


def _configuration_groups(client_configuration: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not client_configuration:
        return []
    raw = client_configuration.get("configuration_groups") or []
    if isinstance(raw, dict):
        raw = raw.get("items") or []
    if not isinstance(raw, list):
        return [{"status": "invalid_configuration_group_payload"}]

    result = []
    for row in raw:
        if not isinstance(row, dict):
            result.append({"status": "invalid_configuration_group_row"})
            continue
        key = _clean_text(row.get("key") or row.get("axis") or row.get("label"))
        label = _clean_text(row.get("label") or row.get("axis") or key)
        values = row.get("values")
        if values is None and row.get("value") not in (None, ""):
            values = [row.get("value")]
        if not isinstance(values, list):
            values = [values] if values not in (None, "") else []
        clean_values = [_clean_text(value) for value in values if _clean_text(value)]
        if key or label or clean_values:
            result.append(
                {
                    "key": key,
                    "label": label,
                    "values": clean_values,
                    "document_output": _clean_text(row.get("document_output")) or "Customer and operator",
                }
            )
    return result


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _add_on_key(raw: dict[str, Any]) -> str:
    for fieldname in ("key", "source_attribute", "label"):
        candidate = raw.get(fieldname)
        if candidate:
            break
    else:
        candidate = ""
    key = _canonical_add_on_key(candidate)
    return ADD_ON_KEY_ALIASES.get(key, key)


def _canonical_add_on_key(value: Any) -> str:
    text = str(value or "").strip().lower().replace("-", " ").replace("/", " ")
    parts = [part for part in text.split() if part]
    return "_".join(parts)


def _assert_add_on_is_eligible(key: str, spec: dict[str, Any], website_item_code: str | None) -> None:
    eligible = tuple(spec.get("eligible_website_item_codes") or ())
    if not eligible:
        return
    if str(website_item_code or "").strip() in eligible:
        return
    frappe.throw(
        _(
            "Tiny snag: this add-on is not available for this product. "
            "Please choose the product options again so we do not attach the wrong upgrade."
        ),
        frappe.ValidationError,
    )


def _add_on_quantity(raw_quantity: Any, *, value: Any) -> int:
    derived = _selected_number_count(value)
    quantity = None
    if raw_quantity not in (None, ""):
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            frappe.throw(
                _("Tiny snag: this add-on quantity is not readable. Please choose the options again."),
                frappe.ValidationError,
            )
    if quantity is None:
        quantity = derived
    if quantity < 1:
        frappe.throw(
            _("Tiny snag: this add-on quantity needs to be at least 1. Please choose the options again."),
            frappe.ValidationError,
        )
    if derived and quantity < derived:
        quantity = derived
    if quantity > MAX_ADD_ON_QUANTITY:
        frappe.throw(
            _("Tiny snag: this add-on has too many selected numbers for checkout. Please request a quote and we will help."),
            frappe.ValidationError,
        )
    return quantity


def _selected_number_count(value: Any) -> int:
    if isinstance(value, list):
        return len([entry for entry in value if str(entry or "").strip()])
    if isinstance(value, dict):
        return len([entry for entry in value.values() if str(entry or "").strip()])
    text = str(value or "").strip()
    if not text:
        return 0
    digit_count = sum(1 for char in text if char.isdigit())
    return digit_count or 1


def _variant_options_dict(rows: list[dict[str, Any]]) -> dict[str, str]:
    options: dict[str, str] = {}
    for row in rows:
        attribute = row.get("attribute")
        value = row.get("attribute_value")
        if attribute and value:
            options[str(attribute)] = str(value)
    return options


def _configuration_summary(payload: dict[str, Any]) -> str:
    pieces = []
    if payload.get("selected_options"):
        options = ", ".join(
            f"{attribute}: {value}"
            for attribute, value in sorted(payload["selected_options"].items())
        )
        pieces.append(f"Options - {options}")
    if payload.get("add_ons"):
        pieces.append("Add-ons preserved in structured payload")
    if payload.get("color_recipes"):
        pieces.append("Color recipe preserved in structured payload")
    if payload.get("configuration_groups"):
        group_bits = []
        for row in payload.get("configuration_groups") or []:
            if not isinstance(row, dict):
                continue
            label = row.get("label") or row.get("key")
            values = ", ".join(str(value) for value in row.get("values") or [] if str(value or "").strip())
            if label and values:
                group_bits.append(f"{label}: {values}")
        if group_bits:
            pieces.append("Configured choices - " + "; ".join(group_bits))
        else:
            pieces.append("Configured choices preserved in structured payload")
    if payload.get("customizations"):
        pieces.append("Customizations preserved in structured payload")
    selected_content = payload.get("selected_content") or {}
    if isinstance(selected_content, dict) and selected_content.get("display_title"):
        pieces.append(f"Selected copy - {selected_content.get('display_title')}")
    if not pieces:
        pieces.append("No extra product options")
    pieces.append(f"Page type - {payload.get('product_page_type')}")
    return "; ".join(pieces)


def _add_on_summary(payload: dict[str, Any]) -> str:
    value = payload.get("selected_value")
    value_piece = f": {value}" if value not in (None, "") else ""
    return (
        f"Add-on - {payload.get('add_on_label')}{value_piece}; "
        f"Parent item - {payload.get('parent_item_code')}; "
        f"Qty per product - {payload.get('quantity_per_parent')}"
    )


def _known_or_empty(value: Any, allowed: tuple[str, ...]) -> str:
    value = str(value or "").strip()
    return value if value in allowed else ""


def customer_facing_line_label(item: Any) -> str:
    """Return a receipt/payment label that preserves chosen add-on details."""
    base_name = _row_get(item, "item_name") or _row_get(item, "item_code")
    payload = _row_payload(item)
    if payload.get("source") == "lt_product_page_add_on":
        label = str(payload.get("add_on_label") or base_name or "").strip()
        value = payload.get("selected_value")
        if value not in (None, ""):
            return f"{label}: {value}"
        return label or str(base_name or "").strip()

    selected_content = payload.get("selected_content") or {}
    if isinstance(selected_content, dict):
        display_title = str(selected_content.get("display_title") or "").strip()
        if display_title:
            return display_title

    summary = str(_row_get(item, LINE_FIELDNAMES["summary"]) or "").strip()
    if summary.startswith("Add-on - "):
        first_piece = summary.split(";", 1)[0].replace("Add-on - ", "", 1).strip()
        if first_piece and "Parent item" not in first_piece:
            return first_piece
    return str(base_name or "").strip()


def customer_facing_line_image(item: Any) -> str:
    """Return the customer-facing image chosen by Product Setup, if present."""
    payload = _row_payload(item)
    selected_media = payload.get("selected_media") or {}
    image = selected_media.get("image") if isinstance(selected_media, dict) else ""
    return str(image or "").strip()


def _row_get(row: Any, fieldname: str) -> Any:
    if hasattr(row, "get"):
        return row.get(fieldname)
    return getattr(row, fieldname, None)


def _row_payload(row: Any) -> dict[str, Any]:
    try:
        return json.loads(_row_get(row, LINE_FIELDNAMES["json"]) or "{}")
    except (TypeError, ValueError):
        return {}


def _contains_internal_marker(text: str) -> bool:
    return any(marker in text for marker in _CUSTOMER_UNSAFE_MARKERS)
