"""Verify LT product-page runtime storage and checkout preservation.

This uses fake/proof catalog data only. It proves the reusable architecture:
page type fields exist, cart configuration is versioned, Sales Order lines
preserve selected meaning, invoices receive the same payload, and quote-first
pages cannot slip into paid checkout.
"""
from __future__ import annotations

import json
import time

import frappe
from frappe.utils import add_days, flt, nowdate

from locally_twisted.product_page_labels import (
    COMMERCE_LANE_LABELS,
    COMMERCE_LANE_OPTIONS,
    PRODUCT_PAGE_TYPE_LABELS,
    PRODUCT_PAGE_TYPE_OPTIONS,
)
from locally_twisted.product_page_runtime import CONFIG_VERSION, LINE_FIELDNAMES
from locally_twisted.product_quote_runtime import QUOTATION_FIELDNAMES


PROOF_ITEM = "unicorn-bouquet-SMA"
PRICE_LIST = "Standard Selling"
FOIL_NUMBER_ADD_ON_ITEM = "ADDON-FOIL-NUMBER"
FOIL_NUMBER_ADD_ON_RATE = 12.0


class ContractFail(Exception):
    pass


def run():
    original_commit = frappe.db.commit
    intercepted_commits = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    try:
        frappe.db.commit = no_commit
        result = _run_contract()
        result["commit_calls_intercepted"] = len(intercepted_commits)
        result["rolled_back"] = True
        return result
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        frappe.db.rollback()


def _run_contract():
    _assert_schema()
    _assert_plain_template_labels()
    _assert_customer_safe_setup_errors_strip_internal_details()
    _assert_live_runtime_contracts_match_proof_source()
    _assert_product_page_add_on_options_are_eligible()
    resolved_item, line = _assert_line_resolution_preserves_configuration()
    _assert_multi_color_checkout_configuration_preserved()
    _assert_generic_product_setup_configuration_preserved()
    add_on_lines = _assert_foil_number_add_on_becomes_priced_line(resolved_item)
    sales_order = _assert_sales_order_accepts_line(line)
    add_on_sales_order = _assert_sales_order_accepts_lines(add_on_lines)
    invoice_name = _assert_invoice_copy(sales_order.name)
    add_on_invoice_name = _assert_invoice_copy(add_on_sales_order.name)
    _assert_quote_first_blocks_checkout(resolved_item)
    _assert_quote_first_payload_requires_real_details(resolved_item)
    lead_name = _assert_lead_product_quote_handoff(resolved_item)
    quotation_name = _assert_product_quote_lead_creates_draft_quotation(lead_name)
    _assert_product_quote_configuration_can_copy_to_sales_order(quotation_name)
    _assert_product_quote_packet_surfaces_payload(quotation_name)
    _assert_bad_cart_configuration_fails_loudly()
    return {
        "ok": True,
        "proof_item": PROOF_ITEM,
        "lead": lead_name,
        "quotation": quotation_name,
        "sales_order": sales_order.name,
        "add_on_sales_order": add_on_sales_order.name,
        "sales_invoice": invoice_name,
        "add_on_sales_invoice": add_on_invoice_name,
        "line_fields": sorted(LINE_FIELDNAMES.values()),
        "schema_version": CONFIG_VERSION,
    }


def _assert_customer_safe_setup_errors_strip_internal_details() -> None:
    from locally_twisted.product_page_runtime import customer_safe_checkout_error

    unsafe_messages = [
        "Tiny snag: this add-on is not set up for checkout yet. Missing Item: ADDON-FOIL-NUMBER",
        "Tiny snag: checkout option storage is not installed. Missing Sales Order Item fields: custom_lt_configuration_json",
        "Tiny snag: this add-on is not available for this product. Add-on: foil_number",
        "Tiny snag: this add-on is not connected to checkout yet. Unknown add-on: secret_addon",
    ]
    for message in unsafe_messages:
        safe = customer_safe_checkout_error(message)
        for marker in ("ADDON-", "custom_lt_", "Missing Item", "Missing Sales", "Unknown add-on", "Add-on:"):
            if marker in safe:
                raise ContractFail(f"customer-safe checkout error leaked internal marker {marker!r}: {safe!r}")
        if "Tiny snag" not in safe:
            raise ContractFail(f"customer-safe checkout error lost branded failure voice: {safe!r}")


def _assert_live_runtime_contracts_match_proof_source() -> None:
    from locally_twisted.product_page_runtime import product_page_contract_for_website_item

    expected = {
        "unicorn-bouquet": ("simple_product", "checkout"),
        "classic-arch": ("complex_custom_product", "checkout"),
    }
    for website_item_code, (page_type, commerce_lane) in expected.items():
        contract = product_page_contract_for_website_item(website_item_code)
        actual = (contract.get("product_page_type"), contract.get("commerce_lane"))
        if actual != (page_type, commerce_lane):
            raise ContractFail(
                f"{website_item_code} live runtime contract should be {page_type}/{commerce_lane}, found {actual}"
            )


def _assert_schema() -> None:
    expected = {
        "Website Item": {"lt_product_page_type", "lt_commerce_lane"},
        "Lead": {
            "custom_lt_product_template_item",
            "custom_lt_product_page_type",
            "custom_lt_product_quote_summary",
            "custom_lt_product_quote_payload",
            "custom_lt_product_quote_items",
        },
        "Sales Order Item": set(LINE_FIELDNAMES.values()),
        "Sales Invoice Item": set(LINE_FIELDNAMES.values()),
        "Quotation": set(QUOTATION_FIELDNAMES.values()),
        "Quotation Item": set(LINE_FIELDNAMES.values()),
    }
    for doctype, fieldnames in expected.items():
        meta = frappe.get_meta(doctype)
        missing = sorted(field for field in fieldnames if not meta.has_field(field))
        if missing:
            raise ContractFail(f"{doctype} missing LT product-page runtime fields: {missing}")
    if not frappe.db.exists("DocType", "LT Product Quote Item"):
        raise ContractFail("missing LT Product Quote Item child DocType")


def _assert_plain_template_labels() -> None:
    missing_type_labels = sorted(value for value in PRODUCT_PAGE_TYPE_OPTIONS if value not in PRODUCT_PAGE_TYPE_LABELS)
    missing_lane_labels = sorted(value for value in COMMERCE_LANE_OPTIONS if value not in COMMERCE_LANE_LABELS)
    if missing_type_labels:
        raise ContractFail(f"product-page type labels missing: {missing_type_labels}")
    if missing_lane_labels:
        raise ContractFail(f"commerce lane labels missing: {missing_lane_labels}")
    raw_label_markers = {"simple_product", "complex_custom_product", "quote_first", "needs_review"}
    for label in [*PRODUCT_PAGE_TYPE_LABELS.values(), *COMMERCE_LANE_LABELS.values()]:
        if any(marker in label for marker in raw_label_markers):
            raise ContractFail(f"product-page template label is not operator/customer safe: {label}")
    expected_custom_field_labels = {
        ("Website Item", "lt_product_page_type"): "Page Template",
        ("Website Item", "lt_commerce_lane"): "Buying Path",
        ("Quotation", QUOTATION_FIELDNAMES["page_type"]): "Page Template",
        ("Quotation", QUOTATION_FIELDNAMES["commerce_lane"]): "Buying Path",
        ("Sales Order Item", LINE_FIELDNAMES["page_type"]): "Product Page Template",
        ("Sales Invoice Item", LINE_FIELDNAMES["page_type"]): "Product Page Template",
        ("Quotation Item", LINE_FIELDNAMES["page_type"]): "Product Page Template",
    }
    for (doctype, fieldname), expected_label in expected_custom_field_labels.items():
        actual = frappe.get_meta(doctype).get_field(fieldname).label
        if actual != expected_label:
            raise ContractFail(f"{doctype}.{fieldname} label should be {expected_label!r}, found {actual!r}")


def _assert_product_page_add_on_options_are_eligible() -> None:
    from locally_twisted.product_options import get_checkout_add_on_options

    website_item_name = frappe.db.get_value("Website Item", {"item_code": "unicorn-bouquet"}, "name")
    if not website_item_name:
        raise ContractFail("missing Website Item for unicorn-bouquet add-on option check")
    frappe.db.set_value(
        "Website Item",
        website_item_name,
        {
            "lt_product_page_type": "simple_product",
            "lt_commerce_lane": "checkout",
        },
        update_modified=False,
    )
    eligible = get_checkout_add_on_options("unicorn-bouquet")
    if not eligible:
        raise ContractFail("eligible ready-to-order product did not expose checkout add-on options")
    foil = next((row for row in eligible if row.get("key") == "foil_number"), None)
    if not foil:
        raise ContractFail(f"unicorn-bouquet add-on options did not include foil_number: {eligible}")
    if foil.get("label") != "Foil number" or float(foil.get("unit_price") or 0) != FOIL_NUMBER_ADD_ON_RATE:
        raise ContractFail(f"foil_number add-on option did not preserve label/price: {foil}")
    ineligible = get_checkout_add_on_options("mothers-day-bouquet")
    if ineligible:
        raise ContractFail(f"ineligible product should not expose add-on options: {ineligible}")


def _assert_line_resolution_preserves_configuration():
    from locally_twisted.api.cart import resolve_cart_item_for_sale
    from locally_twisted.www.checkout import _resolve_sale_lines

    initial_resolved = resolve_cart_item_for_sale(PROOF_ITEM, raise_on_missing=True)
    configuration = _configuration_payload(PROOF_ITEM, initial_resolved.get("variant_options") or [])
    resolved = resolve_cart_item_for_sale(
        PROOF_ITEM,
        raise_on_missing=True,
        configuration=configuration,
    )
    if resolved.get("configuration", {}).get("schema_version") != CONFIG_VERSION:
        raise ContractFail("cart resolver did not preserve versioned configuration")

    lines, resolved_items = _resolve_sale_lines(
        [{"item_code": PROOF_ITEM, "qty": 1, "configuration": configuration}]
    )
    if len(lines) != 1 or len(resolved_items) != 1:
        raise ContractFail("checkout resolver should return exactly one proof line")
    line = lines[0]
    for fieldname in LINE_FIELDNAMES.values():
        if not line.get(fieldname):
            raise ContractFail(f"Sales Order line missing runtime field {fieldname}")

    payload = json.loads(line[LINE_FIELDNAMES["json"]])
    expected_options = _variant_options_dict(initial_resolved.get("variant_options") or [])
    for attribute, value in expected_options.items():
        if payload.get("selected_options", {}).get(attribute) != value:
            raise ContractFail(
                f"line payload should preserve {attribute}={value}, found {payload.get('selected_options')}"
            )
    if payload.get("schema_version") != CONFIG_VERSION:
        raise ContractFail("line payload has wrong schema version")
    return resolved, line


def _assert_multi_color_checkout_configuration_preserved() -> None:
    from locally_twisted.product_page_runtime import cart_line_key, sales_order_line_configuration_fields

    resolved_item = {
        "item_code": PROOF_ITEM,
        "website_item_code": "unicorn-bouquet",
        "variant_options": [
            {"attribute": "Bouquet Size", "attribute_value": "Small"},
            {"attribute": "latex colors", "attribute_value": "White"},
        ],
    }
    configuration = {
        "schema_version": CONFIG_VERSION,
        "item_code": PROOF_ITEM,
        "website_item_code": "unicorn-bouquet",
        "selected_options": {"Bouquet Size": "Small"},
        "color_recipes": [
            {"axis": "latex colors", "values": ["White", "Reflex Champage", "Blue slate", "Smoke grey"]}
        ],
        "add_ons": [],
        "customizations": [],
    }
    line = sales_order_line_configuration_fields(
        resolved_item=resolved_item,
        client_configuration=configuration,
    )
    payload = json.loads(line[LINE_FIELDNAMES["json"]])
    if payload.get("selected_options", {}).get("latex colors"):
        raise ContractFail(f"multi-color checkout preserved color as selected_options: {payload}")
    recipes = payload.get("color_recipes") or []
    if not recipes or recipes[0].get("values") != ["White", "Reflex Champagne", "Blue Slate", "Smoke Grey"]:
        raise ContractFail(f"multi-color checkout did not preserve color recipe: {payload}")
    if "Color recipe preserved" not in line.get(LINE_FIELDNAMES["summary"], ""):
        raise ContractFail("Sales Order summary did not surface color recipe preservation")

    changed_configuration = dict(configuration)
    changed_configuration["color_recipes"] = [{"axis": "latex colors", "values": ["White", "Reflex Champagne", "Black"]}]
    if cart_line_key(PROOF_ITEM, configuration) == cart_line_key(PROOF_ITEM, changed_configuration):
        raise ContractFail("cart line key did not include color_recipes")

    missing_recipe = dict(configuration)
    missing_recipe["color_recipes"] = []
    try:
        sales_order_line_configuration_fields(
            resolved_item=resolved_item,
            client_configuration=missing_recipe,
        )
    except frappe.ValidationError as exc:
        if "color choices saved as a color recipe" not in str(exc):
            raise ContractFail(f"missing color recipe failed with wrong message: {exc}") from exc
    else:
        raise ContractFail("checkout accepted color variant without a color recipe")

    single_select = dict(configuration)
    single_select["selected_options"] = {"Bouquet Size": "Small", "latex colors": "White"}
    try:
        sales_order_line_configuration_fields(
            resolved_item=resolved_item,
            client_configuration=single_select,
        )
    except frappe.ValidationError as exc:
        if "color choices must be saved as a color recipe" not in str(exc):
            raise ContractFail(f"single-select color failed with wrong message: {exc}") from exc
    else:
        raise ContractFail("checkout accepted single-select color as selected_options")


def _assert_generic_product_setup_configuration_preserved() -> None:
    from locally_twisted.api.product_setup import get_product_setup_schema, resolve_product_setup
    from locally_twisted.api.variant_media import get_variant_media
    from locally_twisted.product_page_runtime import sales_order_line_configuration_fields

    blueprint_name = f"lt-runtime-generic-proof-{int(time.time())}"
    blueprint = frappe.get_doc(
        {
            "doctype": "LT Product Blueprint",
            "product_name": "LT Runtime Generic Proof",
            "product_slug": blueprint_name,
            "item_group": "Bouquets",
            "page_template": "Ready-to-order page",
            "buying_path": "Direct checkout",
            "publish_status": "Local Preview Ready",
            "base_price": 35,
            "target_item_code": "unicorn-bouquet",
            "option_rows": [
                {
                    "axis_name": "Bouquet Size",
                    "selection_behavior": "SKU-defining variant",
                    "control_type": "Single select",
                    "required": 1,
                    "values": "Small\nMedium",
                },
                {
                    "axis_name": "Design Choices",
                    "selection_behavior": "Configuration only",
                    "control_type": "Multi select",
                    "required": 1,
                    "min_selections": 1,
                    "max_selections": 3,
                    "values": "Ribbon\nCard\nCharm",
                },
            ],
            "media_rule_rows": [
                {
                    "rule_name": "Ribbon image",
                    "rule_type": "Selection group",
                    "selection_group": "Design Choices",
                    "selection_value": "Ribbon",
                    "image": "/files/lt-product-setup-media-proof.png",
                    "approved_for_customer": 1,
                }
            ],
        }
    )
    blueprint.insert(ignore_permissions=True)
    try:
        resolved_item = {
            "item_code": PROOF_ITEM,
            "website_item_code": "unicorn-bouquet",
            "variant_options": [{"attribute": "Bouquet Size", "attribute_value": "Small"}],
        }
        configuration = {
            "schema_version": CONFIG_VERSION,
            "item_code": PROOF_ITEM,
            "website_item_code": "unicorn-bouquet",
            "selected_options": {"bouquet-size": "Small"},
            "configuration_groups": [
                {
                    "key": "design-choices",
                    "label": "Design Choices",
                    "values": ["Ribbon", "Card"],
                    "document_output": "Customer and operator",
                }
            ],
            "add_ons": [],
            "customizations": [],
        }
        api_schema = get_product_setup_schema("unicorn-bouquet")
        if api_schema.get("source") != "lt_product_setup":
            raise ContractFail(f"generic Product Setup API returned wrong schema source: {api_schema}")
        api_resolution = resolve_product_setup("unicorn-bouquet", json.dumps(configuration))
        if not api_resolution.get("ok"):
            raise ContractFail(f"generic Product Setup API rejected valid configuration: {api_resolution}")
        media = get_variant_media(PROOF_ITEM, "unicorn-bouquet", json.dumps(configuration))
        if media.get("media_role") != "product_setup_media_rule":
            raise ContractFail(f"approved Product Setup media rule did not drive variant media: {media}")
        line = sales_order_line_configuration_fields(
            resolved_item=resolved_item,
            client_configuration=configuration,
        )
        payload = json.loads(line[LINE_FIELDNAMES["json"]])
        groups = payload.get("configuration_groups") or []
        if groups != configuration["configuration_groups"]:
            raise ContractFail(f"generic Product Setup configuration was not preserved: {payload}")
        if "Design Choices" not in line.get(LINE_FIELDNAMES["summary"], ""):
            raise ContractFail("Sales Order summary did not surface generic Product Setup configuration")

        too_many = dict(configuration)
        too_many["configuration_groups"] = [
            {
                "key": "design-choices",
                "label": "Design Choices",
                "values": ["Ribbon", "Card", "Charm", "Extra"],
                "document_output": "Customer and operator",
            }
        ]
        try:
            sales_order_line_configuration_fields(
                resolved_item=resolved_item,
                client_configuration=too_many,
            )
        except frappe.ValidationError as exc:
            if "needs review before checkout" not in str(exc):
                raise ContractFail(f"too-many generic selections failed with wrong message: {exc}") from exc
        else:
            raise ContractFail("checkout accepted too many Product Setup configuration selections")
    finally:
        frappe.delete_doc("LT Product Blueprint", blueprint.name, force=True, ignore_permissions=True)


def _assert_foil_number_add_on_becomes_priced_line(resolved_item: dict):
    from locally_twisted.www.checkout import _resolve_sale_lines

    configuration = _configuration_payload(
        PROOF_ITEM,
        resolved_item.get("variant_options") or [],
        add_ons=[
            {
                "key": "foil_number",
                "label": "Foil number",
                "value": "5",
                "quantity": 1,
            }
        ],
    )
    try:
        lines, resolved_items = _resolve_sale_lines(
            [{"item_code": PROOF_ITEM, "qty": 1, "configuration": configuration}]
        )
    except frappe.ValidationError as exc:
        raise ContractFail(f"confirmed foil-number add-on should become a priced line, but checkout rejected it: {exc}")

    if len(lines) != 2:
        raise ContractFail(f"foil-number add-on checkout should create 2 Sales Order lines, found {len(lines)}")
    if len(resolved_items) != 2:
        raise ContractFail(f"foil-number add-on checkout should return 2 resolved display lines, found {len(resolved_items)}")

    base_line, add_on_line = lines
    if base_line.get("item_code") != PROOF_ITEM:
        raise ContractFail(f"first line should stay the selected product item, found {base_line.get('item_code')}")
    if add_on_line.get("item_code") != FOIL_NUMBER_ADD_ON_ITEM:
        raise ContractFail(f"second line should be {FOIL_NUMBER_ADD_ON_ITEM}, found {add_on_line.get('item_code')}")
    if flt(add_on_line.get("rate")) != FOIL_NUMBER_ADD_ON_RATE:
        raise ContractFail(f"foil-number add-on rate should be {FOIL_NUMBER_ADD_ON_RATE}, found {add_on_line.get('rate')}")

    base_payload = json.loads(base_line[LINE_FIELDNAMES["json"]])
    add_on_payload = json.loads(add_on_line[LINE_FIELDNAMES["json"]])
    if not base_payload.get("add_ons"):
        raise ContractFail("base line payload should preserve selected add-ons")
    if "unit_price" in base_payload["add_ons"][0]:
        raise ContractFail("base line add-on payload should not carry static unit_price; ERPNext Item Price owns price truth")
    if add_on_payload.get("source") != "lt_product_page_add_on":
        raise ContractFail(f"add-on line payload source is wrong: {add_on_payload}")
    if add_on_payload.get("parent_item_code") != PROOF_ITEM:
        raise ContractFail(f"add-on line payload should link back to proof item: {add_on_payload}")
    return lines


def _assert_sales_order_accepts_line(line):
    return _assert_sales_order_accepts_lines([line])


def _assert_sales_order_accepts_lines(lines):
    customer = _create_customer()
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
    sales_order.insert(ignore_permissions=True)
    sales_order.submit()
    for stored in sales_order.items:
        if stored.get(LINE_FIELDNAMES["version"]) != CONFIG_VERSION:
            raise ContractFail("submitted Sales Order Item did not retain configuration version")
    return sales_order


def _assert_invoice_copy(sales_order_name: str) -> str:
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    from locally_twisted.product_page_runtime import copy_sales_order_line_configuration_to_invoice

    invoice = make_sales_invoice(sales_order_name, ignore_permissions=True)
    invoice.flags.ignore_permissions = True
    invoice.flags.mute_email = True
    invoice.set_missing_values()
    copy_sales_order_line_configuration_to_invoice(invoice, sales_order_name)
    invoice.insert(ignore_permissions=True)
    invoice.submit()

    for invoice_row in invoice.items:
        for fieldname in LINE_FIELDNAMES.values():
            if not invoice_row.get(fieldname):
                raise ContractFail(f"Sales Invoice Item did not receive {fieldname} for {invoice_row.item_code}")
    return invoice.name


def _assert_quote_first_blocks_checkout(resolved_item: dict) -> None:
    from locally_twisted.www.checkout import _resolve_sale_lines

    website_item_code = resolved_item.get("website_item_code")
    website_item_name = frappe.db.get_value("Website Item", {"item_code": website_item_code}, "name")
    if not website_item_name:
        raise ContractFail(f"missing Website Item for proof template {website_item_code}")

    frappe.db.set_value(
        "Website Item",
        website_item_name,
        {
            "lt_product_page_type": "complex_custom_product",
            "lt_commerce_lane": "quote_first",
        },
        update_modified=False,
    )

    try:
        _resolve_sale_lines(
            [
                {
                    "item_code": PROOF_ITEM,
                    "qty": 1,
                    "configuration": _configuration_payload(
                        PROOF_ITEM,
                        resolved_item.get("variant_options") or [],
                    ),
                }
            ]
        )
    except frappe.ValidationError as exc:
        if "needs a quote" not in str(exc):
            raise ContractFail(f"quote-first rejection had unexpected message: {exc}")
        return
    raise ContractFail("quote-first product page type did not block paid checkout")


def _assert_quote_first_payload_requires_real_details(resolved_item: dict) -> None:
    from locally_twisted.www.book import _requested_product_quote_payload

    website_item_code = resolved_item.get("website_item_code")
    incoming_payload = {
        "schema_version": CONFIG_VERSION,
        "source": "product-page-quote-form",
        "website_item_code": website_item_code,
        "web_item_name": "Unicorn Bouquet",
        "product_page_type": "complex_custom_product",
        "commerce_lane": "quote_first",
        "selected_options": {
            "Arch Size": "20ft",
            "LED Lights": "No Lights",
        },
        "add_ons": [
            {
                "key": "strike",
                "label": "Strike after event",
                "value": "Yes",
                "quantity": 1,
            }
        ],
        "customizations": [
            {
                "key": "color_notes",
                "label": "Color notes",
                "value": "Reflex Gold, White, and Navy",
            },
            {
                "key": "design_notes",
                "label": "Design notes",
                "value": "Frame the stage entrance.",
            },
        ],
        "needs_operator_review": True,
    }
    payload = _requested_product_quote_payload(website_item_code, json.dumps(incoming_payload))
    expected_summary_parts = [
        "Requested product page quote: Unicorn Bouquet",
        "Arch Size: 20ft",
        "LED Lights: No Lights",
        "Strike after event: Yes",
        "Color notes: Reflex Gold, White, and Navy",
        "Design notes: Frame the stage entrance.",
    ]
    summary = payload.get("summary") or ""
    for part in expected_summary_parts:
        if part not in summary:
            raise ContractFail(f"quote-first payload summary dropped detail {part!r}: {summary!r}")
    if payload.get("selected_options") != incoming_payload["selected_options"]:
        raise ContractFail(f"quote-first payload dropped selected options: {payload}")
    if payload.get("add_ons") != incoming_payload["add_ons"]:
        raise ContractFail(f"quote-first payload dropped add-ons: {payload}")
    if payload.get("customizations") != incoming_payload["customizations"]:
        raise ContractFail(f"quote-first payload dropped customizations: {payload}")

    bad_payload = dict(incoming_payload)
    bad_payload["selected_options"] = ["not", "a", "dict"]
    try:
        _requested_product_quote_payload(website_item_code, json.dumps(bad_payload))
    except frappe.ValidationError as exc:
        if "product quote options" not in str(exc):
            raise ContractFail(f"bad quote options failed with unexpected message: {exc}")
    else:
        raise ContractFail("bad quote-first selected_options should fail loudly")

    stale_payload = dict(incoming_payload)
    stale_payload["commerce_lane"] = "checkout"
    try:
        _requested_product_quote_payload(website_item_code, json.dumps(stale_payload))
    except frappe.ValidationError as exc:
        if "different buying path" not in str(exc):
            raise ContractFail(f"stale quote lane failed with unexpected message: {exc}")
    else:
        raise ContractFail("stale quote-first commerce lane should fail loudly")


def _assert_bad_cart_configuration_fails_loudly() -> None:
    from locally_twisted.product_page_runtime import normalize_client_configuration

    try:
        normalize_client_configuration({"schema_version": "old-version"})
    except frappe.ValidationError as exc:
        if "older option format" not in str(exc):
            raise ContractFail(f"old cart schema failed with unexpected message: {exc}")
        return
    raise ContractFail("old cart schema should fail loudly")


def _assert_lead_product_quote_handoff(resolved_item: dict) -> str:
    from locally_twisted.www.book import (
        _lead_product_quote_child_rows,
        _lead_product_quote_fields,
        _requested_product_quote_payload,
    )

    website_item_code = resolved_item.get("website_item_code")
    incoming_payload = {
        "schema_version": CONFIG_VERSION,
        "source": "product-page-quote-form",
        "website_item_code": website_item_code,
        "selected_options": {"Arch Size": "20ft", "LED Lights": "No Lights"},
        "add_ons": [],
        "customizations": [{"axis": "latex colors", "values": ["Reflex Gold", "White"]}],
        "summary": "Requested product page quote with preserved options",
        "needs_operator_review": True,
    }
    payload = _requested_product_quote_payload(website_item_code, json.dumps(incoming_payload))
    if not payload:
        raise ContractFail("product-page quote payload helper returned nothing")
    if payload.get("commerce_lane") != "quote_first":
        raise ContractFail(f"product-page quote payload should preserve quote_first lane, found {payload}")
    if payload.get("selected_options") != incoming_payload["selected_options"]:
        raise ContractFail(f"product-page quote payload dropped selected options: {payload}")
    if payload.get("customizations") != incoming_payload["customizations"]:
        raise ContractFail(f"product-page quote payload dropped customizations: {payload}")
    color_recipes = payload.get("color_recipes") or []
    if not color_recipes or color_recipes[0].get("values") != ["Reflex Gold", "White"]:
        raise ContractFail(f"product-page quote payload did not create structured color recipes: {payload}")

    fields = _lead_product_quote_fields(payload)
    child_rows = _lead_product_quote_child_rows(payload)
    required_fields = {
        "custom_lt_product_template_item",
        "custom_lt_product_page_type",
        "custom_lt_product_quote_summary",
        "custom_lt_product_quote_payload",
    }
    missing = sorted(required_fields - set(fields))
    if missing:
        raise ContractFail(f"Lead product quote helper did not return fields: {missing}")
    if not child_rows:
        raise ContractFail("Lead product quote helper did not return child rows")

    token = str(int(time.time()))
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": f"LT Product Quote Contract {token}",
            "email_id": f"lt-product-quote-{token}@example.invalid",
            "source": "Website",
            "status": "Open",
            **fields,
            "custom_lt_product_quote_items": child_rows,
        }
    )
    lead.insert(ignore_permissions=True)
    stored = frappe.get_doc("Lead", lead.name)
    if stored.get("custom_lt_product_template_item") != website_item_code:
        raise ContractFail("Lead did not preserve requested product page item")
    quote_payload = stored.get("custom_lt_product_quote_payload") or ""
    if "product-page-quote-form" not in quote_payload:
        raise ContractFail("Lead did not preserve product-page quote payload JSON")
    stored_payload = json.loads(quote_payload)
    if not stored_payload.get("color_recipes"):
        raise ContractFail("Lead did not preserve structured color recipes")
    if len(stored.get("custom_lt_product_quote_items") or []) != 1:
        raise ContractFail("Lead did not preserve product-page quote child row")
    child = stored.get("custom_lt_product_quote_items")[0]
    if child.product_page != website_item_code or child.status != "Draft Quotation Created":
        raise ContractFail("Lead product quote child row did not preserve product/draft status")
    quotation_name = frappe.db.get_value(
        "Quotation",
        {QUOTATION_FIELDNAMES["source_lead"]: stored.name, "docstatus": 0},
        "name",
    )
    if not quotation_name:
        raise ContractFail("product-page quote Lead did not cascade to an internal draft Quotation")
    return lead.name


def _assert_product_quote_lead_creates_draft_quotation(lead_name: str) -> str:
    from locally_twisted.product_quote_runtime import create_product_page_draft_quotation_from_lead

    quotation = create_product_page_draft_quotation_from_lead(lead_name)
    if quotation.doctype != "Quotation":
        raise ContractFail(f"product quote helper returned wrong doctype: {quotation.doctype}")
    if quotation.docstatus != 0:
        raise ContractFail("product quote helper must create a draft Quotation only")
    if quotation.quotation_to != "Lead" or quotation.party_name != lead_name:
        raise ContractFail(
            f"draft Quotation should point to source Lead {lead_name}, found {quotation.quotation_to}/{quotation.party_name}"
        )
    if quotation.get(QUOTATION_FIELDNAMES["source_lead"]) != lead_name:
        raise ContractFail("draft Quotation did not preserve source Lead link")
    if quotation.get(QUOTATION_FIELDNAMES["version"]) != CONFIG_VERSION:
        raise ContractFail("draft Quotation did not preserve product quote schema version")
    if quotation.get(QUOTATION_FIELDNAMES["status"]) != "Draft Quotation Created":
        raise ContractFail("draft Quotation did not expose operator quote status")
    if not quotation.items:
        raise ContractFail("draft Quotation should contain the requested product-page line")

    item = quotation.items[0]
    for fieldname in LINE_FIELDNAMES.values():
        if not item.get(fieldname):
            raise ContractFail(f"Quotation Item did not preserve {fieldname}")
    payload = json.loads(item.get(LINE_FIELDNAMES["json"]))
    if payload.get("source") != "lt_product_page_quote_runtime":
        raise ContractFail(f"Quotation Item payload source is wrong: {payload}")
    if payload.get("schema_version") != CONFIG_VERSION:
        raise ContractFail("Quotation Item payload has wrong schema version")

    second = create_product_page_draft_quotation_from_lead(lead_name)
    if second.name != quotation.name:
        raise ContractFail("product quote helper should be idempotent and reuse the draft Quotation")
    return quotation.name


def _assert_product_quote_configuration_can_copy_to_sales_order(quotation_name: str) -> None:
    from locally_twisted.product_quote_runtime import copy_quotation_line_configuration_to_sales_order

    quotation = frappe.get_doc("Quotation", quotation_name)
    if not quotation.items:
        raise ContractFail("product quote draft Quotation has no items to copy into Sales Order")

    sales_order = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "customer": _create_customer().name,
            "order_type": "Sales",
            "transaction_date": nowdate(),
            "delivery_date": add_days(nowdate(), 7),
            "items": [
                {
                    "item_code": quotation.items[0].item_code,
                    "qty": 1,
                    "rate": 0,
                }
            ],
        }
    )
    copy_quotation_line_configuration_to_sales_order(sales_order, quotation_name)

    copied = sales_order.items[0]
    for fieldname in LINE_FIELDNAMES.values():
        if not copied.get(fieldname):
            raise ContractFail(f"Sales Order Item did not receive quote-first configuration field {fieldname}")
    payload = json.loads(copied.get(LINE_FIELDNAMES["json"]))
    if payload.get("source") != "lt_product_page_quote_runtime":
        raise ContractFail(f"Sales Order Item copied wrong product quote payload: {payload}")


def _assert_product_quote_packet_surfaces_payload(quotation_name: str) -> None:
    from locally_twisted.paperwork import quote_proposal_draft_packet

    result = quote_proposal_draft_packet.run(limit=20)
    if not result.get("ok"):
        raise ContractFail(f"quote/proposal draft packet did not render cleanly: {result.get('failures')}")
    packet = None
    for candidate in result.get("packets") or []:
        if candidate.get("source_name") == quotation_name:
            packet = candidate
            break
    if not packet:
        raise ContractFail("product quote draft Quotation was not visible in the quote/proposal packet review")
    for section in packet.get("sections") or []:
        key_fields = section.get("key_fields_to_review") or {}
        if not key_fields.get("product_quote_summary"):
            raise ContractFail("quote/proposal packet did not surface the product quote summary")
        if not key_fields.get("product_quote_payload"):
            raise ContractFail("quote/proposal packet did not surface the product quote payload")
        if "lt_product_page_quote_runtime" not in str(key_fields.get("product_quote_payload")):
            raise ContractFail("quote/proposal packet product payload did not preserve runtime source")


def _configuration_payload(
    item_code: str,
    variant_options: list[dict] | None = None,
    *,
    add_ons: list[dict] | None = None,
) -> dict:
    return {
        "schema_version": CONFIG_VERSION,
        "item_code": item_code,
        "website_item_code": "unicorn-bouquet",
        "selected_options": _variant_options_dict(variant_options or []),
        "add_ons": add_ons or [],
        "customizations": [],
    }


def _variant_options_dict(rows: list[dict]) -> dict[str, str]:
    return {
        str(row.get("attribute")): str(row.get("attribute_value"))
        for row in rows
        if row.get("attribute") and row.get("attribute_value")
    }


def _create_customer():
    token = str(int(time.time()))
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"LT Product Runtime Contract {token}",
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "All Territories",
        }
    )
    customer.insert(ignore_permissions=True)
    return customer
