from __future__ import annotations

import frappe
from erpnext.accounts.party import get_default_price_list
from erpnext.utilities.product import get_price
from webshop.webshop.doctype.website_item.website_item import WebsiteItem
from webshop.webshop.doctype.webshop_settings.webshop_settings import (
    get_shopping_cart_settings,
    show_quantity_in_website,
)
from webshop.webshop.shopping_cart.cart import get_party
from webshop.webshop.utils.product import get_non_stock_item_status, get_web_item_qty_in_stock


class LocallyTwistedWebsiteItem(WebsiteItem):
    def set_shopping_cart_data(self, context):
        context.shopping_cart = get_guest_safe_product_info_for_website(self.item_code)


def get_guest_safe_product_info_for_website(
    item_code: str,
    skip_quotation_creation: bool = True,
) -> frappe._dict:
    cart_settings = get_shopping_cart_settings()
    if not cart_settings.enabled:
        return frappe._dict({"product_info": {}, "cart_settings": cart_settings})

    party = None if frappe.session.user == "Guest" else get_party()
    selling_price_list = safe_set_price_list(cart_settings)

    price = {}
    if cart_settings.show_price:
        is_guest = frappe.session.user == "Guest"
        if not is_guest or not cart_settings.hide_price_for_guest:
            price = get_price(
                item_code,
                selling_price_list,
                cart_settings.default_customer_group,
                cart_settings.company,
                party=party,
            )

    product_info = {
        "price": price,
        "qty": 0,
        "uom": frappe.db.get_value("Item", item_code, "stock_uom"),
        "sales_uom": frappe.db.get_value("Item", item_code, "sales_uom"),
    }
    product_info.update(_stock_status(item_code))

    return frappe._dict({"product_info": product_info, "cart_settings": cart_settings})


def _selling_price_list(cart_settings, party) -> str | None:
    if party and frappe.db.exists("Customer", party.name):
        selling_price_list = get_default_price_list(party)
        if selling_price_list:
            return selling_price_list
    return cart_settings.price_list


def safe_set_price_list(cart_settings, quotation=None) -> str | None:
    if quotation:
        party_name = quotation.get("party_name")
        party = frappe.get_doc("Customer", party_name) if party_name and frappe.db.exists("Customer", party_name) else None
    else:
        party = None if frappe.session.user == "Guest" else get_party()

    selling_price_list = _selling_price_list(cart_settings, party)
    if quotation:
        quotation.selling_price_list = selling_price_list
    return selling_price_list


def _stock_status(item_code: str) -> dict:
    if not get_shopping_cart_settings().show_stock_availability:
        return {}

    if frappe.get_cached_value("Website Item", {"item_code": item_code}, "on_backorder"):
        return {"on_backorder": True}

    status = get_web_item_qty_in_stock(item_code, "website_warehouse")
    if not status:
        return {}

    return {
        "stock_qty": status.stock_qty,
        "in_stock": (
            status.in_stock
            if status.is_stock_item
            else get_non_stock_item_status(item_code, "website_warehouse")
        ),
        "show_stock_qty": show_quantity_in_website(),
    }
