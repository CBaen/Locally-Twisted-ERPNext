import frappe
import webshop.webshop.product_data_engine.query as product_query

from locally_twisted.overrides.website_item import get_guest_safe_product_info_for_website
from locally_twisted.product_options import apply_variant_starting_price
from webshop.webshop.api import get_product_filter_data as webshop_get_product_filter_data

product_query.get_product_info_for_website = get_guest_safe_product_info_for_website


@frappe.whitelist(allow_guest=True)
def get_product_filter_data(query_args=None):
    result = webshop_get_product_filter_data(query_args=query_args)
    items = (result or {}).get("items") or []
    names = [item.get("name") for item in items if item.get("name")]

    if not names:
        return result

    brand_rows = frappe.get_all(
        "Website Item",
        filters={"name": ["in", names]},
        fields=["name", "lt_brand_description"],
        limit_page_length=0,
    )
    brand_by_name = {row.name: row.lt_brand_description for row in brand_rows}

    for item in items:
        apply_variant_starting_price(item)
        item["lt_brand_description"] = brand_by_name.get(item.get("name")) or ""

    return result
