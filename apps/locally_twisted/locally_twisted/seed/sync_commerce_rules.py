"""Sync ERPNext records needed by LT commerce rules.

Run:
  bench --site frontend execute locally_twisted.seed.sync_commerce_rules.execute
"""
from __future__ import annotations

import json

import frappe

from locally_twisted.commerce_rules import (
    DELIVERY_PARK_CITY_ITEM,
    DELIVERY_STANDARD_ITEM,
    NON_TAXABLE_ITEM_TAX_TEMPLATE,
    PRICE_LIST,
    TAX_ACCOUNT_HEAD,
)


SO_FIELDS = [
    {
        "fieldname": "custom_lt_fulfillment_section",
        "label": "Locally Twisted Fulfillment",
        "fieldtype": "Section Break",
        "insert_after": "shipping_address_name",
    },
    {
        "fieldname": "custom_lt_fulfillment_method",
        "label": "Fulfillment Method",
        "fieldtype": "Select",
        "options": "\nPickup\nDelivery\nDelivery Quote",
        "insert_after": "custom_lt_fulfillment_section",
    },
    {
        "fieldname": "custom_lt_delivery_zone",
        "label": "Delivery Zone",
        "fieldtype": "Data",
        "insert_after": "custom_lt_fulfillment_method",
    },
    {
        "fieldname": "custom_lt_pickup_location",
        "label": "Pickup Location",
        "fieldtype": "Select",
        "options": "\nWest Jordan\nRiverdale",
        "insert_after": "custom_lt_delivery_zone",
    },
    {
        "fieldname": "custom_lt_requested_fulfillment_date",
        "label": "Requested Fulfillment Date",
        "fieldtype": "Date",
        "insert_after": "custom_lt_pickup_location",
    },
    {
        "fieldname": "custom_lt_requested_window_start",
        "label": "Requested Window Start",
        "fieldtype": "Data",
        "insert_after": "custom_lt_requested_fulfillment_date",
        "description": "Requested time only. Locally Twisted confirms manually.",
    },
    {
        "fieldname": "custom_lt_requested_window_end",
        "label": "Requested Window End",
        "fieldtype": "Data",
        "insert_after": "custom_lt_requested_window_start",
        "description": "Requested time only. Locally Twisted confirms manually.",
    },
    {
        "fieldname": "custom_lt_fulfillment_status",
        "label": "Fulfillment Status",
        "fieldtype": "Data",
        "insert_after": "custom_lt_requested_window_end",
    },
]

DELIVERY_ITEMS = {
    DELIVERY_STANDARD_ITEM: {
        "item_name": "Standard Delivery",
        "description": "Standard local delivery fee for ready-to-order checkout.",
        "rate": 15.0,
    },
    DELIVERY_PARK_CITY_ITEM: {
        "item_name": "Park City Delivery",
        "description": "Park City delivery fee for ready-to-order checkout.",
        "rate": 50.0,
    },
}

PAYMENT_TERMS = {
    "LT Due Now": {
        "credit_days": 0,
        "description": "Full payment due at order.",
    },
    "LT Corporate Net 30": {
        "credit_days": 30,
        "description": "Corporate client invoice due 30 days after invoice date.",
    },
}


def execute(commit: bool = True) -> str:
    summary = {
        "custom_fields": [],
        "items": [],
        "item_prices": [],
        "item_tax_templates": [],
        "payment_terms": [],
        "payment_terms_templates": [],
    }
    _ensure_sales_order_fields(summary)
    _ensure_item_tax_templates(summary)
    _ensure_delivery_items(summary)
    _ensure_payment_terms(summary)
    frappe.clear_cache(doctype="Sales Order")
    if commit:
        frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_sales_order_fields(summary: dict) -> None:
    for spec in SO_FIELDS:
        name = f"Sales Order-{spec['fieldname']}"
        if frappe.db.exists("Custom Field", name):
            doc = frappe.get_doc("Custom Field", name)
            changed = False
            for key in ("label", "fieldtype", "options", "insert_after", "description"):
                if key in spec and getattr(doc, key) != spec[key]:
                    setattr(doc, key, spec[key])
                    changed = True
            if changed:
                doc.save(ignore_permissions=True)
                summary["custom_fields"].append(f"updated:{spec['fieldname']}")
            continue
        field = {"doctype": "Custom Field", "dt": "Sales Order", **spec}
        frappe.get_doc(field).insert(ignore_permissions=True)
        summary["custom_fields"].append(f"created:{spec['fieldname']}")


def _company_name() -> str | None:
    return frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")


def _ensure_item_tax_templates(summary: dict) -> None:
    company = _company_name()
    if not company:
        return
    existing_name = (
        frappe.db.exists(
            "Item Tax Template",
            {"title": NON_TAXABLE_ITEM_TAX_TEMPLATE, "company": company},
        )
        or frappe.db.exists("Item Tax Template", NON_TAXABLE_ITEM_TAX_TEMPLATE)
    )
    if existing_name:
        template = frappe.get_doc("Item Tax Template", existing_name)
        changed = False
        if template.title != NON_TAXABLE_ITEM_TAX_TEMPLATE:
            template.title = NON_TAXABLE_ITEM_TAX_TEMPLATE
            changed = True
        if template.company != company:
            template.company = company
            changed = True
        desired_taxes = [{"tax_type": TAX_ACCOUNT_HEAD, "tax_rate": 0}]
        current_taxes = [
            {"tax_type": row.tax_type, "tax_rate": float(row.tax_rate or 0)}
            for row in template.taxes
        ]
        if current_taxes != desired_taxes:
            template.set("taxes", desired_taxes)
            changed = True
        if changed:
            template.save(ignore_permissions=True)
            summary["item_tax_templates"].append(f"updated:{NON_TAXABLE_ITEM_TAX_TEMPLATE}")
        return

    template = frappe.get_doc(
        {
            "doctype": "Item Tax Template",
            "name": NON_TAXABLE_ITEM_TAX_TEMPLATE,
            "title": NON_TAXABLE_ITEM_TAX_TEMPLATE,
            "company": company,
            "taxes": [{"tax_type": TAX_ACCOUNT_HEAD, "tax_rate": 0}],
        }
    )
    template.insert(ignore_permissions=True)
    summary["item_tax_templates"].append(f"created:{NON_TAXABLE_ITEM_TAX_TEMPLATE}")


def _ensure_delivery_items(summary: dict) -> None:
    company = _company_name()
    income_account = frappe.db.get_value("Company", company, "default_income_account")
    for item_code, spec in DELIVERY_ITEMS.items():
        if frappe.db.exists("Item", item_code):
            item = frappe.get_doc("Item", item_code)
            changed = False
            for key, value in {
                "item_name": spec["item_name"],
                "item_group": "Services",
                "stock_uom": "Nos",
                "is_stock_item": 0,
                "disabled": 0,
                "description": spec["description"],
            }.items():
                if getattr(item, key) != value:
                    setattr(item, key, value)
                    changed = True
            if changed:
                item.save(ignore_permissions=True)
                summary["items"].append(f"updated:{item_code}")
        else:
            doc = {
                "doctype": "Item",
                "item_code": item_code,
                "item_name": spec["item_name"],
                "item_group": "Services",
                "stock_uom": "Nos",
                "is_stock_item": 0,
                "include_item_in_manufacturing": 0,
                "disabled": 0,
                "description": spec["description"],
            }
            if company and income_account:
                doc["item_defaults"] = [{"company": company, "income_account": income_account}]
            frappe.get_doc(doc).insert(ignore_permissions=True)
            summary["items"].append(f"created:{item_code}")

        price_name = frappe.db.get_value(
            "Item Price",
            {"item_code": item_code, "price_list": PRICE_LIST, "selling": 1},
            "name",
        )
        if price_name:
            price = frappe.get_doc("Item Price", price_name)
            if float(price.price_list_rate or 0) != float(spec["rate"]):
                price.price_list_rate = spec["rate"]
                price.save(ignore_permissions=True)
                summary["item_prices"].append(f"updated:{item_code}")
            continue
        frappe.get_doc(
            {
                "doctype": "Item Price",
                "item_code": item_code,
                "price_list": PRICE_LIST,
                "price_list_rate": spec["rate"],
                "selling": 1,
                "currency": "USD",
            }
        ).insert(ignore_permissions=True)
        summary["item_prices"].append(f"created:{item_code}")


def _ensure_payment_terms(summary: dict) -> None:
    for term_name, spec in PAYMENT_TERMS.items():
        if not frappe.db.exists("Payment Term", term_name):
            doc = frappe.get_doc(
                {
                    "doctype": "Payment Term",
                    "payment_term_name": term_name,
                    "due_date_based_on": "Day(s) after invoice date",
                    "credit_days": spec["credit_days"],
                    "description": spec["description"],
                }
            )
            doc.name = term_name
            doc.insert(ignore_permissions=True)
            summary["payment_terms"].append(f"created:{term_name}")

        if frappe.db.exists("Payment Terms Template", term_name):
            continue
        template = frappe.get_doc(
            {
                "doctype": "Payment Terms Template",
                "template_name": term_name,
                "terms": [
                    {
                        "payment_term": term_name,
                        "invoice_portion": 100,
                        "due_date_based_on": "Day(s) after invoice date",
                        "credit_days": spec["credit_days"],
                        "description": spec["description"],
                    }
                ],
            }
        )
        template.insert(ignore_permissions=True)
        summary["payment_terms_templates"].append(f"created:{term_name}")
