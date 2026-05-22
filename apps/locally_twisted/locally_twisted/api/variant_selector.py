from __future__ import annotations

import frappe
import webshop.webshop.variant_selector.utils as variant_utils

from locally_twisted.overrides.website_item import safe_set_price_list


@frappe.whitelist(allow_guest=True, methods=["POST"])
def get_next_attribute_and_values(item_code, selected_attributes):
    variant_utils._set_price_list = safe_set_price_list
    return variant_utils.get_next_attribute_and_values(item_code, selected_attributes)
