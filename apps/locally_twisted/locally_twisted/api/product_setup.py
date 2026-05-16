"""Whitelisted Product Setup runtime API for customer-facing ecommerce flows."""
from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _

from locally_twisted.product_setup_runtime import (
    product_setup_schema_for_website_item,
    resolve_product_setup_configuration,
)


@frappe.whitelist(allow_guest=True)
def get_product_setup_schema(item_code: str) -> dict[str, Any]:
    """Return the backend-owned Product Setup schema for a product page."""
    schema = product_setup_schema_for_website_item(item_code)
    if not schema:
        frappe.throw(
            _("Tiny snag: this product setup is not ready yet. Please ask the team for help."),
            frappe.ValidationError,
        )
    return schema


@frappe.whitelist(allow_guest=True)
def resolve_product_setup(item_code: str, configuration: Any = None) -> dict[str, Any]:
    """Validate a browser configuration against Product Setup before commerce."""
    schema = product_setup_schema_for_website_item(item_code)
    if not schema:
        frappe.throw(
            _("Tiny snag: this product setup is not ready yet. Please ask the team for help."),
            frappe.ValidationError,
        )
    return resolve_product_setup_configuration(schema, _configuration_dict(configuration))


def _configuration_dict(configuration: Any) -> dict[str, Any]:
    if configuration in (None, ""):
        return {}
    if isinstance(configuration, str):
        try:
            configuration = json.loads(configuration)
        except (TypeError, ValueError):
            frappe.throw(
                _("Tiny snag: this product option data did not come through cleanly. Please choose the options again."),
                frappe.ValidationError,
            )
    if not isinstance(configuration, dict):
        frappe.throw(
            _("Tiny snag: this product option data did not come through cleanly. Please choose the options again."),
            frappe.ValidationError,
        )
    return configuration
