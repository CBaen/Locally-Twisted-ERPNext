"""Rename the misspelled Reflex Champagne color value in ERPNext records."""
from __future__ import annotations

import frappe


OLD_VALUE = "Reflex Champage"
NEW_VALUE = "Reflex Champagne"


def execute():
    frappe.db.sql(
        """
        UPDATE `tabItem Attribute Value`
           SET attribute_value = %s
         WHERE parent = %s
           AND attribute_value = %s
        """,
        (NEW_VALUE, "latex colors", OLD_VALUE),
    )
    frappe.db.sql(
        """
        UPDATE `tabItem Variant Attribute`
           SET attribute_value = %s
         WHERE attribute = %s
           AND attribute_value = %s
        """,
        (NEW_VALUE, "latex colors", OLD_VALUE),
    )
